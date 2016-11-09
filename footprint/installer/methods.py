# coding=utf8

# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.


"""
This is a collection of methods to facilitate the setup and deployment of UrbanFootprint instances.
Each function that is decorated with an `@task` can be called with `fab [host] [function]`.
Hosts are configured in the `hosts` subdirectory.

High-level methods:
 an installation method for the UF stack: `setup_urbanfootprint()`
 code deployment methods: `deploy()`
 data deployment methods: `publish_datadump()` and `deploy_data()`
 data building: `build()`, formerly `recreate_dev()`

Settings helper methods:
 local settings management: `local_settings()`

"""

#
# Need to append the sys path to make the fabric django contrib module work. Sadly these things must
# be done in this order to have the django_settings object available
import datetime
import fabtools
import importlib
import json
import logging
import multiprocessing
import os

from django.core.management import call_command
# from fabric.contrib import django
from fabric.contrib.project import rsync_project

from fabtools.postgres import _run_as_pg as run_as_pg
from fabric.contrib import console
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from fabric.api import env, sudo, cd, task, prompt, local, settings, run, hide
from dotenv import read_dotenv
import requests

from footprint.utils.postgres_utils import build_postgres_conn_string, postgres_env_password_loaded

logger = logging.getLogger(__name__)

read_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


def psql(command, user=None, host=None, database_name=None, port=None, password=None):

    if not user:
        user = os.environ.get('DATABASE_USERNAME')

    if not password:
        password = os.environ.get('DATABASE_PASSWORD')

    if not host:
        host = os.environ.get('DATABASE_HOST')

    if not database_name:
        database_name = os.environ.get('DATABASE_NAME')

    if not port:
        port = os.environ.get('DATABASE_PORT')

    full_command = """PGPASSWORD={password} psql -U {user} -h {host} -p {port} -d {database_name} -c "{command}" """.format(
        password=password,
        user=user,
        host=host,
        port=port,
        database_name=database_name,
        command=command
    )

    return run(full_command)


def get_django_setting(build_type, setting_name):
    """Import a setting from the relevant django settings module.

    Note: this is a hack. Nothing in this file should depend on django
    settings. Instead they should be configured in some other
    configuration system.
    """
    settings_module = importlib.import_module('footprint.settings_%s' % build_type)
    return getattr(settings_module, setting_name)


def virtualenv(command):
    activate = os.path.join(env.virtualenv_directory, 'bin', 'activate')
    virtualenv_command = ' '.join(['source', activate, '&&', command])
    return run_as_user(env.deploy_user, virtualenv_command)


def manage_py(command, build_type):
    python_interpreter = get_django_setting(build_type, 'PYTHON_INTERPRETER')
    manage_command = ' '.join([
        python_interpreter,
        os.path.join(get_django_setting(build_type, 'ROOT_PATH'), 'manage.py'),
        command,
        '--traceback',
        '--settings=footprint.settings_%s' % build_type])
    sudo(manage_command, user=env.deploy_user)


def run_as_user(user, command):
    return sudo('su %s -c "%s"' % (user, command))


# TODO: Unify this with the rest of the supervisor reload/restarts in this file.
@task
def restart_supervisor():
    sudo('supervisorctl restart all')

@task
def restart_dev():
    npm_install()
    switch_to_dev()
    sudo('supervisorctl status')

@task
def quickstart():
    npm_install()
    pip_install('prod')
    switch_to_prod()
    manage_py('footprint_init --skip --reresult --tilestache', 'init')
    generate_cartocss()
    deploy('prod', True)

@task
def npm_install():
    with cd("/srv/calthorpe/urbanfootprint/websockets"):
        # Symlink issues with Windows+Virtualbox so we add '--no-bin-link'
        # Similar to: https://github.com/npm/npm/issues/7094
        run("/usr/bin/npm install --no-bin-links .")

