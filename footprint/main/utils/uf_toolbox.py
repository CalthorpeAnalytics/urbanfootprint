
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

import Queue
import multiprocessing
import subprocess
import threading
from itertools import chain

import psycopg2
import logging
logger = logging.getLogger(__name__)

##-----------------------------------------------
from django.conf import settings
from django.db import connection
from footprint.utils.postgres_utils import pg_connection_parameters


class MultithreadProcess(threading.Thread):
    """Threaded Unit of work"""

    def __init__(self, queue, sql_to_execute):
        threading.Thread.__init__(self)
        self.queue = queue
        self.sql_to_execute = sql_to_execute

    def run(self):
        while True:
            #grabs host from queue
            job = self.queue.get()
            Task = self.sql_to_execute.format(start_id=job['start_id'], end_id=job['end_id'])
            execute_sql(Task)
            self.queue.task_done()
            return


def queue_process():
    queue = Queue.Queue()
    return queue


def execute_sql(pSQL):

    conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()

    try:
        logger.debug("executing custom sql: {0}".format(pSQL))
        curs.execute(pSQL)
    except Exception, E:
        print str(E)
        raise Exception('SQL: {0}. Original Message: {1}'.format(pSQL, E.message))
    finally:
        conn.commit()
        curs.close()


def copy_from_text_to_db(text_file, table_name):

    conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    try:
        logger.debug("Text file: {0}, Table name: {1}".format(text_file, table_name))
        curs.copy_from(text_file, table_name)
    except Exception, E:
        print str(E)
        raise Exception('Original Message: {0}'.format(E.message))
    finally:
        conn.commit()
        curs.close()


def flatten(list_of_lists):
    """
        Shallow flatten a multi-dimensional list, meaning the top two dimensions are flattened and deeper ones are ignored
    """
    return list(chain.from_iterable(list_of_lists))

def report_sql_values(pSQL, fetch_type):
    # with transaction.commit_manually():
    try:
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()
    except Exception, E:
        print str(E)

    try:
        logger.debug('executing custom report sql: {0}'.format(pSQL))
        curs.execute(pSQL)
        sql_values = getattr(curs, fetch_type)()
    except:
        sql_values = []

    curs.close()
    return sql_values


def copy_to_psql(output_tmp, cDSN, working_schema, tmp_table_name):
    try:
        conn = psycopg2.connect(cDSN)
    except Exception, E:
        print str(E)
    curs = conn.cursor()

    curs.copy_from(output_tmp, working_schema + "." + tmp_table_name)
    conn.commit()
    curs.close()

def connect(conn_string):
    '''given a connection string, connects to the database and returns a cursor '''
    try:
        gDB = psycopg2.connect(conn_string)
    except Exception, E:
        print str(E)
        raise
    return gDB


def get_conn_string(db_name):
    d = database_settings(db_name)
    return 'dbname=' + d['NAME'] + ' host=' + d['HOST'] + ' user=' + d['USER'] + ' password=' + d['PASSWORD']


def report_sql_values_as_dict(query):

    from django.db import connection
    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except Exception, E:
        print str(E)

    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return r if r else None


def db_table_exists(table, cursor=None):
    try:
        if not cursor:
            from django.db import connection

            cursor = connection.cursor()
        if not cursor:
            raise Exception
        try:
            cursor.execute("SELECT tablename FROM pg_tables")
        except:
            raise
        table_names = cursor.fetchall()
        tables = []
        for t in table_names:
            tables.append(t[0])
            # table_names = connection.introspection.get_table_list(cursor)
    except:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in tables

def table_exists(table, schema='public'):
    cursor = connection.cursor()
    query = "select count(*) from information_schema.tables where table_name = '{table}' and table_schema = '{schema}'".format(table=table, schema=schema)
    cursor.execute(query)
    result = cursor.fetchone()[0]

    return result == True

def executeSQL_now(conn_string, sqls, db=None, **kwargs):
    resultset = []
    for sql in sqls:
        try:
            db = connect(conn_string)
            gCurs = db.cursor()

            try:
                gCurs.execute(sql)
            except Exception, E:
                print str(E)
                raise

            try:
                result = gCurs.fetchall()
            except:
                result = ()
            gCurs.close()
            db.commit()

            results = []
            for n in result: results.append(n)
            resultset.append(results)

        except Exception, E:
            try:
                gCurs.close()
            except:
                pass
            resultset.append(E)

    return resultset


