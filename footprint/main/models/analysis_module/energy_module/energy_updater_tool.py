
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
from itertools import product
import os
import time
import datetime
from StringIO import StringIO
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis.building_performance import BuildingPerformance
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.config.scenario import FutureScenario
import logging
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.utils.query_parsing import annotated_related_feature_class_pk_via_geographies
from footprint.main.utils.uf_toolbox import copy_from_text_to_db, execute_sql, drop_table, create_sql_calculations, \
    add_geom_idx, add_primary_key, add_attribute_idx, truncate_table
from footprint.main.utils.utils import parse_schema_and_table

__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)


class EnergyUpdaterTool(AnalysisTool, BuildingPerformance):

    objects = GeoInheritanceManager()
    COMMERCIAL_TYPES = [
        'retail_services', 'restaurant', 'accommodation', 'other_services', 'office_services', 'education',
        'public_admin', 'medical_services', 'wholesale', 'transport_warehousing'
    ]
    METRICS = ['gas', 'electricity']

    thm_to_btu = lambda self, x: x * 99976
    kwh_to_btu = lambda self, x: x * 3412

    @property
    def use_breakout_fields(self):
        return ["{use}_{type}_use".format(use=use, type=e_type) for use, e_type
                in product(self.all_types_and_categories, self.METRICS)]

    @property
    def output_fields(self):
        return ['id', 'title24_zone', 'fcz_zone', 'total_commercial_sqft', 'emp', 'hh', 'total_gas_use',
                'total_electricity_use', 'annual_million_btus_per_unit'] + self.use_breakout_fields

    class Meta(object):
        app_label = 'main'
        abstract = False

    def update(self, **kwargs):

        logger.info("Executing Energy using {0}".format(self.config_entity))

        self.run_analysis(**kwargs)

        logger.info("Done executing Energy")
        logger.info("Executed Energy using {0}".format(self.config_entity))

    def run_analysis(self, **kwargs):

        start_time = time.time()
        self.report_progress(0.1, **kwargs)

        self.climate_zone_class = self.config_entity.db_entity_feature_class(DbEntityKey.CLIMATE_ZONES)
        self.energy_class = self.config_entity.db_entity_feature_class(DbEntityKey.ENERGY)
        self.base_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
        self.rel_table = parse_schema_and_table(self.energy_class._meta.db_table)[1]
        self.rel_column = self.energy_class._meta.parents.values()[0].column

        options = dict(
            energy_result_table=self.energy_class.db_entity_key,
            energy_schema=parse_schema_and_table(self.energy_class._meta.db_table)[0],
            base_table=self.base_class.db_entity_key,
            base_schema=parse_schema_and_table(self.base_class._meta.db_table)[0],
        )
        logger.info("Running Energy Updater Tool with options %s" % options)

        if isinstance(self.config_entity.subclassed, FutureScenario):
            self.end_state_class = self.config_entity.db_entity_feature_class(DbEntityKey.END_STATE)
            logger.info("Running Future Calculations")
            energy_output_list, options = self.run_future_calculations(options, **kwargs)
        else:
            logger.info("Running Base Calculations")
            energy_output_list, options = self.run_base_calculations(options, **kwargs)

        logger.info("Writing to feature table {energy_schema}.{energy_result_table}".format(**options))
        self.write_results_to_database(options, energy_output_list)


        logger.info("Writing to relative table {energy_schema}.{rel_table}".format(
            energy_schema=options['energy_schema'],
            rel_table=self.rel_table))

        updated = datetime.datetime.now()
        truncate_table(options['energy_schema'] + '.' + self.rel_table)

        pSql = '''
        insert into {energy_schema}.{rel_table} ({rel_column}, updated)
        select id, '{updated}' from {energy_schema}.{energy_result_table};'''.format(
            energy_schema=options['energy_schema'],
            energy_result_table=options['energy_result_table'],
            rel_table=self.rel_table,
            rel_column=self.rel_column,
            updated=updated)

        execute_sql(pSql)

        from footprint.main.publishing.data_import_publishing import create_and_populate_relations
        create_and_populate_relations(self.config_entity, self.config_entity.computed_db_entities(key=DbEntityKey.ENERGY)[0])
        self.report_progress(0.2, **kwargs)

        logger.info('Finished: ' + str(time.time() - start_time))

    def collect_climate_rates(self, feature):

        climate_zone_feature = self.climate_zone_class.objects.get(id=feature.climate_zones)

        t24z = climate_zone_feature.title_24_zone
        fcz = climate_zone_feature.forecasting_climate_zone

        title_24_fields = ['_'.join(p) for p in product(self.RESIDENTIAL_TYPES, self.METRICS)]
        title_24_rates = {field: float(getattr(t24z, field)) for field in title_24_fields}

        forcasting_zone_fields = ['_'.join(p) for p in product(self.COMMERCIAL_TYPES, self.METRICS)]
        forcasting_zone_rates = {field: float(getattr(fcz, field)) for field in forcasting_zone_fields}

        climate_input = dict(title24_zone=int(t24z.zone), fcz_zone=int(fcz.zone))
        climate_input.update(title_24_rates)
        climate_input.update(forcasting_zone_rates)

        return climate_input

    def get_feature_input(self, feature):
        return dict(
            id=feature.id,
            hh=feature.hh,
            emp=feature.emp,
            total_commercial_sqft=sum([float(getattr(feature, "bldg_sqft_" + category)) for category in self.COMMERCIAL_TYPES]),
        )

    def run_future_calculations(self, options, **kwargs):
        self.features = self.end_state_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))
        # TODO Use the first PolicySet--this needs to be done better
        self.policy_set = self.config_entity.computed_policy_sets()[0].policy_by_key('energy')
        self.policy_assumptions = self.policy_set.get_building_efficiency_assumptions(self.METRICS)
        self.base_year = self.config_entity.scenario.project.base_year
        self.future_year = self.config_entity.scenario.year
        self.increment = self.future_year - self.base_year
        self.annualize_efficiencies()

        annotated_features = annotated_related_feature_class_pk_via_geographies(self.features, self.config_entity, [
            DbEntityKey.BASE_CANVAS, DbEntityKey.CLIMATE_ZONES])

        energy_output_list = []

        approx_fifth = int(annotated_features.count() / 14 - 1) if annotated_features.count() > 30 else 1
        i = 1
        for feature in annotated_features.iterator():
            self.feature = feature
            self.result_dict = defaultdict(lambda: float(0))

            if i % approx_fifth == 0:
                self.report_progress(0.05, **kwargs)
            self.base_canvas = self.base_class.objects.get(id=feature.base_canvas)
            try:
                climate_rates = self.collect_climate_rates(feature)
            except ObjectDoesNotExist:
                continue


            self.future_occupancy_rate = float(self.feature.hh / self.feature.du if self.feature.du else 0)
            self.base_occupancy_rate = float(self.base_canvas.hh / self.base_canvas.du if self.base_canvas.du else 0)
            # self.energy_input = self.get_energy_input(feature)
            self.feature_dict = self.get_feature_input(feature)
            for category in self.COMMERCIAL_TYPES:
                self.feature_dict.update({
                    category + "_redev": self.redev_units('bldg_sqft_' + category, self.feature, self.base_canvas),
                    category + "_new": self.new_units('bldg_sqft_' + category, self.feature, self.base_canvas),
                    category + "_base": float(getattr(self.base_canvas, 'bldg_sqft_' + category))
                })

            for category in self.RESIDENTIAL_TYPES:
                self.feature_dict.update({
                    category + "_redev": self.redev_units(category, self.feature, self.base_canvas) * self.future_occupancy_rate,
                    category + "_new": self.new_units(category, self.feature, self.base_canvas) * self.future_occupancy_rate,
                    category + "_base": float(getattr(self.base_canvas, category)) * self.base_occupancy_rate
                })

            self.policy_assumptions.update(climate_rates)
            self.calculate_future_energy()
            self.calculate_visualized_field()

            self.result_dict.update(self.feature_dict)
            self.result_dict.update(self.policy_assumptions)

            output_row = map(lambda key: self.result_dict[key], self.output_fields)
            energy_output_list.append(output_row)
            i += 1

        return energy_output_list, options

    def run_base_calculations(self, options, **kwargs):
        features = self.base_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))

        annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
            DbEntityKey.CLIMATE_ZONES])

        energy_output_list = []

        approx_fifth = int(annotated_features.count() / 14 - 1) if annotated_features.count() > 30 else 1

        i = 1
        for feature in annotated_features.iterator():
            self.result_dict = defaultdict(lambda: float(0))
            self.feature = feature

            if i % approx_fifth == 0:
                self.report_progress(0.05, **kwargs)
            try:
                climate_rates = self.collect_climate_rates(feature)
            except ObjectDoesNotExist:
                continue

            occupancy_rate = self.feature.hh / self.feature.du if self.feature.du else 0
            residential_units = {
                field: float(getattr(feature, field) * occupancy_rate) for field in self.RESIDENTIAL_TYPES
            }
            commercial_bldg_sqft = {
                field: float(getattr(feature, 'bldg_sqft_'+field)) for field in self.COMMERCIAL_TYPES
            }

            self.feature_dict = self.get_feature_input(feature)

            self.feature_dict.update(climate_rates)
            self.feature_dict.update(residential_units)
            self.feature_dict.update(commercial_bldg_sqft)

            self.calculate_base_use()
            self.calculate_visualized_field()

            output_row = map(lambda key: self.result_dict[key], self.output_fields)
            energy_output_list.append(output_row)
            i += 1

        self.calculate_visualized_field()
        return energy_output_list, options

    def calculate_future_energy(self):

        all_types = self.RESIDENTIAL_TYPES + self.COMMERCIAL_TYPES

        # we have three categories of units to deal with - redev, new development, and base
        for landuse, metric in product(all_types, self.METRICS):
            fmt = dict(use=landuse, metric=metric)

            base_use = self.apply_efficiency_policy_to_unchanged_landuse(landuse, metric)
            new_use = self.apply_efficiency_policy_to_new_units(landuse, metric)
            reduced_use = self.apply_efficiency_policy_to_redevelopment(landuse, metric)

            self.result_dict.update({
                "{use}_base_{metric}_use".format(**fmt): base_use,
                "{use}_new_{metric}_use".format(**fmt): new_use,
                "{use}_redev_{metric}_use".format(**fmt): reduced_use,
                '{use}_{metric}_use'.format(**fmt): new_use + base_use - reduced_use,
            })

        for metric in self.METRICS:
            commercial_use = sum(
                [self.result_dict['{use}_{metric}_use'.format(use=use, metric=metric)] for use in self.COMMERCIAL_TYPES]
            )
            residential_use = sum(
                [self.result_dict['{use}_{metric}_use'.format(use=use, metric=metric)] for use in self.RESIDENTIAL_TYPES]
            )

            self.result_dict.update({
                'residential_{metric}_use'.format(metric=metric): residential_use,
                'commercial_{metric}_use'.format(metric=metric): commercial_use,
                'total_{metric}_use'.format(metric=metric): commercial_use + residential_use,
            })

    def calculate_visualized_field(self):

        electric_btus = self.kwh_to_btu(self.result_dict['total_electricity_use'])
        gas_btus = self.thm_to_btu(self.result_dict['total_gas_use'])

        total_units = float(self.feature.emp) + float(self.feature.pop)

        if total_units:
            self.result_dict['annual_million_btus_per_unit'] = (electric_btus + gas_btus) / (total_units * 1000000)
        else:
            self.result_dict['annual_million_btus_per_unit'] = 0

        if self.result_dict['annual_million_btus_per_unit'] >= 10000000000:
            self.result_dict['annual_million_btus_per_unit'] = 9999999999

    def calculate_base_use(self):
        self.result_dict.update(self.feature_dict)
        for energy_type in self.METRICS:

            types = self.RESIDENTIAL_TYPES + self.COMMERCIAL_TYPES

            for use in types:
                subuse_units = self.result_dict[use]
                if not subuse_units:
                    continue
                subuse_rate = self.result_dict['{0}_{1}'.format(use, energy_type)]
                subuse_consumption = subuse_units * subuse_rate
                self.result_dict['{0}_{1}_use'.format(use, energy_type)] += subuse_consumption

                if use in self.RESIDENTIAL_TYPES:
                    self.result_dict['residential_{0}_use'.format(energy_type)] += subuse_consumption

                elif use in self.COMMERCIAL_TYPES:
                    self.result_dict['commercial_{0}_use'.format(energy_type)] += subuse_consumption

            self.result_dict['total_{0}_use'.format(energy_type)] = \
                self.result_dict['residential_{0}_use'.format(energy_type)] + \
                self.result_dict['commercial_{0}_use'.format(energy_type)]


    def write_results_to_database(self, options, energy_output_list):

        drop_table('{energy_schema}.{energy_result_table}'.format(**options))

        attribute_list = filter(lambda x: x not in ['id', 'title24_zone', 'fcz_zone'], self.output_fields)

        output_field_syntax = 'id int, title24_zone int, fcz_zone int, ' + create_sql_calculations(attribute_list, '{0} numeric(14, 4)')

        pSql = '''
        create table {energy_schema}.{energy_result_table} ({output_field_syntax});'''.format(output_field_syntax=output_field_syntax, **options)
        execute_sql(pSql)

        output_textfile = StringIO("")

        for row in energy_output_list:
            stringrow = []
            for item in row:
                if isinstance(item, int):
                    stringrow.append(str(item))
                else:
                    stringrow.append(str(round(item, 4)))
            output_textfile.write("\t".join(stringrow) + "\n")

        output_textfile.seek(os.SEEK_SET)
        #copy text file output back into Postgres
        copy_from_text_to_db(output_textfile, '{energy_schema}.{energy_result_table}'.format(**options))
        output_textfile.close()

        pSql = '''alter table {energy_schema}.{energy_result_table} add column wkb_geometry geometry (GEOMETRY, 4326);'''.format(**options)
        execute_sql(pSql)

        pSql = '''update {energy_schema}.{energy_result_table} b set
                    wkb_geometry = st_setSRID(a.wkb_geometry, 4326)
                    from (select id, wkb_geometry from {base_schema}.{base_table}) a
                    where cast(a.id as int) = cast(b.id as int);
        '''.format(**options)

        execute_sql(pSql)

        add_geom_idx(options['energy_schema'], options['energy_result_table'], 'wkb_geometry')
        add_primary_key(options['energy_schema'], options['energy_result_table'],  'id')
        add_attribute_idx(options['energy_schema'], options['energy_result_table'],  'annual_million_btus_per_unit')
