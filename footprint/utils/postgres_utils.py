
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

from contextlib import contextmanager
import os

def build_postgres_conn_string(omit_db=False):
    '''
    Builds a postgres connection string based on the settings
    of a particular database (e.g settings.DATABASES['default'])
    '''

    # We may want to ommit port & host depending on how pg_hba.conf has been configured
    # (TCP sockets vs unix sockets). Specifying the port/host triggers a different authentication mechanism

    pg_conn_string = ''

    port = os.environ['DATABASE_PORT']
    host = os.environ['DATABASE_HOST']
    user = os.environ['DATABASE_USERNAME']
    name = os.environ['DATABASE_NAME']

    if port:
        pg_conn_string += '-p {port} '.format(port=port)

    if host:
        pg_conn_string += '-h {host} '.format(host=host)

    if user:
        pg_conn_string += '-U {user} '.format(user=user)

    if not omit_db:
        pg_conn_string += '{dbname}'.format(dbname=name)

    return pg_conn_string

def pg_connection_parameters(db_settings):
    return dict(database=db_settings['NAME'], host=db_settings['HOST'], user=db_settings['USER'], port=db_settings.get('PORT', 5432), password=db_settings['PASSWORD'])

@contextmanager
def postgres_env_password_loaded():
    '''Configure external PGPASSWORD environment variable.

    Sets the postgres-specific environment variable 'PGPASSWORD'
    variable so that postgres utilities can see it.
    '''
    var_existed = False

    if 'PGPASSWORD' in os.environ:
        old_val = os.environ['PGPASSWORD']
        var_existed = True

    os.environ["PGPASSWORD"] = os.environ['DATABASE_PASSWORD']

    try:
        yield
    finally:
        if var_existed:
            os.environ['PGPASSWORD'] = old_val
        else:
            del os.environ['PGPASSWORD']
