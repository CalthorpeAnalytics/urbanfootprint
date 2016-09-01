# coding=utf-8

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

import urllib2
from logging import getLogger

import psycopg2
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, connections, connection
from django.db.backends.postgresql_psycopg2.introspection import DatabaseIntrospection

from footprint.main.managers.database.managers import InformationSchemaManager, PGNamespaceManager
from footprint.main.utils.utils import parse_schema_and_table, increment_key
from footprint.utils.postgres_utils import pg_connection_parameters

logger = getLogger(__name__)
__author__ = 'calthorpe_analytics'


class InformationSchema(models.Model):

    table_catalog = models.CharField(max_length = 100)
    table_schema = models.CharField(max_length = 100)
    table_name = models.CharField(max_length = 100)
    # Pretend this is the primary key since the table doesn't have a single column primary key
    column_name = models.CharField(max_length = 100, null=False, primary_key=True)
    data_type = models.CharField(max_length = 100)
    udt_name = models.CharField(max_length = 100, null=False, primary_key=True)

    objects = InformationSchemaManager()

    def __unicode__(self):
        return "Catalog: {0}, Schema: {1}, Table: {2}, Column: {3}, Type: {4}".format(self.table_catalog, self.table_schema, self.table_name, self.column_name, self.data_type)

    def full_table_name(self):
        return "{0}.{1}".format(self.table_schema, self.table_name)

    @classmethod
    def create_primary_key_column_from_another_column(cls, schema, table, primary_key_column, from_column=None):
        """
            Adds the column of the given type to the given table if absent
        :param schema: The database schema name
        :param table: The table name
        :param primary_key_column: Name of primary key column to create. If a primary key already exists it will be
        renamed from this, unless from_column is specified, in which case the existing primary_key will lose its constraint
        """
        full_tablename = '"{schema}"."{table}"'.format(schema=schema, table=table)
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        existing_primary_key = InformationSchema.get_primary_key_name(schema, table)
        if existing_primary_key:
            logger.info('Found existing primary key %s' % existing_primary_key)

        if not InformationSchema.objects.has_column(schema, table, primary_key_column):
            # If not create a primary key or alter the existing one's name
            # Copy values from the from_column to the new primary_key_column
            if existing_primary_key and not from_column:
                # Rename the primary key to primary_key_column and end
                alter_source_id_sql = 'alter table {full_tablename} rename column {existing_primary_key} to {primary_key_column}'.format(
                    full_tablename=full_tablename, existing_primary_key=existing_primary_key, primary_key_column=primary_key_column)
                logger.info('Existing primary key exists and no from column is specified. Executing: %s' % alter_source_id_sql)
                cursor.execute(alter_source_id_sql)
                return

            if from_column:
                # Create a new primary key column without values
                create_column_sql = 'alter table {full_tablename} add column {primary_key_column} integer'.format(
                    full_tablename=full_tablename, primary_key_column=primary_key_column)
                logger.info('From column is specified to be primary key source. Executing: %s' % create_column_sql)
                cursor.execute(create_column_sql)
                # Copy values from the from_column, always casting to integer
                update_sql = 'update {full_tablename} set {primary_key_column} = cast({from_column} AS integer)'.format(
                    full_tablename=full_tablename, primary_key_column=primary_key_column, from_column=from_column)
                logger.info('Copying values from column to primary key. Executing: %s' % update_sql)
                cursor.execute(update_sql)
            else:
                # Populate with a serial primary key
                alter_source_id_sql = 'alter table {full_tablename} add column {primary_key_column} serial primary key'.format(
                    full_tablename=full_tablename, primary_key_column=primary_key_column)
                logger.info('Copying values from column to primary key. Executing: %s' % alter_source_id_sql)
                cursor.execute(alter_source_id_sql)
            # Drop the original_primary_key column if it exists
            if existing_primary_key:
                alter_source_id_sql = 'alter table {full_tablename} drop column {existing_primary_key}'.format(
                    full_tablename=full_tablename, existing_primary_key=existing_primary_key)
                logger.info('Existing primary key being removed. Executing: %s' % alter_source_id_sql)
                cursor.execute(alter_source_id_sql)
            if from_column:
                # Create the primary key constraint if we haven't yet
                alter_source_id_sql = 'alter table {full_tablename} add constraint {table}_{schema}_{primary_key_column}_pk primary key ({primary_key_column})'.format(
                    full_tablename=full_tablename, table=table, schema=schema, primary_key_column=primary_key_column)
                logger.info('Adding constraint to primary key. Executing: %s' % alter_source_id_sql)
                cursor.execute(alter_source_id_sql)
        elif existing_primary_key != primary_key_column:
            # If there a column matching primary_key_column that isn't the primary key, we need to rename
            # the primary_key_column to something unique and then rename existing_primary_key to primary_key_column

            # Find a unique column to rename primary_key_column (e.g. renamed id to id_1, or id_2, etc)
            unique_column = increment_key(primary_key_column)
            while InformationSchema.objects.has_column(schema, table, unique_column):
                unique_column = increment_key(unique_column)

            # Rename the primary_key_column
            rename_primary_key_column_name_sql = 'alter table {full_tablename} rename column {primary_key_column} to {unique_column}'.format(
                full_tablename=full_tablename, primary_key_column=primary_key_column, unique_column=unique_column)
            logger.info('Existing column with primary key name exists that needs to be renamed: %s' % rename_primary_key_column_name_sql)
            cursor.execute(rename_primary_key_column_name_sql)

            # Rename the existing_primary_key to primary_key_column (e.g. rename to ogc_fid to id for uploaded tables)
            rename_existing_primary_key_sql = 'alter table {full_tablename} rename column {existing_primary_key} to {primary_key_column}'.format(
                    full_tablename=full_tablename, existing_primary_key=existing_primary_key, primary_key_column=primary_key_column)
            logger.info('Existing primary key exists that needs to be renamed to desired primary key column name. Executing: %s' % rename_existing_primary_key_sql)
            cursor.execute(rename_existing_primary_key_sql)

    @classmethod
    def get_primary_key_name(cls, schema, table):
        """
            Uses the inspection code to find the primary key column name, if one exists
        :param schema:
        :param table:
        :return: The primary key name or None
        """

        connection = connections['default']
        cursor = connection.cursor()
        table_name = '"{schema}"."{table}"'.format(schema=schema, table=table)

        # Use our own class to make up for lack of schema support in table queries
        smart_database_introspection = SmartDatabaseIntrospection(connection)
        try:
            indexes = smart_database_introspection.get_indexes(cursor, table_name)
        except NotImplementedError:
            indexes = {}

        # Fill this dict with field definitions
        for i, row in enumerate(smart_database_introspection.get_table_description(cursor, table_name)):
            column_name = row[0]
            # Add primary_key and unique, if necessary.
            if column_name in indexes:
                if indexes[column_name]['primary_key']:
                    return column_name


    class Meta(object):
        db_table = '"information_schema"."columns"'