@task
def client():
    client = os.environ.get('CLIENT')
    client_path = "footprint/client/configuration/{client}".format(client=client)
    sproutcore_path = "sproutcore/frameworks/footprint/resources/images"
    with cd('/srv/calthorpe/urbanfootprint'):
        run('if [ -e {client_path}/login_page_logo.png ]; then cp -f {client_path}/login_page_logo.png {sproutcore_path}/client_login_page_logo.png; fi'.format(client_path=client_path, sproutcore_path=sproutcore_path))
        run('if [ -e {client_path}/login_page_logo_lower.png ]; then cp -f {client_path}/login_page_logo.png {sproutcore_path}/client_login_page_logo_lower.png; fi'.format(client_path=client_path, sproutcore_path=sproutcore_path))

@task
def setup_tilestache_user():
    """
    create the tilestache postgres user and grant it limited, read only access to the database tables it needs
    this allows us to use "trust" identification without worrying about compromising security
    :return:
    """
    fabtools.icanhaz.postgres.user("tilestache", "tilestache", superuser=False, createdb=False,
                                   createrole=False, login=True)

    setup = """
    grant connect on database urbanfootprint to tilestache;
    grant select on tilestache_layer to tilestache;
    grant select on tilestache_config to tilestache;
    """

    psql(setup)


@task
def setup_databases():
    """
        Create production postgres database using local_settings for the DB
    """

    logger.info("confirming Postgres knows about username:{user} password:{pwd}".format(
        user=env.deploy_user,
        pwd=env.password))
    fabtools.icanhaz.postgres.user(
        env.deploy_user,
        env.password,
        superuser=True,
        createdb=True,
        createrole=True,
        login=True)

    run_as_pg("""psql -U postgres -h {host} -c "ALTER USER {user} password '{pwd}';" """.format(
        user=env.deploy_user,
        pwd=env.password,
        host=os.environ['DATABASE_HOST']
    ))

    run_as_pg("""psql -U postgres -h {host} -c "ALTER USER {user} SUPERUSER;" """.format(
        user=env.deploy_user,
        host=os.environ['DATABASE_HOST']
    ))

    database_name = os.environ['DATABASE_NAME']
    fabtools.icanhaz.postgres.database(database_name, env.deploy_user)
    # the following two lines below should be enabled for postgis 2.0 (also remove template_postgis from above lines)
    psql("CREATE EXTENSION IF NOT EXISTS POSTGIS")
    psql("CREATE EXTENSION IF NOT EXISTS DBLINK")

    psql("ALTER DATABASE {database_name} SET search_path = '$user',public,postgis;".format(database_name=database_name))


@task
def publish_datadump(build_type='prod'):
    """
    Generates a local datadump and publishes it to the requested servers
    This is done with the env.user, not env.deploy_user, so that it's easy
    to access files via ssh
    """

    # Make sure remote folders exist
    sudo('mkdir -p {0}'.format(env.DATA_DUMP_PATH))
    sudo('chown -R {0}.www-data {1}'.format(env.user, env.DATA_DUMP_PATH))

    create_new_dump = console.confirm("Create new database dumpfile?", default=False)
    logger.info("Creating datadump on {host}".format(host=env.host))
    if create_new_dump:
        manage_py('create_datadump', build_type)
    logger.info("Finished datadump on {host}".format(host=env.host))

    logger.info('Copying media to %s' % env.DATA_DUMP_PATH)
    media_root = get_django_setting(build_type, 'MEDIA_ROOT')
    rsync_project(env.DATA_DUMP_PATH, os.path.join(media_root, 'media'), default_opts='-pthrvzO')
    logger.info('Copied media to %s' % env.DATA_DUMP_PATH)

    dump_location = get_django_setting(build_type, 'CALTHORPE_DATA_DUMP_LOCATION')
    local_dump_file = os.path.join(dump_location, 'pg_dump.dmp')

    logger.info("Copying dump to {host}".format(host=env.host))
    rsync_project(env.DATA_DUMP_PATH + '/pg_dump.dmp', local_dir=local_dump_file, default_opts='-pthrvzO')