def get_geom_reg(conn_string, schema, table):
    #TODO: update this to use the views.geometry columns
    query = "select srid, type, coord_dimension from views.geometry_columns " \
            "where f_table_schema = '{0}' and f_table_name = '{1}'".format(schema, table)
    return executeSQL_now(conn_string, [query])[0][0]


def list_all_geom_tables(conn_string):
    query = "select table_schema, table_name from information_schema.columns where column_name = 'wkb_geometry';"
    return executeSQL_now(conn_string, [query])


def get_constraints(conn_string, schema, table):
    query = """select constraint_name from information_schema.constraint_column_usage
    where table_schema = '{0}' and table_name = '{1}'""".format(schema, table)
    return executeSQL_now(conn_string, [query])

# return qualities of the geometry field

def get_geom_type(conn_string, schema, table):
    query = "select distinct(geometrytype(wkb_geometry)) from {0}.{1}".format(schema, table)
    return executeSQL_now(conn_string, [query])


def get_geom_SRID(conn_string, schema, table):
    query = "select distinct(st_srid(wkb_geometry)) from {0}.{1}".format(schema, table)
    return executeSQL_now(conn_string, [query])


def get_geom_dims(conn_string, schema, table):
    query = "select distinct(ST_CoordDim(wkb_geometry)) from {0}.{1}".format(schema, table)
    return executeSQL_now(conn_string, [query])

# add constraints functions

def add_constraint_geom_type(conn_string, schema, table, geom_type):
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_geotype_wkb_geometry check(geometrytype(wkb_geometry) = '{2}');".format(
        schema, table, geom_type)
    executeSQL_now(conn_string, [add_constraint])


def add_constraint_SRID(schema, table, srid):
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_srid_wkb_geometry check (st_srid(wkb_geometry) = '{2}');".format(
        schema, table, srid)
    execute_sql(add_constraint)


def add_constraint_geom_dims(conn_string, schema, table, geom_dims):
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_dims_wkb_geometry check (ST_CoordDim(wkb_geometry) = {2});".format(
        schema, table, geom_dims)
    executeSQL_now(conn_string, [add_constraint])

# drop a constraint
def drop_spatial_constraint(schema, table, type, column):
    query = 'ALTER TABLE {0}.{1} DROP CONSTRAINT enforce_{2}_{3};'.format(schema, table, type, column)
    execute_sql(query)

# add geometric index
def add_geom_idx(schema, table, column="wkb_geometry"):

    query = '''
    CREATE INDEX on {schema}.{table} using GIST ({column});'''.format(table=table, schema=schema, column=column)
    execute_sql(query)


def drop_geom_idx(schema, table):
    query = 'DROP INDEX {0}."{1}_wkb_geometry_id";'.format(schema, table)
    execute_sql(query)


def add_attribute_idx(schema, table, field):
    query = '''create index {1}_{2}_idx on {0}.{1} ({2});'''.format(schema, table, field)
    execute_sql(query)


def add_primary_key(schema, table, field):
    query = '''alter table {0}.{1} add constraint {1}_pkey primary key ({2});'''.format(schema, table, field)
    execute_sql(query)


def drop_table(table_name):
    pSql = '''drop table if exists {0} cascade;'''.format(table_name)
    execute_sql(pSql)

def truncate_table(table_name):
    pSql = '''truncate table {0} cascade;'''.format(table_name)
    execute_sql(pSql)

#----------------------------------------------------------------------------------------
def count_cores():
    return multiprocessing.cpu_count()


def create_sql_calculations(table_fields, sql_format, seperator=', '):

    sql_calculations = ''
    count = 1
    if len(table_fields) > 0:
        for field in table_fields:
            if count == 1:
                format = sql_format
                sql_calculations += format.format(field)
            else:
                format = seperator + sql_format
                sql_calculations += format.format(field)
            count += 1

    return sql_calculations

def create_sql_calculations_two_variables(table_fields, sql_query):
    sql_calculations = ''
    if len(table_fields) > 0:
        for field in table_fields:
            sql_calculations += sql_query.format(field[0], field[1])
    return sql_calculations


def create_sql_calculations_four_variables(table_fields, sql_query):
    sql_calculations = ''
    for field in table_fields:
        sql_calculations += sql_query.format(field[0], field[1], field[2], field[3], field[4])
    return sql_calculations


# make sure all spatial tables in db have proper constraints
# this will ensure that they are registered in the geometry_columns view
def validate_constraints_whole_db(conn_string):
    geom_tables = list_all_geom_tables(conn_string)
    for t in geom_tables[0]:
        schema, table = t[0], t[1]
        validate_constraints(conn_string, schema, table)


