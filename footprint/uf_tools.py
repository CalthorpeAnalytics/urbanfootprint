
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

import subprocess
from django.db import connections, transaction, connection
import psycopg2
from footprint.main.utils.utils import database_settings


def connect(conn_string):
    '''given a connection string, connects to the database and returns a cursor '''
    try: gDB = psycopg2.connect( conn_string )
    except Exception, E:
        print str(E)
        raise
    return gDB


def get_conn_string(db_name):
    d = database_settings(db_name)
    return 'dbname=' + d['NAME'] + ' host=' + d['HOST'] + ' user=' + d['USER'] + ' password=' + d['PASSWORD']


def db_table_exists(table, cursor=None):
    try:
        if not cursor:
            from django.db import connection
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        try:
            selection = """SELECT tablename FROM pg_tables"""
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


@transaction.commit_on_success
def executeSQL_now(conn_string, sqls, db=None, **kwargs):
    """
    :param conn_string:
    :param sqls:
    :param db:
    :param kwargs:
    :return:
    """
    cursor = connection.cursor()
    resultset = []

    for sql in sqls:
        try:
            cursor.execute(sql)
            result = cursor.fetchall()

            results = []
            for n in result:
                results.append(n)
            resultset.append(results)

        except Exception, E:
            resultset.append(E)

    return resultset


def dictfetchall(cursor):
    """
        Wraps the cursor results into dicts.
        Call this after cursor.execute()
    :param cursor:
    :return:
    """
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


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
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_geotype_wkb_geometry check(geometrytype(wkb_geometry) = '{2}');".format(schema, table, geom_type)
    executeSQL_now(conn_string, [add_constraint])


def add_constraint_SRID(conn_string, schema, table, srid):
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_srid_wkb_geometry check (st_srid(wkb_geometry) = '{2}');".format(schema, table, srid)
    executeSQL_now(conn_string, [add_constraint])

def add_constraint_geom_dims(conn_string, schema, table, geom_dims):
    add_constraint = "ALTER TABLE {0}.{1} ADD CONSTRAINT enforce_dims_wkb_geometry check (ST_CoordDim(wkb_geometry) = {2});".format(schema, table, geom_dims)
    executeSQL_now(conn_string, [add_constraint])

# drop a constraint
def drop_spatial_constraint(conn_string, schema, table, type, column):
    query = 'ALTER TABLE {0}.{1} DROP CONSTRAINT enforce_{2}_{3};'.format(schema, table, type, column)
    executeSQL_now(conn_string, [query])

# add geometric index
def add_geom_idx(conn_string, schema, table, column="wkb_geometry"):
    query = 'CREATE INDEX {0}_geom_idx on {1}.{0} using GIST ({2});'.format(table, schema, column)
    executeSQL_now(conn_string, [query])
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
                add_constraint_SRID(conn_string,schema,table,srid[0])
                info += ': added SRID constraint, '
        except Exception, E:
            print E
            raise
    else: info += ': SRID OK, '

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
        except Exception, E: print E; raise

    else: info += ' geom_type OK, '

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

    else: info += ' coord_dims OK '

    print info

def reproject_table(conn_string, schema, table, srid):
#    old_srid, type, coords = get_geom_reg(conn_string, schema, table)
#    drop_spatial_constraint(conn_string,schema,table,type,'wkb_geometry')
#    if old_srid <> 0:
#        # TODO column doesn't exist
#        #drop_spatial_constraint(conn_string, schema, table, 'srid', column)
#        pass
    reproject = 'UPDATE {0}.{1} set wkb_geometry = ST_setSRID(ST_transform(wkb_geometry, {2}),{2});'\
        .format(schema, table, srid)
    executeSQL_now(conn_string, [reproject])
    add_geom_idx(conn_string, schema, table)

#    add_constraint_SRID(conn_string, schema, table, srid)