@task
def fetch_datadump(force_local_db_destroy=True, use_local=True, build_type='prod'):
    """
    Sync local database and media folder with official data_dump
    'fetch_datadump:force_local_db_destroy:True' to not prompt for db destruction confirmation
    'fetch_datadump:use_local:True avoid going through the ssh wire
    """

    database_name = os.environ['DATABASE_NAME']

    if not force_local_db_destroy:
        msg = 'You are DESTROYING the local "{dbname}" database! Continue?'.format(
            dbname=database_name)

        accepted_database_destroy = console.confirm(msg, default=False)

        if not accepted_database_destroy:
            print 'Aborting fetch_datadump()'
            return

    if not use_local:
        media_root = get_django_setting(build_type, 'MEDIA_ROOT')
        rsync_project(os.path.join(media_root, '/media'),
                      local_dir=media_root, default_opts='-pthrvzO')

    # rsync postgres datadump file into local folder
    # The reason we don't use tempfile.gettempdir() is that we always want the file to exist
    # in the same place so we can take advantage of rsync's delta file-chunk speedup. In OSX,
    # after every reboot, gettempdir returns a different directory defeating the point of using
    # rsync. We use the '/tmp/' folder instead

    temp_dir = get_django_setting(build_type, 'TEMP_DIR')
    local_dump_file = os.path.join(temp_dir, 'pg_dump.dmp')
    if not use_local:
        dump_path = get_django_setting(build_type, 'DATA_DUMP_PATH')
        rsync_project(os.path.join(dump_path, '/pg_dump.dmp', local_dir=local_dump_file))

    with postgres_env_password_loaded():
        db_conn_string = build_postgres_conn_string()

        # Some versions of postgres do not have --if-exists, so just ignore the error if it doesn't exist
        with settings(warn_only=True):
            local('dropdb {db_conn_string}'.format(db_conn_string=db_conn_string))

        local('createdb -O {db_user} {db_conn_string}'.format(
            db_user=os.environ['DATABASE_USERNAME'], db_conn_string=db_conn_string))

        local('''psql -h {1} -p {2} -c 'ALTER DATABASE {0} SET search_path = "$user",public,postgis;' {0}'''.format(
            os.environ['DATABASE_NAME'],
            os.environ['DATABASE_HOST'],
            os.environ['DATABASE_PORT']
        ))

        with settings(warn_only=True):
            result = local('pg_restore {db_conn_string} -d {dbname} {local_dump_file}'.format(
                db_conn_string=build_postgres_conn_string(omit_db=True),
                dbname=os.environ['DATABASE_NAME'],
                local_dump_file=local_dump_file))
        if result.failed:
            print "ERROR: You probably don't have 'calthorpe' ROLE defined. Fix by executing:"
            print "CREATE ROLE calthorpe; GRANT calthorpe to {user};".format(
                user=os.environ['DATABASE_USERNAME'])
            raise SystemExit()


@task
def deploy_data(build_type='prod'):
    """
    Logs into remote machine and loads the data_load that has been published to the same machine
    The dump file is expected at /srv/datadump/pg_dump.dmp
    """

    # stop any connections to the db
    with settings(warn_only=True):
        sudo('supervisorctl stop all')
        sudo('/etc/init.d/supervisor stop')

    # with cd(get_django_setting(build_type, 'ROOT_PATH')):
    #
    #
    #     fab_cmd = env.virtualenv_directory + '/bin/fab'
    #     sudo('{fab_cmd} localhost fetch_datadump:use_local=True,force_local_db_destroy=True'.format(
    #         fab_cmd=fab_cmd), user=env.deploy_user)

    with postgres_env_password_loaded():
        db_conn_string = build_postgres_conn_string()
        database_name = os.environ['DATABASE_NAME']

        # Some versions of postgres do not have --if-exists, so just ignore the error if it doesn't exist
        with settings(warn_only=True):
            drop_db_connections(database_name)
            run('dropdb {db_conn_string}'.format(db_conn_string=db_conn_string))

        run_as_pg('createdb -O {db_user} {db_conn_string}'.format(
            db_user=os.environ['DATABASE_USERNAME'], db_conn_string=db_conn_string))

        psql("ALTER DATABASE {database_name} SET search_path = '$user',public,postgis;".format(database_name=database_name))

        with settings(warn_only=True):
            result = run('pg_restore {db_conn_string} -d {dbname} {local_dump_file}'.format(
                db_conn_string=build_postgres_conn_string(omit_db=True),
                dbname=database_name,
                local_dump_file='/srv/datadump/pg_dump.dmp'))
        if result.failed:
            print "ERROR: You probably don't have 'calthorpe' ROLE defined. Fix by executing:"
            print "CREATE ROLE calthorpe; GRANT calthorpe to {user};".format(user=os.environ['DATABASE_USERNAME'])
            raise SystemExit()

    if os.path.exists('/srv/calthorpe_media'):
        sudo('rm -r /srv/calthorpe_media')
    sudo('cp -R /srv/datadump/media/calthorpe_media /srv/')
    directory_permissions(build_type=build_type)

    # start connections to the db
    sudo('/etc/init.d/supervisor start')
    sudo('supervisorctl start all')

