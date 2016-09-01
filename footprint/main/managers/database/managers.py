
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

import psycopg2
from django.conf import settings
from django.db import connection
from django.db import models, transaction

from footprint.main.lib.functions import merge, compact_dict
from footprint.utils.postgres_utils import pg_connection_parameters

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class InformationSchemaManager(models.Manager):
    def tables_of_schema(self, schema, **kwargs):
        return self.values('table_name').annotate().filter(table_schema=schema, **kwargs)

    def tables_of_schema_with_column(self, schema, column):
        return self.values('table_name').annotate().filter(table_schema=schema, column_name=column)

    def columns_of_table(self, schema, table, column_name=None):
        """
            Returns the columns matching the given schema, table, and column_name
        :param schema:
        :param table:
        :param column_name: Optionally limit the result to a single value
        :return: The matching InformationSchema instances
        """
        return self.filter(**compact_dict(dict(table_schema=schema, table_name=table, column_name=column_name)))

    def has_column(self, schema, table, column_name):
        """
            Returns true if the give column exists for the given schema and table, otherwise false
        :param schema:
        :param table:
        :param column_name:
        :return:
        """
        return len(self.columns_of_table(schema, table, column_name)) == 1

    def table_exists(self, schema, table):
        return len(self.filter(table_schema=schema, table_name=table)) > 0

    def tables_with_geometry(self, schema=None, table=None):
        """
            Returns tables with a column data type of 'geometry'
        :param schema: Optional schema to search
        :param table: Optional table to which to limit search. This guarantees 0 or 1 result
        :return:
        """
        return self.filter(**merge(dict(udt_name='geometry'),
                                   compact_dict(dict(table_schema=schema, table_name=table))))

class PGNamespaceManager(models.Manager):
    def schema_exists(self, schema):
        return len(self.filter(nspname=schema)) > 0

    def create_schema(self, schema, connection=connection):
        if not self.schema_exists(schema):
            logger.info("Creating schema %s" % schema)

            conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute('create schema {0}'.format(schema))
            logger.info("Schema %s created" % schema)
            # This has to be here to create the schema immediately. I don't know why
            if transaction.is_managed():
                transaction.commit()
        else:
            logger.info("Schema %s already exists" % schema)

    def drop_schema(self, schema, connection=connection):
        if self.schema_exists(schema):
            logger.info("Dropping schema %s" % schema)

            conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute('drop schema {0} cascade'.format(schema))
            logger.info("Schema %s dropped" % schema)
