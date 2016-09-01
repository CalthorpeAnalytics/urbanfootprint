#coding=utf-8

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

from django.core.management.color import color_style
from django.db.models import DateTimeField
from django.template.defaultfilters import slugify

from footprint.main.lib.functions import map_to_dict
from footprint.main.models.analysis.agriculture_feature import AgricultureFeature
from footprint.main.models.config.project import Project
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.dynamic_subclassing import create_tables_for_dynamic_classes
from footprint.main.utils.utils import get_client_source_data_connection, full_module_path


__author__ = 'calthorpe_analytics'

import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SourceTableLoader(object):

    def create_sample_data(self, project, full_table, source_table='base_feature'):
        """
        creates a subset of the source table, based on the rows in another sample table (base geography, by default)
        """
        sample_table_name = full_table + '_sample'
        source_table = project + '_' + source_table + '_sample'
        create_sample_sql = '''drop table if exists {sample_table} cascade;
          create table {sample_table} as select a.* from {full_table} a, {source_table} b
          where a.geography_id = b.geography_id'''.format(
            sample_table=sample_table_name,
            full_table=full_table,
            source_table=source_table
        )
        return create_sample_sql

    def create_empty_source_table(self, clazz, source_table_name, source_db_connection, extra_fields={}):
        project = Project(key='sutter_county', id=0)
        db_entity = DbEntity(key=Keys.DB_ABSTRACT_BASE_AGRICULTURE_FEATURE, feature_class_configuration=dict(
            abstract_class=full_module_path(clazz)
        ))
        SourceClass = FeatureClassCreator(project, db_entity, no_ensure=True).dynamic_model_class(base_only=True, schema='public', table=source_table_name)
        # class SourceClass(clazz):
        #     class Meta(clazz.Meta):
        #         db_table = source_table_name
        create_tables_for_dynamic_classes(SourceClass)
        for field in SourceClass._meta.fields[1:]:
            setattr(field, 'null', True)

        drop_table = "DROP TABLE IF EXISTS {final_table} CASCADE;".format(final_table=source_table_name)

        sql, refs = source_db_connection.creation.sql_create_model(SourceClass, color_style())
        add_geometry_fields = '''
            ALTER TABLE {final_table} ADD COLUMN geography_id VARCHAR;
            ALTER TABLE {final_table} ADD COLUMN wkb_geometry GEOMETRY;'''.format(final_table=source_table_name)

        sql = drop_table + sql[0] + add_geometry_fields
        for dbfield, fieldtype in extra_fields.items():
            sql += 'ALTER TABLE {final_table} ADD COLUMN {field} {type}'.format(
                final_table=source_table_name, field=dbfield, type=fieldtype)
        source_db_connection.cursor().execute(sql)


class AgScenarioLoader(SourceTableLoader):
    """
    Prepares an agriculture scenario table with built form names and geography id's, and creates a keyed
    table that will be loaded into a UF instance upon initialization
    """

    PROJECTS = ['sutter_county', 'yuba_county', 'yolo_county', 'sacramento_county', 'el_dorado_county', 'placer_county']

    def open_region_table(self, region):
        path = os.path.join(settings.ROOT_PATH, 'footprint', 'client', 'configuration',
                            settings.CLIENT, 'base', 'agriculture_base_data', region + '.dbf')
        if not os.path.exists(path):
            raise Exception(path + " does not exist")

        return dbf.Dbf(path)

    def load_project_to_source_db(self, region):
        source_db_connection = get_client_source_data_connection()
        cursor = source_db_connection.cursor()

        logger.info("Preparing base agriculture import table for " + region)
        tmp_db_table = region + '_base_agriculture_feature_tmp'
        recreate_db_table_sql = '''
          drop table if exists {table} cascade;
          create table {table} (
              geography_id VARCHAR,
              wkb_geometry GEOMETRY,
              ag_type_name VARCHAR,
              built_form_key VARCHAR
        );\n'''.format(table=tmp_db_table)
        logger.info("Running SQL: {0}".format(recreate_db_table_sql))
        cursor.execute(recreate_db_table_sql)

        try:
            source_table = self.open_region_table(region)
            insert_sql = 'INSERT INTO {table} (geography_id, ag_type_name, built_form_key) VALUES \n'.format(
            table=tmp_db_table)
            for row in source_table:
                built_form_key = 'ct__' + slugify(row['OPTYPE']).replace('-', '_')
                insert_sql += "('{geography_id}', '{ag_type_name}', '{built_form_key}'),\n".format(
                    geography_id=int(row['URBAN_ID']), ag_type_name=row['OPTYPE'], built_form_key=built_form_key
                )
            insert_sql = insert_sql[:-2] + ';'
            logger.info("Running INSERT SQL for {0} rows".format(len(source_table)))
            cursor.execute(insert_sql)
        except:
            logger.warn("No source data found for {0} Agriculture".format(region))

        #todo create join to base canvas geography table
        final_table = tmp_db_table[:-4]
        base_table = region + "_base_feature"

        self.create_empty_source_table(AgricultureFeature, final_table, source_db_connection)

        fields = map_to_dict(
            lambda field: [field.name, {'default': field.default, 'type': field.__class__, 'null': field.null}],
            AgricultureFeature._meta.fields)

        import_fields = ['wkb_geometry', 'geography_id']
        field_names = ''
        selections = ''
        fields['geography_id'] = {'default': '', 'type': '', 'null': ''}
        for f, detail in fields.items():

            if detail['type'] == DateTimeField:
                selection = 'current_timestamp'
            else:
                selection = detail['default']

            if f in import_fields:
                selection = f
            elif detail['null'] and not selection:
                continue

            field_names += "{0},\n\t\t".format(f)
            selections += "{0},\n\t\t".format(selection)
            del selection

        field_names = field_names[:-4]
        selections = selections[:-4]

        geography_join_sql = '''
           ALTER TABLE {final_table} drop column id;
           INSERT INTO {final_table} ({field_names}) (select {selections} from {base_table});

           UPDATE {final_table} a SET built_form_key = b.built_form_key from {tmp_table} b
           where a.geography_id = b.geography_id;

           DROP TABLE {tmp_table} CASCADE;'''.format(
            field_names=field_names, selections=selections,
            base_table=base_table, final_table=final_table, tmp_table=tmp_db_table)

        logger.info(geography_join_sql)
        cursor.execute(geography_join_sql)
        cursor.execute(self.create_sample_data(region, final_table))