@task
def directory_permissions(build_type='prod'):
    media_root = get_django_setting(build_type, 'MEDIA_ROOT')
    sudo('chown {user}:www-data {media} -R'.format(user=env.deploy_user,
                                                   media=media_root))
    sudo('chmod 777 {media} -R'.format(media=media_root))


def drop_db_connections(database_name):
    """
    looks up the db in local settings by its alias and drops any connections
    """

    drop_connections = """
        SELECT
            pg_terminate_backend(pid)
        FROM
            pg_stat_activity
        WHERE
            datname = '{db}'
        AND pid <> pg_backend_pid()
    """.format(db=database_name)

    psql(drop_connections)


def drop_databases():
    """
        Drop the databases. This is not part of the normal setup process, rather it's used to recreate the database in development.
    :return:
    """

    db_name = os.environ['DATABASE_NAME']
    for database_name in ['test_{0}'.format(db_name), db_name]:
        with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            exists = psql("", database_name=database_name).succeeded
            # Drop the database if it exists
        if exists:
            drop_db_connections(database_name)
            run_as_pg("dropdb {db};".format(db=database_name))


@task
def switch_to_dev():
    switch_to_prod(reverse=True)


@task
def switch_to_prod(reverse=False):
    # This should be done in ansible, once there is a specific 'dev'
    # role. Then, we need to override
    # `DjangoTestSuiteRunner.setup_databases`.

    # For more information:
    # http://stackoverflow.com/questions/5917587/django-unit-tests-without-a-db
    # https://docs.djangoproject.com/en/1.5/topics/testing/advanced/#django.test.simple.DjangoTestSuiteRunner.setup_databases
    if reverse:
        # Production needs superuser privileges to run tests
        build_type = 'dev'
        superuser = 'superuser'
    else:
        build_type = 'prod'
        superuser = 'nosuperuser'

    try:
        sudo('rm -f /etc/supervisor/conf.d/calthorpe.conf')
        sudo('rm -f /etc/nginx/sites-available/calthorpe.nginx')

    except Exception as e:
        logger.warning('Failed to remove configuration files: %s', e)

    run_as_pg(
        """psql -h {host} -c "ALTER ROLE {user} {superuser}";""".format(
            user=env.deploy_user,
            superuser=superuser,
            host=os.environ['DATABASE_HOST']
        )
    )

    root_path = get_django_setting(build_type, 'ROOT_PATH')
    sudo('ln -sf {ROOT_PATH}/conf/etc/nginx/sites-available/calthorpe.nginx.{build_type} '
         '/etc/nginx/sites-enabled/calthorpe.nginx '.format(ROOT_PATH=root_path,
                                                            build_type=build_type))
    sudo('ln -sf {ROOT_PATH}/conf/etc/supervisor/conf.d/calthorpe.supervisor.{build_type} '
         ' /etc/supervisor/conf.d/calthorpe.conf'.format(ROOT_PATH=root_path,
                                                         build_type=build_type))
    try:
        sudo('supervisorctl stop all')
        sudo('sleep 15')
        # Double down on making sure we don't end up with duplicate python processes
        sudo('pkill -f -9 /srv/calthorpe/urbanfootprint/manage.py || true')
    except Exception as e:
        logger.warning('error: %s', e)

    sudo('service supervisor restart')
    sudo('service nginx restart')

@task
def restart_celery():
    sudo('supervisorctl restart celery_worker')
    sudo('supervisorctl restart celerybeat')


@task
def update_published_data():
    manage_py('footprint_init --skip --results --tilestache', 'init')