def validate_constraints(conn_string, schema, table):
    info = schema + '.' + table
    constraints = get_constraints(conn_string, schema, table)[0]

    # make sure the SRID has a constraint, and if not, create one
    if ("enforce_srid_wkb_geometry",) not in constraints:
        try:
            srid = get_geom_SRID(conn_string, schema, table)[0][0]
            # TODO: better error handling here -- can we try fixing the problem before rejecting it?
            if len(srid) > 1:
                print "there are multiple SRID's for this table, cannot add constraint"
                raise
            elif len(srid) == 0:
                print "there is no SRID for the geometry in this table. cannot add constraint"
                raise
            else:
                add_constraint_SRID(conn_string, schema, table, srid[0])
                info += ': added SRID constraint, '
        except Exception, E:
            print E
            raise
    else:
        info += ': SRID OK, '

    # make sure the geometry type has a constraint, and if not, create one
    if ("enforce_geotype_wkb_geometry",) not in constraints:
        try:
            geom_type = get_geom_type(conn_string, schema, table)[0][0]
            # TODO: better error handling here -- can we try fixing the problem before rejecting it?
            if len(geom_type) > 1:
                print "there are multiple geometry types for this table. cannot add constraint"
                raise
            elif len(geom_type) == 0:
                print "there is no geometry type for the geometry in this table. cannot add constraint"
                raise
            else:
                add_constraint_geom_type(conn_string, schema, table, geom_type[0])
                info += ' added geom_type constraint, '
        except Exception, E:
            print E
            raise

    else:
        info += ' geom_type OK, '

    # make sure the number of dimensions has a constraint, and if not, create one
    if ("enforce_dims_wkb_geometry",) not in constraints:
        try:
            dims = get_geom_dims(conn_string, schema, table)[0][0]
            # TODO: better error handling here -- can we try fixing the problem before rejecting it?
            if len(dims) > 1:
                print "there are inconsistent coordinate dimensions for this table. cannot add constraint"
                raise
            elif len(dims) == 0:
                print "there are no coordinate dimensions for the geometry in this table. cannot add constraint"
                raise
            else:
                add_constraint_geom_dims(conn_string, schema, table, dims[0])
                info += ' added coord_dims constraint'
        except Exception, E:
            print E
            raise

    else:
        info += ' coord_dims OK '

    print info


def reproject_table(schema, table, srid):

    reproject = 'UPDATE {0}.{1} set wkb_geometry = ST_setSRID(ST_transform(wkb_geometry, {2}),{2});' \
        .format(schema, table, srid)
    execute_sql(reproject)


def ogr_to_gdb(conn_string, schema, table, output_gdb):
    reproject_table(conn_string, schema, table, '4326')
    ogr_command = 'ogr2ogr -overwrite -skipfailures -f "FileGDB" "{1}" PG:"{0}" "{2}.{3}" ' \
        .format(conn_string, output_gdb, schema, table)
    print ogr_command
    subprocess.call(ogr_command, shell=True)


def register_geometry_columns(schema=None):
    select_tables = "Truncate geometry_columns cascade; \n" \
                    "select table_name, table_schema from information_schema.columns " \
                    "where column_name = 'wkb_geometry' " \
                    "and table_schema = '{0}';".format(schema)
    if not schema:
        select_tables = "Truncate geometry_columns cascade; \n" \
                        "select table_name, table_schema from information_schema.columns " \
                        "where column_name = 'wkb_geometry';"

    params = pg_connection_parameters(settings.DATABASES['default'])
    connection = psycopg2.connect(**params)
    gCurs = connection.cursor()

    try:
        print select_tables
        gCurs.execute(select_tables)
    except Exception, E:
        print str(E)
        raise
    tables_to_fix = gCurs.fetchall()
    print tables_to_fix
    if not schema:
        print "assigning schema"

    for table, schema in tables_to_fix:
        update = '''
        INSERT INTO geometry_columns(f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, "type")
        SELECT '', '{schema}', '{table}', 'wkb_geometry', ST_CoordDim(wkb_geometry), ST_SRID(wkb_geometry), ST_GeometryType(wkb_geometry)
        FROM {schema}.{table} LIMIT 1;'''.format(schema=schema, table=table)
        print update
        gCurs.execute(update)
    connection.commit()

        # try:
        #     print update
        #     r = gCurs.execute(update)
        #     gDB.commit()
        # except Exception, E:
        #     print str(E)
        #     gDB.close()
        #     gDB = psycopg2.connect(server)
        #     gCurs = gDB.cursor()