class PGNamespace(models.Model):
    """
     This class is just needed to list schemas and see if they exist if they have no tables
    """
    # Pretend this is the primary key since the table doesn't have a single column primary key
    nspname = models.CharField(max_length = 100, null=False, primary_key=True)
    objects = PGNamespaceManager()

    class Meta(object):
        db_table = 'pg_namespace'


class SouthMigrationHistory(models.Model):
    """
     This class is just needed to list schemas and see if they exist if they have no tables
    """
    # Pretend this is the primary key since the table doesn't have a single column primary key
    id = models.IntegerField(null=False, primary_key=True)
    app_name = models.CharField(max_length=100)
    migration = models.CharField(max_length=100)
    applied = models.DateTimeField()

    class Meta(object):
        db_table = 'south_migrationhistory'


class SpatialRefSys(models.Model):
    proj4text = models.CharField(max_length=2048)
    srtext = models.CharField(max_length=2048)
    auth_srid = models.IntegerField()
    auth_name = models.CharField(max_length=2048)
    srid = models.IntegerField(primary_key=True)

    class Meta(object):
        db_table = 'spatial_ref_sys'


class GeometryColumns(models.Model):

    f_table_catalog = models.CharField(max_length=256, null=False)
    f_table_schema = models.CharField(max_length=256, null=False, primary_key=True)
    f_table_name = models.CharField(max_length=256, null=False, primary_key=True)
    f_geometry_column = models.CharField(max_length=256, null=False, primary_key=True)
    coord_dimension = models.IntegerField(null=False)
    srid = models.IntegerField(null=False)
    type = models.CharField(max_length=30, null=False)

    class Meta(object):
        db_table = 'geometry_columns'