@task
def dump_db(db, schema=False, exclude_schema=False, exclude_table=False, table=False, compress=True, output_dir="/tmp"):
    dump_command = 'pg_dump -U postgres'

    if compress:
        dump_command += " -Fc"

    dump_command += " {db} ".format(db=db)
    output_file = db

    if schema:
        dump_command += " -n {schema} ".format(schema=schema)
        output_file += "_" + schema
    if table:
        dump_command += " -t {table} ".format(table=table)
        output_file += "_" + table
    if exclude_schema:
        dump_command += " -N {schema} ".format(schema=schema)
        output_file += "_NO" + schema
    if exclude_table:
        dump_command += " -T {table} ".format(table=table)
        output_file += "_NO" + table

    output_file += ".dump" if compress else ".sql"
    output = os.path.join(output_dir, output_file)

    dump_command += " -f {output}".format(output)
    run_as_pg(dump_command)

    return output


@task
def build(build_type='prod'):
    """
        Drops and recreates the databases for development, then initializes main
        This will raise an error if 127.0.0.1 is not in env.hosts to protect live databases
        Make sure complete migration scripts exist prior to running this
    :return:
    """
    restart_supervisor()
    prepare_build_or_deploy(build_type=build_type)
    start = datetime.datetime.now()
    recreate_db(build_type)
    with cd(get_django_setting(build_type, 'ROOT_PATH')):
        manage_py('syncdb --noinput', build_type)
        manage_py('migrate', build_type)
        manage_py('collectstatic --noinput', build_type)
        setup_tilestache_user()
    build_database(build_type=build_type)
    post_build_database()
    end = datetime.datetime.now()
    elapsed = end - start
    print elapsed
    npm_install()

@task
def recreate_db(build_type='prod'):
    """
        Drops and recreates the databases
    :param build_type:
    :return:
    """
    is_remote = '127.0.0.1' not in env.hosts and 'localhost' not in env.hosts

    if build_type == 'dev':
        # this is a super-hack to make sure we use a build file with CELERY_ALWAYS_EAGER=False
        # TODO: unify this with 'dev' and/or provide a way to override this celery setting.
        build_type = 'devbuild'
    if is_remote and not getattr(env, 'allow_remote_recreate', False):
        raise Exception("build is not allowed for non-localhosts for security purposes")
    if not getattr(env, 'allow_remote_recreate', False):
        if not confirm("This command destroys the database and regenerates it -- proceed?", default=False):
            return
        if not get_django_setting(build_type, 'USE_SAMPLE_DATA_SETS'):
            if not confirm("THIS IS A PRODUCTION DATA SET! REALLY DELETE IT?", default=False):
                return

    logger.info("dropping databases...")
    drop_databases()

    logger.info("creating database...")
    setup_databases()


@task
def build_database(build_type='dev', **kwargs):
    """
    Calls footprint_init to load fixture datasets from into the app.

    :param kwargs: all the options for footprint init
    :return:
    """

    # TODO: unify dev+devbuild and prod+init and/or provide a way to
    # override this celery setting. In the mean time this is a hack to
    # make sure we use a build file with CELERY_ALWAYS_EAGER=False
    if build_type == 'dev':
        build_type = 'devbuild'
    elif build_type == 'prod':
        build_type = 'init'
    with cd(get_django_setting(build_type, 'ROOT_PATH')):
        args = ' '.join(["--{}={}".format(key, value) for key, value in kwargs.iteritems()])
        manage_py('footprint_init %s' % args, build_type)


@task
def post_build_database():
    """
        Called after footprint_init to reset caches, etc
    :return:
    """
    try:
        clear_tilestache_cache()
    except Exception as e:
        logger.warn('Problem clearing tilestache cache: %s', e)

    generate_cartocss()

    if env.dev:
        switch_to_dev()
    else:
        restart_supervisor()


@task
def generate_cartocss():
    cpu_count = multiprocessing.cpu_count()

    run("ls -1 /srv/calthorpe_media/cartocss/*.mml | sed -e 's/.mml//g' | xargs -P{} -I{{}} -n1 \
         -d '\n' sh -c '/usr/bin/carto {{}}.mml > {{}}.xml'".format(cpu_count))
    directory_permissions()

