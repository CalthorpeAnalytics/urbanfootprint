
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


import logging

import os
import psycopg2
import stat
from celery.utils.functional import uniq
from django.conf import settings
import tempfile

from django.conf import settings

from footprint.client.configuration import InitFixture, resolve_fixture
from footprint.main.database.command_execution import CommandExecution
from footprint.main.lib.functions import merge
from footprint.main.models import Region, PGNamespace
from footprint.main.models.database.information_schema import verify_srid
from footprint.main.utils.uf_toolbox import drop_table
from footprint.main.utils.utils import database_settings, chop_geom, postgres_url_to_connection_dict, file_url_to_path, os_user
from footprint.utils.postgres_utils import pg_connection_parameters
from footprint.utils.utils import drop_db

GEOMETRY_COLUMN = 'wkb_geometry'

logger = logging.getLogger(__name__)

class ImportData(object):

    _sample_database_cache = {}
    def create_target_db_string(self):
        self.target_database_connection = "-h {0} -p {1} --user {2} {3}".format(
            self.target_database.get('HOST', 'localhost'),
            self.target_database.get('PORT', 5432),
            self.target_database['USER'],
            self.target_database['NAME'])
        logger.info("Using target database connection: {0}".format(self.target_database_connection))

    def __init__(self, **arguments):

        self.arguments = arguments
        self.dump_only = self.arguments.get('dump_only', None)
        self.region_key = self.arguments.get('schema', None)
        self.target_database = database_settings('default')
        # The config_entity whose feature tables should be imported
        self.config_entity = self.arguments.get('config_entity', None)
        if self.config_entity:
            logger.info("Importing DbEntity table into ConfigEntity {0}".format(self.config_entity.subclassed))
        # The optional db_entity_key whose Feature class table should be imported. Otherwise all DbEntity tables
        # are imported for the config_entity, including inherited ones from parent ConfigEntities
        self.db_entity_key = self.arguments.get('db_entity_key', None)
        self.db_entities = filter(lambda db_entity: not self.db_entity_key or (db_entity.key == self.db_entity_key),
                                  self.config_entity.owned_db_entities())
        self.test = self.arguments.get('test', None)

        # The psql connection to the target server, normally the django server
        self.create_target_db_string()

        self.command_execution = CommandExecution(logger)

        self.target_connection_dict = dict(
            user=self.target_database['USER'],
            password=self.target_database['PASSWORD'],
            host=self.target_database.get('HOST', 'localhost'),
            port=self.target_database.get('PORT', 5432),
            database=self.target_database['NAME']
        )

        # Used to get around password authentication
        self.connections = ["{host}:*:*:{user}:{password}".format(**dict(
                    host=self.target_database['HOST'],
                    user=self.target_database['USER'],
                    password=self.target_database['PASSWORD']))]


        for db_entity in self.db_entities:
            # Create a password file in order to avoid dealing with stdin for passwords
            # This has been bypassed in favor of passing the password to stdin
            if not (db_entity.has_db_url or db_entity.has_file_url):
                raise Exception("This db_entity, {0}, has no database or file url".format(db_entity.key))
            if db_entity.has_db_url:
                # Setup the connection strings for the db_entity so that we can get around interactive password authentication
                # TODO This is never distinct per db_entity. We could just use self.target_connection_dict
                connection_dict = postgres_url_to_connection_dict(db_entity.url)
                self.connections.append("{host}:*:*:{user}:{password}".format(**connection_dict))

    def run(self):
        """
            Imports the data and syncs dependent system components, such as GeoServer to the imported data.
        """

        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.passwordfile = f.name

            for connection in uniq(self.connections):
                f.write("{0}\n".format(connection))

            # A pgpass file must have permissions of 0600 (or less permissive):
            # http://www.postgresql.org/docs/9.3/static/libpq-pgpass.html
            os.fchmod(f.fileno(), stat.S_IRUSR | stat.S_IWUSR)

        # Set the ENV variable to use this file
        os.environ['PGPASSFILE'] = self.passwordfile
        logger.info("Created password file at %s" % self.passwordfile)

        logger.info("Importing data")

        create_schema_command = "psql {0} -c 'CREATE SCHEMA IF NOT EXISTS {1}; GRANT ALL ON SCHEMA {1} TO public;'".format(
            self.target_database_connection,
            settings.IMPORT_SCHEMA
        )
        results = self.command_execution.run(create_schema_command)
        if results.returncode:
            raise Exception(results.stderr.text)

        self.import_data()

        os.remove(self.passwordfile)
        del os.environ['PGPASSFILE']

    def import_data(self, **kwargs):
        """
            Imports data from an external source to create the test data
            :return a two item tuple containing the region that was imported and a list of the imported projects
        """

        # Calculate a sample lat/lon box of the config_entity
        config_entity = self.config_entity
        if self.test:
            bounds = chop_geom(config_entity.bounds, 0.90)
            logger.info(u"Creating subselection with extents: {0}. This will be used to crop any table that doesn't have a sample version".format(bounds))

        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        for db_entity in self.db_entities:

            # This is the index on wkb_geometry.
            spatial_index_name = '{schema}_{key}_geom_idx'.format(schema=db_entity.schema, key=db_entity.key)

            table = db_entity.table

            if db_entity.has_file_url:
                # Remove any table of the same name from the import schema. This is unlikley since imported
                # tables have timestamps
                drop_table('"%s"."%s"' % (settings.IMPORT_SCHEMA, db_entity.key))
                sql_file_path = file_url_to_path(db_entity.url)
                # Create a command that pipes shp2pgsql to psql
                db_entity.srid = db_entity.srid or '4326'
                logger.info("verifying SRID {0}".format(db_entity.srid))
                verify_srid(db_entity.srid)

                # Create the import schema if needed
                PGNamespace.objects.create_schema(settings.IMPORT_SCHEMA)

                # Import the table
                import_sql_command = '/usr/bin/psql {0} -f {1}'.format(self.target_database_connection, sql_file_path)
                stdin = "{0}\n{1}".format(self.arguments.get('password', None), self.target_database.get('PASSWORD', None))
                results = self.command_execution.run(import_sql_command, stdin=stdin)
                if results.returncode:
                    raise Exception(results.stderr.text)

                # We expect a table in the public schema with a named based on db_entity.key
                # Move the table from the public schema to the db_entity schema
                move_to_schema = "alter table {0}.{1} set schema {2};".format(settings.IMPORT_SCHEMA, db_entity.key, db_entity.schema)
                logger.info("Moving import file table to schema: %s" % move_to_schema)
                cursor.execute(move_to_schema)
                # Drop the constraint that enforces the srid of the wkb_geometry if one exists
                drop_constraint = '''alter table {0}.{1} drop constraint if exists enforce_srid_wkb_geometry'''.format(db_entity.schema, db_entity.key)
                logger.info("Dropping constraint on wkb_geometry: %s" % drop_constraint)
                cursor.execute(drop_constraint)

                # Note we're not creating an index on wkb_geometry
                # here because imported files already have an index
                # created.

            elif db_entity.has_db_url:
                # The import database currently stores tables as
                # public.[config_entity.key]_[feature_class._meta.db_table (with schema removed)][_sample (for samples)]
                #
                # We always use the table name without the word sample for the target table name
                if settings.USE_SAMPLE_DATA_SETS or self.test:
                    source_table = "{0}_{1}_{2}".format(
                        config_entity.import_key or config_entity.key, db_entity.table, 'sample')
                else:
                    source_table = "{0}_{1}".format(config_entity.import_key or config_entity.key, db_entity.table)

                connection_dict = postgres_url_to_connection_dict(db_entity.url)
                self._dump_tables_to_target(
                    '-t %s' % source_table,
                    source_schema='public',
                    target_schema=db_entity.schema,
                    source_table=source_table,
                    target_table=table,
                    connection_dict=connection_dict)

                # Create a spatial index
                spatial_index = '''create index {index_name} on {schema}.{key} using GIST (wkb_geometry);'''.format(
                    index_name=spatial_index_name,
                    schema=db_entity.schema, key=db_entity.key)
                cursor.execute(spatial_index)

            # Whether the table comes from our server or an upload, we want to transform the SRID to 4326
            transform_to_4326 = 'ALTER TABLE {schema}.{table} ALTER COLUMN wkb_geometry ' \
                                'TYPE Geometry(geometry, 4326) ' \
                                'USING ST_Transform(ST_Force_2d(wkb_geometry), 4326);'.format
            logger.info("Transforming to 4326: %s" % transform_to_4326(schema=db_entity.schema, table=db_entity.table))

            cursor.execute(transform_to_4326(schema=db_entity.schema, table=db_entity.table))

            # Now cluster the data and vacuum so that future joins are faster:
            # * CLUSTER rewrites the data on disk so that rows that are spatially near each
            #   other are also near each other on disk
            # * VACUUM cleans up disk space, removing sparse holes on disk.
            # * ANALYZE regenerates statistics about wkb_geometry so that the query planner can make
            #   better decisions.

            logger.info('Clustering %s.%s to optimize spatial joins', db_entity.schema, table)
            cluster = 'CLUSTER {index_name} ON {target_schema}.{target_table};'.format(
                index_name=spatial_index_name,
                target_schema=db_entity.schema,
                target_table=table)
            cursor.execute(cluster)

            logger.info('Vacuuming and analyzing %s.%s.', db_entity.schema, table)
            analyze = 'VACUUM ANALYZE {target_schema}.{target_table};'.format(
                target_schema=db_entity.schema,
                target_table=table)

            cursor.execute(analyze)

            logger.info("Finished importing data for DbEntity table {0}.{1}".format(db_entity.schema, db_entity.key))

    def _dump_tables_to_target(self, table_selector, source_schema=None, target_schema=None, source_table=None, target_table=None, connection_dict=None):
        """
            Dumps the table indicated by the table_selector string to the target_schema on the target database. Throws an exception if the target already exists
        :param table_selector: A string used in pg_dump to specify the table, such as '-t TABLE_NAME'. Optional attributes like --schema-only may be included
        :param source_schema: The optional source_schema to use when specifying a target_schema. Both can be left null or both most be used.
        :param target_schema: The optional target schema on the target database whither to write the table. If None the schema is that of the source
        :param source_table optional table name to use when specifying a target_table. Both can be left null or both most be used.
        :param target_table optional table name to write the table. If None the table is that of the host
        :param connection_dict: The optional database configuration. A dict of user, password, host, port, and database. Defaults to self.pg_dump_connection
        :return: True if the table was created.
        """
        def sed_format(str, required_variables):
            str = str.replace(' ', '\ ')
            str = "sed " + str
            return str.format(source_table=source_table,
                              source_schema=source_schema,
                              target_table=target_table,
                              target_schema=target_schema)

        # The search_path written by pg_dump does not include the postgis schema, so we add it here
        sed_search_path = 'sed %s' % 's/public\,\ pg_catalog/public\,\ pg_catalog\,\ postgis/'
        # We optionally use sed to change the name of the schema and or table
        sed_table = sed_format('s/{source_table}/{target_table}/g', [source_table, target_table])
        # We include the table here so public is only changed where associated with the table
        sed_schema = sed_format('s/{source_schema}\.{target_table}/{target_schema}\.{target_table}/g', [source_schema, target_schema])
        # Also add the schema to the create table statement
        sed_schema_table_create = sed_format("s/CREATE TABLE {target_table}/CREATE TABLE {target_schema}.{target_table}/g", [source_schema, target_schema])
        sed_schema_table_copy = sed_format("s/COPY {target_table}/COPY {target_schema}.{target_table}/g", [source_schema, target_schema])
        sed_schema_table_alter = sed_format("s/ALTER TABLE ONLY {target_table}/ALTER TABLE ONLY {target_schema}.{target_table}/g", [source_schema, target_schema])

        pg_dump_connection = "--host={host} --port={port} --user={user} {database}".format(**connection_dict)
        dump_to_psql_command = ' | '.join(filter(lambda str: str, [
            '{BIN_DIR}/pg_dump {pg_dump_connection} {table_selector}'.format(BIN_DIR=settings.BIN_DIR,
                                               pg_dump_connection=pg_dump_connection, table_selector=table_selector),
            sed_search_path,
            sed_table,
            sed_schema,
            sed_schema_table_create,
            sed_schema_table_copy,
            sed_schema_table_alter,
            '{BIN_DIR}/psql {target_db_connection}'.format(BIN_DIR=settings.BIN_DIR,
                                                           target_db_connection=self.target_database_connection)
        ]))
        results = self.command_execution.run(dump_to_psql_command,
            stdin="{0}\n{1}".format(self.arguments.get('password', None), self.target_database.get('PASSWORD', None))
        )


        return True

    def import_db(self, database_name, local_dump_file):
        # Try to connect
        main_db = pg_connection_parameters(settings.DATABASES['default'])
        db = merge(main_db, dict(database=database_name))

        db_conn_string = "--host={host} --port={port} --user={user}".format(**db)
        self.run_as_pg('createdb {db_conn_string} {name}'.format(
            db_conn_string=db_conn_string,
            name=database_name), **db)

        self.run_as_pg('psql {db_conn_string} -c "CREATE EXTENSION IF NOT EXISTS POSTGIS" {name}'.format(
            db_conn_string=db_conn_string,
            name=database_name), **db)

        self.run_as_pg('psql {db_conn_string} -c "CREATE EXTENSION IF NOT EXISTS DBLINK" {name}'.format(
            db_conn_string=db_conn_string,
            name=database_name), **db)

        self.run_as_pg('''psql {db_conn_string} -c 'ALTER DATABASE {name} SET search_path = "$user",public,postgis;' postgres'''.format(
            db_conn_string=db_conn_string,
            name=database_name), **db)

        self.run_as_pg('psql {db_conn_string} -f {local_dump_file} {name}'.format(
            db_conn_string=db_conn_string,
            local_dump_file=local_dump_file,
            name=database_name), **db)

    def run_as_pg(self, command, **db):
        result = self.command_execution.run(command)
        if result.returncode:
            raise Exception(result.stderr.text)
