
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


class WaterUpdaterTool(AnalysisTool, BuildingPerformance):
    objects = GeoInheritanceManager()

    METRICS = ['indoor', 'outdoor']

    @property
    def output_fields(self):
        return ['id', 'evapotranspiration_zone', 'pop', 'hh', 'emp', 'total_water_use', 'residential_water_use',
                       'commercial_water_use', 'residential_indoor_water_use', 'commercial_indoor_water_use',
                       'residential_outdoor_water_use', 'commercial_outdoor_water_use', 'annual_gallons_per_unit']

    class Meta(object):
        app_label = 'main'
        abstract = False

    def update(self, **kwargs):

        logger.info("Executing Water using {0}".format(self.config_entity))

        self.run_water_calculations(**kwargs)

        logger.info("Done executing Water")
        logger.info("Executed Water using {0}".format(self.config_entity))

    def run_future_water_calculations(self, **kwargs):

        self.base_year = self.config_entity.scenario.project.base_year
        self.future_year = self.config_entity.scenario.year
        self.increment = self.future_year - self.base_year
        self.annualize_efficiencies()

        features = self.end_state_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))

        annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
            DbEntityKey.BASE_CANVAS, DbEntityKey.CLIMATE_ZONES])

        water_output_list = []

        options = dict(
            water_result_table=self.water_class.db_entity_key,
            water_schema=parse_schema_and_table(self.water_class._meta.db_table)[0],
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
            if feature.climate_zones:
                climate_zone_feature = self.climate_zone_class.objects.get(id=feature.climate_zones)
            else:
                logger.warn("No Climate Zone intersection for feature id {0} or check geography relation table".format(feature.id))
                continue

            self.feature_dict = dict(
                id=feature.id,
                pop=float(feature.pop),
                hh=float(feature.hh),
                emp=float(feature.emp),

                evapotranspiration_zone=climate_zone_feature.evapotranspiration_zone.zone,
                annual_evapotranspiration=float(climate_zone_feature.evapotranspiration_zone.annual_evapotranspiration),
            )

            for use in 'residential', 'commercial':
                key = "{use}_irrigated_sqft".format(use=use)
                self.feature_dict.update({
                    key + "_redev": self.redev_units(key, feature, base_feature),
                    key + "_new": self.new_units(key, feature, base_feature),
                    key + "_base": float(getattr(base_feature, key))
                })

            future_residential_factor = feature.hh / feature.du * feature.pop / feature.hh if feature.hh > 0 else 0
            base_residential_factor = base_feature.hh / base_feature.du * base_feature.pop / base_feature.hh if base_feature.hh else 0

            for key in self.RESIDENTIAL_TYPES:
                self.feature_dict.update({
                    key + "_redev": self.redev_units(key, feature, base_feature) * float(base_residential_factor),
                    key + "_new": self.new_units(key, feature, base_feature) * float(future_residential_factor),
                    key + "_base": float(getattr(base_feature, key)) * float(base_residential_factor)
                })

            for key in self.COMMERCIAL_TYPES:
                self.feature_dict.update({
                    key + "_redev": self.redev_units("emp_" + key, feature, base_feature) * float(base_residential_factor),
                    key + "_new": self.new_units("emp_" + key, feature, base_feature) * float(future_residential_factor),
                    key + "_base": float(getattr(base_feature, "emp_" +key)) * float(base_residential_factor)
                })

            self.calculate_future_water()
            self.calculate_visualized_field()

            output_row = map(lambda key: self.result_dict.get(key), self.output_fields)
            water_output_list.append(output_row)
            i += 1

        return water_output_list, options

    def run_base_water_calculations(self):

        features = self.base_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))

        annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
            DbEntityKey.CLIMATE_ZONES])

        water_output_list = []

        options = dict(
            water_result_table=self.water_class.db_entity_key,
            water_schema=parse_schema_and_table(self.water_class._meta.db_table)[0],
            base_table=self.base_class.db_entity_key,
            base_schema=parse_schema_and_table(self.base_class._meta.db_table)[0],
        )

        for feature in annotated_features.iterator():
            self.result_dict = defaultdict(lambda: float(0))
            self.feature = feature

            if feature.climate_zones:
                climate_zone_feature = self.climate_zone_class.objects.get(id=feature.climate_zones)
            else:
                logger.warn("No Climate Zone intersection for feature id {0} or check geography relation table".format(feature.id))
                continue

            hh_factor = (feature.pop / feature.hh) * (feature.hh / feature.du) if (feature.du > 0 and feature.hh > 0) else 0

            self.feature_dict = dict(
                id=feature.id,
                pop=float(feature.pop),
                hh=float(feature.hh),
                emp=float(feature.emp),

                evapotranspiration_zone=climate_zone_feature.evapotranspiration_zone.zone,
                annual_evapotranspiration=float(climate_zone_feature.evapotranspiration_zone.annual_evapotranspiration),

                residential_irrigated_sqft=float(feature.residential_irrigated_sqft),
                commercial_irrigated_sqft=float(feature.commercial_irrigated_sqft),

                du_detsf_ll=float(feature.du_detsf_ll * hh_factor),
                du_detsf_sl=float(feature.du_detsf_sl * hh_factor),
                du_attsf=float(feature.du_attsf * hh_factor),
                du_mf=float(feature.du_mf * hh_factor),

                retail_services=float(feature.emp_retail_services),
                restaurant=float(feature.emp_restaurant),
                accommodation=float(feature.emp_accommodation),
                arts_entertainment=float(feature.emp_arts_entertainment),
                other_services=float(feature.emp_other_services),
                office_services=float(feature.emp_office_services),
                public_admin=float(feature.emp_public_admin),
                education=float(feature.emp_education),
                medical_services=float(feature.emp_medical_services),
                wholesale=float(feature.emp_wholesale),
                transport_warehousing=float(feature.emp_transport_warehousing),
                manufacturing=float(feature.emp_manufacturing),
                construction=float(feature.emp_construction),
                utilities=float(feature.emp_utilities),
                agriculture=float(feature.emp_agriculture),
                extraction=float(feature.emp_extraction),
                military=float(feature.emp_military)
            )

            self.calculate_base_water()
            self.calculate_visualized_field()
            output_row = map(lambda key: self.result_dict[key], self.output_fields)
            water_output_list.append(output_row)

        return water_output_list, options

    def calculate_visualized_field(self):
        total_units = float(self.feature.emp) + float(self.feature.pop)
        if total_units:
            self.result_dict['annual_gallons_per_unit'] = self.result_dict['total_water_use'] / total_units
        else:
            self.result_dict['annual_gallons_per_unit'] = 0

    def format_policy_inputs(self):

        self.policy_assumptions = {}

        # TODO Use the first PolicySet--this needs to be done better
        policy_set = self.config_entity.computed_policy_sets()[0].policy_by_key('water')
        get_policy = lambda key: policy_set.policy_by_key(key)

        residential_indoor_rates = {
            key+"_indoor": get_policy('residential_indoor_water_factors.' + key) for key in self.RESIDENTIAL_TYPES
        }
        commercial_indoor_rates = {
            key+"_indoor": get_policy('commercial_indoor_water_factors.' + key) for key in self.COMMERCIAL_TYPES
        }

        building_efficiency_assumptions = policy_set.get_building_efficiency_assumptions(self.METRICS)

        self.policy_assumptions.update(residential_indoor_rates)
        self.policy_assumptions.update(commercial_indoor_rates)

        self.policy_assumptions.update(building_efficiency_assumptions)

    def run_water_calculations(self, **kwargs):
        self.format_policy_inputs()

        self.water_class = self.config_entity.db_entity_feature_class(DbEntityKey.WATER)
        self.base_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
        self.climate_zone_class = self.config_entity.db_entity_feature_class(DbEntityKey.CLIMATE_ZONES)
        self.rel_table = parse_schema_and_table(self.water_class._meta.db_table)[1]
        self.rel_column = self.water_class._meta.parents.values()[0].column

        if isinstance(self.config_entity.subclassed, FutureScenario):
            self.report_progress(0.2, **kwargs)
            self.end_state_class = self.config_entity.db_entity_feature_class(DbEntityKey.END_STATE)


            water_output_list, options = self.run_future_water_calculations(**kwargs)
        else:
            self.report_progress(0.2, **kwargs)
            water_output_list, options = self.run_base_water_calculations()
            self.report_progress(0.7, **kwargs)

        self.write_water_results_to_database(options, water_output_list)

        updated = datetime.datetime.now()
        truncate_table(options['water_schema'] + '.' + self.rel_table)

        pSql = '''
        insert into {water_schema}.{rel_table} ({rel_column}, updated) select id, '{updated}' from {water_schema}.{water_result_table};'''.format(
            water_schema=options['water_schema'],
            water_result_table=options['water_result_table'],
            rel_table=self.rel_table,
            rel_column=self.rel_column,
            updated=updated)

        execute_sql(pSql)

        from footprint.main.publishing.data_import_publishing import create_and_populate_relations
        create_and_populate_relations(self.config_entity, self.config_entity.computed_db_entities(key=DbEntityKey.WATER)[0])
        self.report_progress(0.10000001, **kwargs)

    def calculate_future_water(self):

        for landuse in self.RESIDENTIAL_TYPES + self.COMMERCIAL_TYPES:
            base_use = self.apply_efficiency_policy_to_unchanged_landuse(landuse, 'indoor')
            new_use = self.apply_efficiency_policy_to_new_units(landuse, 'indoor')
            reduced_use = self.apply_efficiency_policy_to_redevelopment(landuse, 'indoor')
            subcategory_use_total = new_use + base_use - reduced_use
            self.result_dict['{use}_indoor_water_use'.format(use=landuse)] = subcategory_use_total

        # todo look for residential efficiencies broken out by subcategory, otherwise use metacategory assumption
        for category in ['residential', 'commercial']:
            metric = 'outdoor'
            kwargs = {
                "redev_units": self.feature_dict[category + "_irrigated_sqft_redev"],
                "new_units": self.feature_dict[category + "_irrigated_sqft_new"],
                "base_units": self.feature_dict[category + "_irrigated_sqft_base"],
                "base_use_rate": self.feature_dict['annual_evapotranspiration']
            }
            base_use = self.apply_efficiency_policy_to_unchanged_landuse(category, metric, **kwargs)
            new_use = self.apply_efficiency_policy_to_new_units(category, metric, **kwargs)
            reduced_use = self.apply_efficiency_policy_to_redevelopment(category, metric, **kwargs)
            subcategory_use_total = new_use + base_use - reduced_use
            self.result_dict['{use}_outdoor_water_use'.format(use=category)] = subcategory_use_total / 365

        commercial_indoor_use = sum(
            [self.result_dict['{use}_indoor_water_use'.format(use=use)] for use in self.COMMERCIAL_TYPES])
        residential_indoor_use = sum(
            [self.result_dict['{use}_indoor_water_use'.format(use=use)] for use in self.RESIDENTIAL_TYPES])

        total_indoor_use = commercial_indoor_use + residential_indoor_use
        residential_use = residential_indoor_use + self.result_dict['residential_outdoor_water_use']
        commercial_use = commercial_indoor_use + self.result_dict['commercial_outdoor_water_use']
        total_outdoor_use = self.result_dict['residential_outdoor_water_use'] + self.result_dict['commercial_outdoor_water_use']

        self.result_dict.update({
            'outdoor_water_use': total_outdoor_use,
            'indoor_water_use': total_indoor_use,
            'residential_water_use': residential_use,
            'residential_indoor_water_use': residential_indoor_use,

            'commercial_water_use': commercial_use,
            'commercial_indoor_water_use': commercial_indoor_use,
            'total_water_use': commercial_use + residential_use
        })

        try:
            assert abs(residential_use + commercial_use - total_outdoor_use - total_indoor_use) < .1
        except:
            pass
        self.result_dict.update(self.feature_dict)

    def calculate_base_water(self):

        types = self.RESIDENTIAL_TYPES + self.COMMERCIAL_TYPES
        self.result_dict = defaultdict(lambda: float(0))
        self.result_dict.update(self.feature_dict)

        for water_type in self.METRICS:

            if 'outdoor' in water_type:
                self.result_dict['residential_{0}_water_use'.format(water_type)] = self.result_dict['residential_irrigated_sqft'] * \
                   self.result_dict['annual_evapotranspiration'] / 365
                self.result_dict['commercial_{0}_water_use'.format(water_type)] = self.result_dict['commercial_irrigated_sqft'] * \
                   self.result_dict['annual_evapotranspiration'] / 365
            else:
                for type in types:
                    water_use = self.result_dict[type] * self.policy_assumptions['{0}_{1}'.format(type, water_type)]
                    self.result_dict['{0}_{1}_water_use'.format(type, water_type)] = water_use

                    if type in self.RESIDENTIAL_TYPES:
                        self.result_dict['residential_{0}_water_use'.format(water_type)] += water_use

                    if type in self.COMMERCIAL_TYPES:
                        self.result_dict['commercial_{0}_water_use'.format(water_type)] += water_use

                self.result_dict['residential_water_use'] += self.result_dict['residential_{0}_water_use'.format(water_type)]
                self.result_dict['commercial_water_use'] += self.result_dict['commercial_{0}_water_use'.format(water_type)]

            self.result_dict['total_{0}_water_use'.format(water_type)] = \
                self.result_dict['residential_{0}_water_use'.format(water_type)] + \
                self.result_dict['commercial_{0}_water_use'.format(water_type)]

        self.result_dict['residential_water_use'] = self.result_dict['residential_indoor_water_use'] + \
             self.result_dict['residential_outdoor_water_use']

        self.result_dict['commercial_water_use'] = self.result_dict['commercial_indoor_water_use'] + \
             self.result_dict['commercial_outdoor_water_use']

        self.result_dict['total_outdoor_water_use'] = \
            self.result_dict['residential_outdoor_water_use'] + \
            self.result_dict['commercial_outdoor_water_use']

        self.result_dict['total_water_use'] = self.result_dict['residential_water_use'] + self.result_dict['commercial_water_use']


    def write_water_results_to_database(self, options, water_output_list):

        drop_table('{water_schema}.{water_result_table}'.format(**options))

        attribute_list = filter(lambda x: x not in ['id', 'evapotranspiration_zone'], self.output_fields)
        output_field_syntax = 'id int, ' + 'evapotranspiration_zone int, ' + create_sql_calculations(attribute_list, '{0} numeric(15, 4)')

        pSql = '''
        create table {water_schema}.{water_result_table} ({fields});'''.format(fields=output_field_syntax, **options)
        execute_sql(pSql)

        output_textfile = StringIO("")

        for row in water_output_list:
            stringrow = []
            for item in row:
                if isinstance(item, int):
                    stringrow.append(str(item))
                else:
                    stringrow.append(str(round(item, 4)))
            output_textfile.write("\t".join(stringrow,) + "\n")

        output_textfile.seek(os.SEEK_SET)
        #copy text file output back into Postgres
        copy_from_text_to_db(output_textfile, '{water_schema}.{water_result_table}'.format(**options))
        output_textfile.close()
        ##---------------------------
        pSql = '''alter table {water_schema}.{water_result_table} add column wkb_geometry geometry (GEOMETRY, 4326);
        '''.format(**options)
        execute_sql(pSql)

        pSql = '''update {water_schema}.{water_result_table} b set
                    wkb_geometry = st_setSRID(a.wkb_geometry, 4326)
                    from (select id, wkb_geometry from {base_schema}.{base_table}) a
                    where cast(a.id as int) = cast(b.id as int);
        '''.format(**options)

        execute_sql(pSql)

        add_geom_idx(options['water_schema'], options['water_result_table'],  'wkb_geometry')
        add_primary_key(options['water_schema'], options['water_result_table'], 'id')
        add_attribute_idx(options['water_schema'], options['water_result_table'], 'annual_gallons_per_unit')