def ogr_to_gdb(conn_string, schema, table, output_gdb):

    reproject_table(conn_string, schema, table, '4326')
    ogr_command = 'ogr2ogr -overwrite -skipfailures -f "FileGDB" "{1}" PG:"{0}" "{2}.{3}" '\
        .format(conn_string, output_gdb, schema, table)
    print ogr_command
    subprocess.call(ogr_command, shell=True)



def getis_ord(schema, table, field, distance, nonzero_field="wkb_geometry"):
    """
    this is a first pass at a stat function ... should be moved somewhere and guard rails should be installed
    to prevent / deter bad analysis
    :param schema:
    :param table:
    :param field:
    :param distance:
    :param nonzero_field:
    :return:
    """
    stat_totals = ''' select sum({2}), count(id_grid), avg({2}) from {0}.{1} where {2} <> 0;
        '''.format(schema, table, field, distance, nonzero_field)

    stat_totals = executeSQL_now('default', [stat_totals])[0]

    stat_total = stat_totals[0]
    N = stat_totals[1]
    mean_stat = stat_totals[2]

    print "feature_count = " + str(N)
    print "mean value = " + str(mean_stat)

    n_buffer = '''
        CREATE OR REPLACE FUNCTION get_nbuffer_{2} (
          in_id_grid integer,
          in_geom geometry,
          {2} float,
          dist float,
          OUT id_grid integer,
          OUT wkb_geometry geometry,
          OUT {2}_{3}m float,
          OUT {2} float
          )
        AS
        $$
          select $1 as id_grid,
          $2 as wkb_geometry,
          $3 as {2},
          sum(r.{2}) as {2}_{3}m

          FROM {0}.{1} r WHERE st_dwithin($2, r.wkb_geometry, $4)
            AND id_grid is not Null
            AND {2} <> 0;
        $$
        COST 10000
        language SQL STABLE strict;
        '''.format(schema, table, field, distance, nonzero_field)

    cluster_tbl = '''
                    drop table if exists {0}.{1}_{2}_{3}m_tmp cascade;

                    create table {0}.{1}_{2}_{3}m_tmp (
                    id_grid         integer,
                    wkb_geometry    geometry,
                    {2}             float,
                    {2}_{3}m         float
                    );

                    insert into {0}.{1}_{2}_{3}m_tmp select
                    (f).* from (
                        select get_nbuffer_{2}(id_grid, wkb_geometry, {2}, {3}) as f
                        from {0}.{1} where {2} <> 0) s
                        ;

                    alter table {0}.{1}_{2}_{3}m_tmp add column getis_ord_gi float;
                    alter table {0}.{1}_{2}_{3}m_tmp add column expected_gi float;

                    update {0}.{1}_{2}_{3}m_tmp
                        set getis_ord_gi = {2}_{3}m / {4},
                        expected_gi  = {2}_{3}m / ({5} - 1);

                    drop table if exists {0}.{2}_cluster_{3}m cascade;

                    '''.format(schema, table, field, distance, stat_total, N, mean_stat, nonzero_field)

    executeSQL_now('default', [n_buffer, cluster_tbl])
#    variance = '''select sum( (getis_ord_gi - {6}) ^2 ) / {5} as z_score
#    from {0}.{1}_{2}_{3}m_tmp'''.format(schema, table, field, distance, stat_total, N, mean_ord)
    variance = '''select variance(getis_ord_gi) from {0}.{1}_{2}_{3}m_tmp;'''.format(schema, table, field, distance)

    variance = executeSQL_now('default', [variance])[0][0]
    print variance

    z_score = '''create table {0}.{2}_cluster_{3}m as select
            id_grid,
            wkb_geometry,
            {2},
            {2}_{3}m,
            getis_ord_gi,
            (getis_ord_gi - expected_gi)/sqrt({4}) as z_score
            from {0}.{1}_{2}_{3}m_tmp;
            drop table {0}.{1}_{2}_{3}m_tmp cascade;
    '''.format(schema, table, field, distance, variance)

    executeSQL_now('default', [z_score])

    print "ok"
