
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

from collections import defaultdict
import os
import datetime
import random
from StringIO import StringIO
from django.db.models import Q
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis.building_performance import BuildingPerformance
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool

from footprint.main.models.config.scenario import FutureScenario
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey

import logging
from footprint.main.utils.query_parsing import annotated_related_feature_class_pk_via_geographies
from footprint.main.utils.uf_toolbox import drop_table, execute_sql, copy_from_text_to_db, create_sql_calculations, \
    add_geom_idx, add_primary_key, add_attribute_idx, truncate_table
from footprint.main.utils.utils import parse_schema_and_table


__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


class SwmmUpdaterTool(AnalysisTool, BuildingPerformance):
    objects = GeoInheritanceManager()

    @property
    def output_fields(self):
        return ['id', 'total_swmm_runoff']

    class Meta(object):
        app_label = 'main'
        abstract = False

    def update(self, **kwargs):

        logger.info("Executing SWMM using {0}".format(self.config_entity))

        self.run_calculations(**kwargs)

        logger.info("Done executing SWMM")
        logger.info("Executed SWMM using {0}".format(self.config_entity))

    def run_future_water_calculations(self, **kwargs):

        self.base_year = self.config_entity.scenario.project.base_year
        self.future_year = self.config_entity.scenario.year
        self.increment = self.future_year - self.base_year

        features = self.end_state_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))

        annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
            DbEntityKey.BASE_CANVAS, DbEntityKey.CLIMATE_ZONES])

        output_list = []

        options = dict(
            result_table=self.klass.db_entity_key,
            the_schema=parse_schema_and_table(self.klass._meta.db_table)[0],
            base_table=self.base_class.db_entity_key,
            base_schema=parse_schema_and_table(self.base_class._meta.db_table)[0],
        )
        approx_fifth = int(annotated_features.count() / 14 - 1) if annotated_features.count() > 30 else 1
        i = 1
        for feature in annotated_features.iterator():
            self.feature = feature
            self.result_dict = defaultdict(lambda: float(0))

            if i % approx_fifth == 0:
                self.report_progress(0.05, **kwargs)

            base_feature = self.base_class.objects.get(id=feature.base_canvas)

            self.feature_dict = dict(
                id=feature.id,
                pop=float(feature.pop),
                hh=float(feature.hh),
                emp=float(feature.emp),
            )

            self.calculate_future_water()
            self.calculate_visualized_field()

            output_row = map(lambda key: self.result_dict.get(key), self.output_fields)
            output_list.append(output_row)
            i += 1

        return output_list, options

    def run_base_calculations(self):

        features = self.base_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))

        annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
            DbEntityKey.CLIMATE_ZONES])

        output_list = []

        options = dict(
            result_table=self.klass.db_entity_key,
            the_schema=parse_schema_and_table(self.klass._meta.db_table)[0],
            base_table=self.base_class.db_entity_key,
            base_schema=parse_schema_and_table(self.base_class._meta.db_table)[0],
        )

        for feature in annotated_features.iterator():
            self.result_dict = defaultdict(lambda: float(0))
            self.feature = feature

            self.feature_dict = dict(
                id=feature.id,
                pop=float(feature.pop),
                hh=float(feature.hh),
                emp=float(feature.emp),
            )

            self.calculate_base_water()
            self.calculate_visualized_field()
            output_row = map(lambda key: self.result_dict[key], self.output_fields)
            output_list.append(output_row)

        return output_list, options

    def calculate_visualized_field(self):
        total_units = float(self.feature.emp) + float(self.feature.pop)
        if total_units:
            self.result_dict['total_swmm_runoff'] = self.result_dict['total_swmm_runoff'] / total_units
        else:
            self.result_dict['total_swmm_runoff'] = 0

    def run_calculations(self, **kwargs):
        self.klass = self.config_entity.db_entity_feature_class(DbEntityKey.SWMM)
        self.base_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
        self.climate_zone_class = self.config_entity.db_entity_feature_class(DbEntityKey.CLIMATE_ZONES)
        self.rel_table = parse_schema_and_table(self.klass._meta.db_table)[1]
        self.rel_column = self.klass._meta.parents.values()[0].column

        self.report_progress(0.2, **kwargs)
        if isinstance(self.config_entity.subclassed, FutureScenario):
            self.end_state_class = self.config_entity.db_entity_feature_class(DbEntityKey.END_STATE)
            output_list, options = self.run_future_water_calculations(**kwargs)
        else:
            output_list, options = self.run_base_calculations()
            self.report_progress(0.7, **kwargs)

        self.write_results_to_database(options, output_list)

        updated = datetime.datetime.now()
        truncate_table(options['the_schema'] + '.' + self.rel_table)

        pSql = '''
        insert into {the_schema}.{rel_table} ({rel_column}, updated) select id, '{updated}' from {the_schema}.{result_table};'''.format(
            the_schema=options['the_schema'],
            result_table=options['result_table'],
            rel_table=self.rel_table,
            rel_column=self.rel_column,
            updated=updated)

        execute_sql(pSql)

        from footprint.main.publishing.data_import_publishing import create_and_populate_relations
        create_and_populate_relations(self.config_entity, self.config_entity.computed_db_entities(key=DbEntityKey.SWMM)[0])
        self.report_progress(0.10000001, **kwargs)

    def calculate_future_water(self):

        self.result_dict.update({
            'total_swmm_runoff': 999999,
        })

        self.result_dict.update(self.feature_dict)

    def calculate_base_water(self):

        self.result_dict = defaultdict(lambda: float(0))

        self.result_dict.update({
            'total_swmm_runoff': 123456,
        })

        self.result_dict.update(self.feature_dict)

    def write_results_to_database(self, options, output_list):

        drop_table('{the_schema}.{result_table}'.format(**options))

        attribute_list = filter(lambda x: x not in ['id'], self.output_fields)
        output_field_syntax = 'id int, ' + create_sql_calculations(attribute_list, '{0} numeric(15, 4)')

        pSql = '''
        create table {the_schema}.{result_table} ({fields});'''.format(fields=output_field_syntax, **options)
        execute_sql(pSql)

        output_textfile = StringIO("")

        for row in output_list:
            stringrow = []
            for item in row:
                if isinstance(item, int):
                    stringrow.append(str(item))
                else:
                    stringrow.append(str(round(item, 4)))
            output_textfile.write("\t".join(stringrow,) + "\n")

        output_textfile.seek(os.SEEK_SET)
        #copy text file output back into Postgres
        copy_from_text_to_db(output_textfile, '{the_schema}.{result_table}'.format(**options))
        output_textfile.close()
        ##---------------------------
        pSql = '''alter table {the_schema}.{result_table} add column wkb_geometry geometry (GEOMETRY, 4326);
        '''.format(**options)
        execute_sql(pSql)

        pSql = '''update {the_schema}.{result_table} b set
                    wkb_geometry = st_setSRID(a.wkb_geometry, 4326)
                    from (select id, wkb_geometry from {base_schema}.{base_table}) a
                    where cast(a.id as int) = cast(b.id as int);
        '''.format(**options)

        execute_sql(pSql)

        add_geom_idx(options['the_schema'], options['result_table'],  'wkb_geometry')
        add_primary_key(options['the_schema'], options['result_table'], 'id')
        add_attribute_idx(options['the_schema'], options['result_table'], 'total_swmm_runoff')