def sync_geometry_columns(schema=None, table=None):
    """
    Adds one or more entries to the PostGIS geometry_columns
    :param schema: Optional database schema to which to limit search
    :param table: Optional table name to which to limit search
    :return:
    """
    tables_with_geometry = InformationSchema.objects.tables_with_geometry(schema=schema, table=table)
    for information_scheme in tables_with_geometry:

        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        sql = "select ST_CoordDim({2}), ST_SRID({2}), ST_GeometryType({2}) from {1}.{0}".format(information_scheme.table_name, information_scheme.table_schema, information_scheme.column_name)
        ret = cursor.execute(sql)
        if ret and len(ret) > 0:
            coord, srid, geom_type = ret[0]
        else:
            coord, srid, geom_type = (2, 4326, 'GEOMETRY')
        geometry_record, new_record = GeometryColumns.objects.get_or_create(
            f_table_name=information_scheme.table_name,
            f_geometry_column=information_scheme.column_name,
            f_table_schema=information_scheme.table_schema,
                defaults=dict(
                    coord_dimension=coord,
                    srid=srid,
                    type=geom_type,
                ))
        if not new_record:
            geometry_record.coord_dimension = coord
            geometry_record.srid = srid
            geometry_record.type = geom_type
            geometry_record.save()


def scrape_insert_from_spatialreference(authority, srid):
    address = "http://www.spatialreference.org/ref/{1}/{0}/postgis/".format(srid, authority)
    logger.info('Looking up {authority}:{srid}'.format(srid=srid, authority=authority))
    try:
        return urllib2.urlopen(address).read()
    except:
        logger.warn('Could not find SRID {srid}!'.format(srid=srid))
        return None


def verify_srid(srid):
    try:
        srs = SpatialRefSys.objects.get(auth_srid=int(srid))
        logger.info("Using SRID: " + srid)
        return srs
    except ObjectDoesNotExist:
        insert = scrape_insert_from_spatialreference('esri', srid)
        if insert:
            logger.info("Inserting {srid} into spatial_ref_sys table".format(srid=srid))
            logger.info(insert)
            connection.cursor().execute(insert)
            srs = SpatialRefSys.objects.filter(auth_srid=int(srid))
            if srs.count():
                return srs[0]

    return False


class SmartDatabaseIntrospection(DatabaseIntrospection):

    def describe_table_columns(self, cursor, full_table_name):
        schema, table = parse_schema_and_table(full_table_name)
        # conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        # conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        # cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s and table_schema = %s""", [table, schema])
        null_map = dict(cursor.fetchall())
        cursor.execute('SELECT * FROM "{schema}"."{table}" LIMIT 1'.format(schema=schema, table=table))
        return cursor.description

    def get_table_description(self, cursor, full_table_name):
        """
            Override the parent method to take schemas into account, sigh
        :param cursor:
        :param full_table_name:
        :return:
        """
        schema, table = parse_schema_and_table(full_table_name)
        # conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        # conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        # cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s and table_schema = %s""", [table, schema])
        null_map = dict(cursor.fetchall())
        cursor.execute('SELECT * FROM "{schema}"."{table}" LIMIT 1'.format(schema=schema, table=table))
        return [tuple([item for item in line[:6]] + [null_map[line[0]]==u'YES'])
                for line in cursor.description]


    def get_indexes(self, cursor, table_name):
        """
            OVERRIDDEN to work with schemas, sigh

        Returns a dictionary of fieldname -> infodict for the given table,
        where each infodict is in the format:
            {'primary_key': boolean representing whether it's the primary key,
             'unique': boolean representing whether it's a unique index}
        """
        schema, table = parse_schema_and_table(table_name)
        # This query retrieves each index on the given table, including the
        # first associated field name
        cursor.execute("""
            SELECT attr.attname, idx.indkey, idx.indisunique, idx.indisprimary
            FROM pg_catalog.pg_class c, pg_catalog.pg_class c2,
                pg_catalog.pg_index idx, pg_catalog.pg_attribute attr,
                information_schema.columns isc
            WHERE c.oid = idx.indrelid
                AND idx.indexrelid = c2.oid
                AND attr.attrelid = c.oid
                AND attr.attnum = idx.indkey[0]
                AND c.relname = %s
                AND c.relname = isc.table_name
                AND isc.table_schema = %s
                AND isc.column_name = attr.attname
                """, [table, schema])
        indexes = {}
        for row in cursor.fetchall():
            # row[1] (idx.indkey) is stored in the DB as an array. It comes out as
            # a string of space-separated integers. This designates the field
            # indexes (1-based) of the fields that have indexes on the table.
            # Here, we skip any indexes across multiple fields.
            if ' ' in row[1]:
                continue
            indexes[row[0]] = {'primary_key': row[3], 'unique': row[2]}
        return indexes