@task
def clear_tilestache_cache():
    with cd("/srv/calthorpe/urbanfootprint"):
        call_command("empty_tilestache_cache")

@task
def delete_all_cartocss():
    sudo("rm -r /srv/calthorpe_media/cartocss/*")
    sudo("rm -r /srv/calthorpe_static/cartocss/*")


def ec2_timestamp():
    today = datetime.date.today()
    return "{year}.{month}.{day}".format(year=today.year, month=today.month, day=today.day)


@task
def build_sproutcore(build_type='prod', minify=False):
    update_sproutcore_build_number(build_type=build_type)

    # build sproutcore
    with cd('{root}/sproutcore'.format(root=get_django_setting(build_type, 'ROOT_PATH'))):
        # Build main in the build dir
        build_command = 'sproutcore build fp --buildroot=builds'
        if not minify:
            build_command += ' --dont_minify'
        sudo(build_command, user=env.deploy_user)

        # Change ownership on output
        sudo('chown -R {0}.www-data ./builds'.format(env.deploy_user))

        # ln to the builds dir from Django's static dir
        sudo('ln -f -s {root}/sproutcore/builds/static/* {root}/footprint/main/static'.format(
            root=get_django_setting(build_type, 'ROOT_PATH')), user=env.deploy_user)

        # symlink to the sproutcore build directory "build-number"
        sudo('ln -f -s {root}/sproutcore/builds/static/fp/en/$(sproutcore build-number fp)/index.html '
             '{root}/footprint/main/templates/footprint/index.html'.format(
                 root=get_django_setting(build_type, 'ROOT_PATH'),
                 user=env.deploy_user))

    # do a collect static to grab all static files and link them to the right directory
    manage_py('collectstatic -l --noinput', build_type)


def pip_install(build_type):
    pip_cmd = 'pip install -r ' + os.path.join(get_django_setting(build_type, 'ROOT_PATH') + '/requirements.txt')
    virtualenv(pip_cmd)
    manage_py('syncdb --noinput', build_type)


def prepare_build_or_deploy(build_type):
    client()
    directory_permissions(build_type=build_type)

@task
def deploy(build_type='prod', skip_git=False):
    """
    Deploy code, pip dependencies and execute migrations
    """
    prepare_build_or_deploy(build_type=build_type)

    if not skip_git:
        with cd('/srv/calthorpe/urbanfootprint/'):
            sudo('git config --global user.name {0}'.format(env.deploy_user))
            sudo('git stash', user=env.deploy_user)
            run_as_user(env.deploy_user, 'git fetch')

            if getattr(env, 'branch', None):
                run_as_user(env.deploy_user, ('git checkout {branch}'.format(branch=env.branch)))

            # There should never be any local commits on hosts that we are deploying to.
            run_as_user(env.deploy_user, 'git pull')
            run_as_user(env.deploy_user, 'git submodule init')
            run_as_user(env.deploy_user, 'git submodule sync')
            run_as_user(env.deploy_user, 'git submodule update --remote')

    commit = get_commit(build_type=build_type)

    with cd(get_django_setting(build_type, 'ROOT_PATH')):
        pip_install(build_type)
        manage_py('migrate --delete-ghost-migrations', build_type)

    build_sproutcore(build_type=build_type)

    with settings(warn_only=True):
        sudo('supervisorctl stop all')
        sudo('/etc/init.d/supervisor stop')
        sudo('/etc/init.d/nginx stop')

    sudo('/etc/init.d/nginx start')
    sudo('/etc/init.d/supervisor start')
    sudo('supervisorctl start all')

    name = getattr(env, 'name', env.host)

@task
def update_sproutcore_build_number(build_type='prod'):
    with cd('/srv/calthorpe/urbanfootprint/'):
        manage_py('update_builddate', build_type)
    print "build number updated"

@task
def get_commit(build_type='prod'):
    with cd(get_django_setting(build_type, 'ROOT_PATH')):
        with hide('output'):
            commit = run("git rev-list HEAD --max-count=1 --pretty --oneline").stdout
    print str(commit)
    return commit
