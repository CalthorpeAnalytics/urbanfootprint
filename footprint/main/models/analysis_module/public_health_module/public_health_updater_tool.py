
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

import csv
import glob
import logging
from StringIO import StringIO
from math import exp, log

import os
import re
from django.db import models
from django.db.models import Q

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.analysis_module.public_health_module.public_health_preprocesses import \
    populate_public_health_grid_relation_table, populate_grid_census_rate_attributes, run_distance_variables_processes, \
    run_aggregate_within_distance_processes, run_aggregate_within_variable_distance_processes, \
    populate_transformations_and_indices
from footprint.main.models.config.scenario import FutureScenario
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.utils.uf_toolbox import drop_table, execute_sql, copy_from_text_to_db, add_geom_idx, add_primary_key, \
    create_sql_calculations, report_sql_values, truncate_table, flatten
from footprint.main.utils.utils import parse_schema_and_table
from footprint.utils.websockets import send_message_to_client

__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)
UD4H_MODEL_PATH = "/srv/calthorpe/urbanfootprint/footprint/main/models/analysis_module/public_health_module/ud4h/"

class PublicHealthOutcomeAnalysis(models.Model):
    """
    A model that describes a csv and the necessary information on how to handle it
    """
    transformations = {
        'binary': lambda value, duan: exp(value) / (1 + exp(value)),
        'linear': lambda value, duan: value,
        'linear/log': lambda value, duan: exp(value) * duan,
        'poisson': lambda value, duan: exp(value),
    }
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=5)
    csv_path = models.CharField(max_length=200, null=False)

    group = models.IntegerField()
    type = models.CharField(max_length=15)  # choices=['binary', 'linear_log', 'poisson', 'linear'])
    duan = models.FloatField(default=1)
    age_group = models.CharField(max_length=10)  # choices=['children', 'teens', 'adult', 'seniors'])
    income_group = models.CharField(max_length=10)  # choices=['low', 'middle', 'high', 'all'])

    @property
    def outcome(self):
        base = os.path.basename(self.csv_path)
        return os.path.splitext(base)[0]

    @property
    def key_prefix(self):
        age_group = 'adult' if self.age_group == 'adults' else self.age_group
        return "{0}_{1}_".format(age_group, self.income_group)

    model_dict = None
    intercept = None
    attribute_transformation = None

    def load_model_dict(self):
        with open(self.csv_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            #skip the header row
            next(reader, None)

            intercept = next(reader, None)
            self.intercept = float(intercept[1])

            self.model_dict = {
                var: float(est) for var, est, stdev, tval, absz in reader
            }

        for var, est in self.model_dict.iteritems():
            # UD4H provides csvs with generalized input names - here we make them specific to the age and income group
            if var in ["walk_tr_any", "walk_any", "pa60_daysperweek", "obese", "rec_pa",
                       "vig_pa", "BMIPCT", "BMI_log", "mvpa_METS_log"]:
                new_key = "{age}_{income}_{var}".format(age=self.age_group, income=self.income_group, var=var.lower())
                self.model_dict[new_key] = est
                self.model_dict.pop(var)

            if var in ['pop_age', 'age']:
                new_key = "{var}_{age}".format(var=var, age=self.age_group)
                self.model_dict[new_key] = est
                self.model_dict.pop(var)

            if var in ['disabled1', 'disabled2']:
                new_key = "{source}_{var}_{age}".format(source=self.source, var=var, age=self.age_group)
                self.model_dict[new_key] = est
                self.model_dict.pop(var)


        self.attribute_transformations = {
            var: float(transforms[self.age_group][self.income_group])
            for var, transforms in read_UD4H_attr_transforms().items()
        }

        self.attribute_minimum = {
            var: float(transforms['minimum'])
            for var, transforms in read_UD4H_attr_transforms().items()
        }
        self.attribute_maximum = {
            var: float(transforms['maximum'])
            for var, transforms in read_UD4H_attr_transforms().items()
        }

    def run_csv_model(self, feature_dict):
        if not self.model_dict:
            self.load_model_dict()

        result = self.intercept

        for var, est in self.model_dict.items():

            if 'disabled' in var:
                feature = feature_dict[var[5:100]]
                var = var[0:14]
            else:
                feature = feature_dict[var]

            if self.attribute_minimum.get(var) and feature * self.attribute_transformations.get(var, 1) < self.attribute_minimum.get(var):
                result = result + (self.attribute_minimum.get(var) * est)
            elif self.attribute_maximum.get(var) and feature * self.attribute_transformations.get(var, 1) > self.attribute_maximum.get(var):
                result = result + (self.attribute_maximum.get(var) * est)
            else:
                result = result + (feature * self.attribute_transformations.get(var, 1) * est)

        transformed_result = self.transformations[self.type](result, self.duan)

        return transformed_result

    class Meta(object):
        app_label = 'main'
        abstract = False


class PublicHealthUpdaterTool(AnalysisTool):

    objects = GeoInheritanceManager()
    # draft of methods for public health analysis

    public_health_model_groups = {1: None, 2: None, 3: None, 4: None}

    outcome_fields = ['id', 'hh', 'pop', 'pop_adult', 'pop_adult_high', 'pop_adult_med', 'pop_adult_low', 'pop_senior',
                      'pop_teen', 'pop_children', 'adult_all_walk_minutes', 'adult_all_bike_minutes',
                      'adult_all_auto_minutes',  'adult_all_rec_pa_minutes', 'adult_all_walk_tr_minutes',
                      'adult_all_walk_le_minutes',   'adult_all_mod_pa_minutes', 'adult_all_vig_pa_minutes',
                      'adult_all_bmi', 'adult_all_overweight',
                     'adult_all_obese', 'adult_all_high_bp', 'adult_all_heart_dis', 'adult_all_dia_type2',
                     'adult_all_gh_poor', 'adult_low_walk_minutes', 'adult_low_bike_minutes', 'adult_low_auto_minutes',
                     'adult_low_rec_pa_minutes', 'adult_low_walk_tr_minutes', 'adult_low_walk_le_minutes',
                     'adult_low_mod_pa_minutes', 'adult_low_vig_pa_minutes', 'adult_low_bmi', 'adult_low_overweight',
                     'adult_low_obese', 'adult_low_high_bp', 'adult_low_heart_dis', 'adult_low_dia_type2',
                     'adult_low_gh_poor', 'adult_med_walk_minutes', 'adult_med_bike_minutes', 'adult_med_auto_minutes',
                     'adult_med_rec_pa_minutes', 'adult_med_walk_tr_minutes', 'adult_med_walk_le_minutes',
                     'adult_med_mod_pa_minutes', 'adult_med_vig_pa_minutes', 'adult_med_bmi', 'adult_med_overweight',
                     'adult_med_obese', 'adult_med_high_bp', 'adult_med_heart_dis', 'adult_med_dia_type2',
                     'adult_med_gh_poor', 'adult_high_walk_minutes', 'adult_high_bike_minutes',
                     'adult_high_auto_minutes', 'adult_high_rec_pa_minutes', 'adult_high_walk_tr_minutes',
                     'adult_high_walk_le_minutes', 'adult_high_mod_pa_minutes', 'adult_high_vig_pa_minutes',
                     'adult_high_bmi', 'adult_high_overweight', 'adult_high_obese', 'adult_high_high_bp',
                     'adult_high_heart_dis', 'adult_high_dia_type2', 'adult_high_gh_poor', 'seniors_all_walk_minutes',
                     'seniors_all_auto_minutes', 'seniors_all_rec_pa_minutes', 'seniors_all_walk_tr_minutes',
                     'seniors_all_walk_le_minutes', 'seniors_all_mod_pa_minutes', 'seniors_all_vig_pa_minutes',
                     'seniors_all_bmi', 'seniors_all_overweight', 'seniors_all_obese', 'seniors_all_high_bp',
                     'seniors_all_heart_dis', 'seniors_all_dia_type2', 'seniors_all_gh_poor', 'teens_all_walk_minutes',
                     'teens_all_auto_minutes', 'teens_all_rec_pa_minutes', 'teens_all_pa60_daysperweek',
                     'teens_all_walkfrom_any', 'teens_all_bmipct', 'teens_all_overweight', 'teens_all_obese',
                     'teens_all_gh_poor', 'children_all_walk_minutes', 'children_all_auto_minutes',
                     'children_all_rec_pa_minutes', 'children_all_pa60_daysperweek', 'children_all_walkfrom_any',
                     'children_all_bmipct', 'children_all_overweight', 'children_all_obese', 'children_all_gh_poor']

    def public_health_progress(self, proportion, **kwargs):

        send_message_to_client(kwargs['user'].id, dict(
            event='postSavePublisherProportionCompleted',
            job_id=str(kwargs['job'].hashid),
            config_entity_id=self.config_entity.id,
            ids=[kwargs['analysis_module'].id],
            class_name='AnalysisModule',
            key=kwargs['analysis_module'].key,
            proportion=proportion)
        )
        logger.info("Progress {0}".format(proportion))

    def read_public_health_models(self):

        for group, models in self.public_health_model_groups.items():
            if not models:
                self.public_health_model_groups[group] = list(PublicHealthOutcomeAnalysis.objects.filter(group=group))

    def run_public_health_preprocesses(self, sql_config_dict, **kwargs):
        #first populates relational tables of all the geographies utilized by the PH model
        self.public_health_progress(0.1, **kwargs)
        populate_public_health_grid_relation_table(sql_config_dict)
        # #populates census variables in the grid from the census rates table
        self.public_health_progress(0.1, **kwargs)
        populate_grid_census_rate_attributes(sql_config_dict)
        # populate distance columns in the grid variables table
        self.public_health_progress(0.1, **kwargs)
        run_distance_variables_processes(sql_config_dict)
        # populate aggregations within specified distance  columns in the grid variables table
        self.public_health_progress(0.1, **kwargs)
        run_aggregate_within_distance_processes(sql_config_dict)
        #population aggregations within the variable distance of the average commute trip by taz
        self.public_health_progress(0.1, **kwargs)
        run_aggregate_within_variable_distance_processes(sql_config_dict)
        #update raw geoprocessed values with the corresponding transformations and popule calculated indices
        self.public_health_progress(0.1, **kwargs)
        populate_transformations_and_indices(sql_config_dict)

    def update(self, **kwargs):
        """
        Executes the VMT module functions
        """
        public_health_variables_class = self.config_entity.db_entity_feature_class(DbEntityKey.PH_VARIABLES)
        uf_150mgrid_class = self.config_entity.db_entity_feature_class(DbEntityKey.GRID_150M)

        census_rate_class = self.config_entity.db_entity_feature_class(DbEntityKey.CENSUS_RATES)
        grid_outcome_class = self.config_entity.db_entity_feature_class(DbEntityKey.PH_GRID_OUTCOMES)
        block_group_outcome_class = self.config_entity.db_entity_feature_class(DbEntityKey.PH_BLOCK_GROUP_OUTCOMES)
        outcome_summary_class = self.config_entity.db_entity_feature_class(DbEntityKey.PH_OUTCOMES_SUMMARY)

        if isinstance(self.config_entity.subclassed, FutureScenario):
            scenario_class = self.config_entity.db_entity_feature_class(DbEntityKey.END_STATE)
            trip_length_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT_FUTURE_TRIP_LENGTHS)
            transit_stop_class = self.config_entity.db_entity_feature_class(DbEntityKey.FUTURE_TRANSIT_STOPS)

        else:
            scenario_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
            trip_length_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT_BASE_TRIP_LENGTHS)
            transit_stop_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_TRANSIT_STOPS)

        sql_config_dict = dict(
            uf_canvas_table=scenario_class.db_entity_key,
            uf_canvas_schema=parse_schema_and_table(scenario_class._meta.db_table)[0],
            public_health_variables_table=public_health_variables_class.db_entity_key,
            public_health_variables_schema=parse_schema_and_table(public_health_variables_class._meta.db_table)[0],
            source_grid_table=uf_150mgrid_class.db_entity_key,
            source_grid_schema=parse_schema_and_table(uf_150mgrid_class._meta.db_table)[0],
            transit_stop_table=transit_stop_class.db_entity_key,
            transit_stop_schema= parse_schema_and_table(transit_stop_class._meta.db_table)[0],
            census_rate_table=census_rate_class.db_entity_key,
            census_rate_schema=parse_schema_and_table(census_rate_class._meta.db_table)[0],
            trip_lengths_table=trip_length_class.db_entity_key,
            trip_lengths_schema=parse_schema_and_table(trip_length_class._meta.db_table)[0],
            grid_outcome_schema=parse_schema_and_table(grid_outcome_class._meta.db_table)[0],
            grid_outcome_table=grid_outcome_class.db_entity_key,
            block_group_outcome_schema=parse_schema_and_table(block_group_outcome_class._meta.db_table)[0],
            block_group_outcome_table=block_group_outcome_class.db_entity_key,
            outcome_summary_schema=parse_schema_and_table(outcome_summary_class._meta.db_table)[0],
            outcome_summary_table=outcome_summary_class.db_entity_key
        )

        self.run_public_health_preprocesses(sql_config_dict, **kwargs)
        read_UD4H_model_doc()
        self.read_public_health_models()

        all_features = public_health_variables_class.objects.filter(Q(pop__gt=0))
        output = []

        for feature in all_features:

            feature_dict = dict(
                id=feature.id,
                pop=feature.pop,
                pop_adult=feature.pop_adult,
                pop_adult_high=feature.pop_adult_high,
                pop_adult_med=feature.pop_adult_med,
                pop_adult_low=feature.pop_adult_low,
                pop_senior=feature.pop_senior,
                pop_teen=feature.pop_teen,
                pop_children=feature.pop_children,
                hh=feature.hh,
                gender2=feature.gender2,                   # = percent_female
                age_children=feature.age_children,         # = average_age
                age_adult=feature.age_adult,               # = average_age
                age_teens=feature.age_teens,               # = average_age
                age_seniors=feature.age_seniors,           # = average_age

                racehisp1=feature.racehisp1,               # = pop_white
                racehisp2=feature.racehisp2,               # = pop_black
                racehisp4=feature.racehisp4,               # = pop_asian
                racehisp97=feature.racehisp97,             # = pop_american_indian + pop_hawaiian_islander + pop_other_ethnicity
                emply2=feature.emply2,                  # = pop_age16_up - pop_employed
                educa2=feature.educa2,                  # = % pop_hs_diploma
                educa3=feature.educa3,                  # = % pop_some_college
                educa4=feature.educa4,                  # = % pop_college_degree
                educa5=feature.educa5,                 # = % pop_graduate_degree
                own2=feature.own2,                    # = percent renters
                hhsize=feature.hhsize,                 # = hh_avg_size
                hhveh=feature.hhveh,                    # = hh_avg_vehicles
                incom2=feature.incom2,                   # = income_10k_35k = hh_inc_10_20 + hh_inc_20_30 + hh_inc_30_40/2
                incom3=feature.incom3,                   # = income_35k_50k = hh_inc_30_40/2 + hh_inc_40_50
                incom4=feature.incom4,                   # = income_50k_75k = hh_inc_50_60 + hh_inc_60_75
                incom5=feature.incom5,                   # = income_75k_100k = hh_inc_75_100
                incom6=feature.incom6,                   # = income_100k_150k = hh_inc_100_125 + hh_inc_125_150
                incom7=feature.incom7,                   # = income_150k_plus = hh_inc_150
                child_any1=feature.child_any1,              # = % hh_with_children

                disabled1_children=feature.disabled1_children,     # = % pop with disability (excluding trouble walking)
                disabled1_teens=feature.disabled1_teens,        # = % pop with disability (excluding trouble walking)
                disabled1_adult=feature.disabled1_adult,        # = % pop with disability (excluding trouble walking)
                disabled1_seniors=feature.disabled1_seniors,      # = % pop with disability (excluding trouble walking)

                disabled2_children=feature.disabled2_children,      # = % pop with trouble walking
                disabled2_teens=feature.disabled2_teens,         # = % pop with trouble walking
                disabled2_adult=feature.disabled2_adult,         # = % pop with trouble walking
                disabled2_seniors=feature.disabled2_seniors,       # = % pop with trouble walking

                emply_hh=feature.emply_hh,                # = employed_pop / hh
                educa_hh2=feature.educa_hh2,               # = % hh with high school diploma
                educa_hh3=feature.educa_hh3,               # = % hh with some college
                educa_hh4=feature.educa_hh4,               # = % hh with college degree
                educa_hh5=feature.educa_hh5,               # = % hh with graduate degree)

                # BE Vars
                bldg_sqft_res=feature.bldg_sqft_res,
                bldg_sqft_ret1=feature.bldg_sqft_ret1,
                bldg_sqft_off=feature.bldg_sqft_off,
                b1=feature.b1,
                b2=feature.b2,
                b3=feature.b3,
                b4=feature.b4,
                b5=feature.b5,
                a=feature.a,
                du_1km_tr=feature.du_1km_tr,
                resmix_dens=feature.resmix_dens,
                bldg_sqft_ret=feature.bldg_sqft_ret,
                far_nonres=feature.far_nonres,
                mix5=feature.mix5,
                rail_any=feature.rail_any,
                transit_distance=feature.transit_distance,
                transit_count=feature.transit_count,
                school_distance=feature.school_distance,
                retail_distance=feature.retail_distance,
                restaurant_distance=feature.restaurant_distance,
                intersection_density_sqmi=feature.intersection_density_sqmi,
                local_street=feature.local_street,
                major_street=feature.major_street,
                freeway_arterial_any=feature.freeway_arterial_any,
                park_open_space_distance=feature.park_open_space_distance,
                acres_parcel_park_open_space=feature.acres_parcel_park_open_space,
                du_variable=feature.du_variable,
                emp_variable=feature.emp_variable,
                res_index=feature.res_index,
                com_index=feature.com_index,
                park_access=feature.park_access,
                regional_access=feature.regional_access,
                network_index=feature.network_index,
                transit_access=feature.transit_access,
                majrd_index=feature.major_road_index,
                walk_index=feature.walk_index,
                walk_index_chts_senior_walk_any=feature.walk_index_chts_senior_walk_any,
                walk_index_chts_senior_auto_min=feature.walk_index_chts_senior_auto_min,
                walk_index_chts_teens_walk_any=feature.walk_index_chts_teens_walk_any,
                walk_index_chts_child_walk_any=feature.walk_index_chts_child_walk_any,
                walk_index_chts_adult_bike_any=feature.walk_index_chts_adult_bike_any,
                walk_index_chts_adult_walk_min=feature.walk_index_chts_adult_walk_min,
                walk_index_chts_senior_walk_min=feature.walk_index_chts_senior_walk_min,
                walk_index_chts_teens_walk_min=feature.walk_index_chts_teens_walk_min,
                walk_index_chts_adult_auto_min=feature.walk_index_chts_adult_auto_min,
                walk_index_chis_adult_modPA_any=feature.walk_index_chis_adult_modpa_any,
                walk_index_chis_adult_overweight=feature.walk_index_chis_adult_overweight,
                walk_index_chis_senior_overweight=feature.walk_index_chis_senior_overweight,
                walk_index_chis_adult_obese=feature.walk_index_chis_adult_obese,
                walk_index_chis_senior_gh=feature.walk_index_chis_senior_gh,
                walk_index_chis_senior_walk_le_min=feature.walk_index_chis_senior_walk_le_min,
                walk_index_chis_adult_modPA_min=feature.walk_index_chis_adult_modpa_min,
                walk_index_chis_adult_bmi=feature.walk_index_chis_adult_bmi,
                walk_index_chis_child_PA60=feature.walk_index_chis_child_pa60,
                walk_index_chis_child_walk_school=feature.walk_index_chis_child_walk_school
            )

            model_result = self.apply_public_health_models_to_feature(feature_dict)
            result_minutes = self.populate_output_minutes(model_result)
            output_dict = map(lambda key: result_minutes[key.lower()], self.outcome_fields)
            output.append(output_dict)
        self.public_health_progress(0.1, **kwargs)
        self.write_results_to_database(sql_config_dict, output)
        self.public_health_progress(0.1, **kwargs)
        self.aggregate_results_to_block_group(sql_config_dict)
        self.public_health_progress(0.1, **kwargs)
        self.aggregate_results_to_outcomes_summary_table(sql_config_dict)
        self.public_health_progress(0.15, **kwargs)

    def apply_public_health_models_to_feature(self, feature_dict):

        # the first group of models does not require any preprocessing
        for model in self.public_health_model_groups[1]:
            transformed_result = model.run_csv_model(feature_dict)
            feature_dict[model.outcome.lower()] = transformed_result

        # the second group of models requires the walk_any and walk_tr_any variables
        for model in self.public_health_model_groups[2]:
            transformed_result = model.run_csv_model(feature_dict)
            feature_dict[model.outcome.lower()] = transformed_result

        # before running the third group of models we need to produce some additional variables
        # from the outputs already generated
        for model in self.public_health_model_groups[3]:
            prefix = model.key_prefix.lower()
            if model.age_group in ['adult', 'seniors']:
                feature_dict[prefix + "walk_tr"] = feature_dict[prefix + "walk_tr_any"] * feature_dict[prefix + "walk_tr_min"]
                feature_dict[prefix + "walk_le"] = feature_dict[prefix + "walk_le_any"] * feature_dict[prefix + "walk_le_min"]
                feature_dict[prefix + "mod_pa"] = feature_dict[prefix + "mod_pa_any"] * feature_dict[prefix + "mod_pa_min"]
                feature_dict[prefix + "vig_pa"] = feature_dict[prefix + "vig_pa_any"] * feature_dict[prefix + "vig_pa_min"]
                feature_dict[prefix + "mvpa_mets"] = sum([
                    feature_dict[prefix + "walk_tr"] * 3.5,
                    feature_dict[prefix + "walk_le"] * 3.5,
                    feature_dict[prefix + "mod_pa"] * 4,
                    feature_dict[prefix + "vig_pa"] * 8
                ])
                feature_dict[prefix + "mvpa_mets_log"] = log(feature_dict[prefix + "mvpa_mets"]+1)
            transformed_result = model.run_csv_model(feature_dict)
            feature_dict[model.outcome.lower()] = transformed_result

        for model in self.public_health_model_groups[4]:
            prefix = model.key_prefix.lower()

            if model.age_group in ['adult', 'seniors']:
                feature_dict[prefix + "bmi_log"] = log(feature_dict[prefix + "bmi"])

            transformed_result = model.run_csv_model(feature_dict)
            feature_dict[model.outcome.lower()] = transformed_result

        return feature_dict

    def populate_output_minutes(self, feature_dict):
        for model in self.outcome_fields:
            if '_minutes' in model:
                model_name = model[:-8]
                if model_name + '_min' in feature_dict and model_name + '_any' in feature_dict:
                    feature_dict[model_name + '_minutes'] = feature_dict[model_name + '_min'] * \
                                                            feature_dict[model_name + '_any']
        return feature_dict

    def write_results_to_database(self, options, public_health_output_list):

        drop_table('{grid_outcome_schema}.{grid_outcome_table}'.format(**options))

        attribute_list = filter(lambda x: x != 'id', self.outcome_fields)
        options['output_field_syntax'] = 'id int, ' + \
                                         create_sql_calculations(attribute_list, '{0} numeric(20,8)')

        execute_sql("create table {grid_outcome_schema}.{grid_outcome_table} ({output_field_syntax});".format(
            **options))

        output_textfile = StringIO("")
        for row in public_health_output_list:
            stringrow = []
            for item in row:
                if isinstance(item, int):
                    stringrow.append(str(item))
                else:
                    stringrow.append(str(round(item, 8)))
            output_textfile.write("\t".join(stringrow) + "\n")

        output_textfile.seek(os.SEEK_SET)
        #copy text file output back into Postgres
        copy_from_text_to_db(output_textfile, '{grid_outcome_schema}.{grid_outcome_table}'.format(**options))
        output_textfile.close()
        ##---------------------------
        pSql = '''alter table {grid_outcome_schema}.{grid_outcome_table}
                    add column wkb_geometry geometry (GEOMETRY, 4326);'''.format(**options)
        execute_sql(pSql)

        pSql = '''update {grid_outcome_schema}.{grid_outcome_table} b set
                    wkb_geometry = st_setSRID(a.wkb_geometry, 4326)
                    from (select id, wkb_geometry from {source_grid_schema}.{source_grid_table}) a
                    where cast(a.id as int) = cast(b.id as int);
        '''.format(**options)
        execute_sql(pSql)

        add_geom_idx(options['grid_outcome_schema'], options['grid_outcome_table'], 'wkb_geometry')
        add_primary_key(options['grid_outcome_schema'], options['grid_outcome_table'],  'id')

        # Since not every grid cell results in a grid_outcome, we need to wipe out the rel
        # table and recreate it to match the base grid_coutcome table. Otherwise there will
        # be to many rel table rows and cloning the DbEntity or ConfigEntity will fail
        logger.info("Writing to relative table {grid_outcome_schema}.{grid_outcome_table}rel".format(**options))
        truncate_table("{grid_outcome_schema}.{grid_outcome_table}rel".format(**options))
        from footprint.main.publishing.data_import_publishing import create_and_populate_relations
        create_and_populate_relations(
            self.config_entity,
            self.config_entity.computed_db_entities(key=DbEntityKey.PH_GRID_OUTCOMES)[0])


    def aggregate_results_to_block_group(self, sql_config_dict):
        """
        Aggregates the result table (at grid scale) to a Census Block Group result
        """

        attribute_list = filter(lambda x: x not in ['id', 'hh', 'pop', 'pop_adult', 'pop_adult_high', 'pop_adult_med',
                                                    'pop_adult_low', 'pop_senior', 'pop_teen', 'pop_children'],
                                self.outcome_fields)

        field_calculations = ''',
        '''.join([
            "case when SUM(grid.pop) > 0 then SUM(grid.{field} * grid.pop) / SUM(grid.pop) else 0 end as {field}".format(
                field=field)
            for field in attribute_list
        ])

        drop_table('{block_group_outcome_schema}.{block_group_outcome_table}'.format(**sql_config_dict))

        create_blockgroup_results = """
        CREATE TABLE {block_group_outcome_schema}.{block_group_outcome_table} AS SELECT

          bg.id as id,
          bg.blockgroup as blockgroup,
          bg.tract as tract,
          bg.county_name as county_name,

          SUM(grid.pop) as pop,
          SUM(grid.hh) as hh,
          SUM(grid.pop_adult) as pop_adult,

          SUM(grid.pop_adult_high) as pop_adult_high,
          SUM(grid.pop_adult_med) as pop_adult_med,
          SUM(grid.pop_adult_low) as pop_adult_low,

          SUM(grid.pop_senior) as pop_senior,
          SUM(grid.pop_teen) as pop_teen,
          SUM(grid.pop_children) as pop_children,

          {field_calculations},

          bg.wkb_geometry as wkb_geometry

        FROM (select grid_id, census_id from {public_health_variables_schema}.{source_grid_table}_join group by grid_id, census_id) grid_portions
        inner join {grid_outcome_schema}.{grid_outcome_table} grid on grid_portions.grid_id = grid.id
        inner join {census_rate_schema}.{census_rate_table} bg on grid_portions.census_id = bg.id

        group by bg.id, bg.blockgroup, tract, bg.county_name, bg.wkb_geometry;

        """.format(field_calculations=field_calculations, **sql_config_dict)

        execute_sql(create_blockgroup_results)

    def aggregate_results_to_outcomes_summary_table(self, sql_config_dict):
        """
        Aggregates the result table (at grid scale) to a standardized summary table
        """

        attribute_list = filter(lambda x: x not in ['id', 'hh', 'pop', 'pop_adult', 'pop_adult_high', 'pop_adult_med',
                                                    'pop_adult_low', 'pop_senior', 'pop_teen', 'pop_children'],
                                self.outcome_fields)
        output_list = filter(lambda x: x not in ['id'],
                                self.outcome_fields)

        field_calculations = ''',
        '''.join([
            "case when SUM(pop) > 0 then SUM({field} * pop) / SUM(pop) else 0 end as {field}".format(
                field=field)
            for field in attribute_list
        ])

        truncate_table('{outcome_summary_schema}.{outcome_summary_table}'.format(**sql_config_dict))

        pSql = """
        SELECT
          SUM(hh) as hh,
          SUM(pop) as pop,
          SUM(pop_adult) as pop_adult,
          SUM(pop_adult_high) as pop_adult_high,
          SUM(pop_adult_med) as pop_adult_med,
          SUM(pop_adult_low) as pop_adult_low,
          SUM(pop_senior) as pop_senior,
          SUM(pop_teen) as pop_teen,
          SUM(pop_children) as pop_children,

          {field_calculations}

        FROM {grid_outcome_schema}.{grid_outcome_table};
        """.format(field_calculations=field_calculations, **sql_config_dict)

        summary_results = flatten(report_sql_values(pSql, 'fetchall'))

        index_id = 0
        for result in output_list:

            source = 'ref'
            model_name = result
            ph_models = self.list_UD4H_models()

            if '_minutes' in model_name:
                model_name = model_name[:-8] + '_min'

            for model in ph_models:
                ph_model_name = "".join(model[0]['name'].split())[:-4].lower()
                if ph_model_name == model_name:
                    source = model[0]['source']

            pSql = '''
            insert into {outcome_summary_schema}.{outcome_summary_table} values ({index_id}, '{column_name}', '{source}', {model_output});
            '''.format(index_id=index_id, column_name=str(result), source=str(source), model_output=summary_results[index_id], **sql_config_dict)

            execute_sql(pSql)
            index_id += 1

    def list_UD4H_models(self):
        """
        reads a csv provided by UD4H and returns a list of those models and their associated characteristics
        :return:
        """
        csv_path = UD4H_MODEL_PATH + 'UD4H_models.csv'
        csv_dir = UD4H_MODEL_PATH
        ph_models = []
        with open(csv_path, mode='rU') as csv_file:
            reader = csv.reader(csv_file)

            #skip the header
            next(reader, None)

            for group, model_file_name, source, age_group, inc_group, outcome, type, transformation, duan, two_part_model_calculation, calibration in reader:
                ph_models.append([dict(name=model_file_name,
                                       source=source,
                                       csv_path=csv_dir+source+'/' + model_file_name.strip(),
                                       group=int(group),
                                       age_group=age_group,
                                       income_group=inc_group,
                                       type=type,
                                       duan=duan)])

        return ph_models

    class Meta(object):
        app_label = 'main'
        abstract = False


def read_UD4H_attr_transforms():

    csv_path = UD4H_MODEL_PATH + "ud4h_attr_transforms.csv"

    with open(csv_path, mode='rU') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        transformation_dict = dict()
        for attr, source, minimum, maximum, adult_all, adult_low, adult_medium, adult_high, seniors, teens, children in reader:
            if 'disabled' in attr:
                attr = source + '_' + attr

            transformation_dict.update({
                attr: {'source': source,
                       'minimum': minimum,
                       'maximum': maximum,
                       'adult':  {'all': adult_all, 'low': adult_low, 'med': adult_medium, 'high': adult_high},
                       'seniors': {'all': seniors},
                       'teens': {'all': teens},
                       'children': {'all': children}}

            })
        return transformation_dict


def read_UD4H_model_doc():
    """
    reads a csv provided by UD4H to populate our PublicHealthOutcomeAnalysis model
    :return:
    """
    csv_path = UD4H_MODEL_PATH + 'UD4H_models.csv'
    csv_dir = UD4H_MODEL_PATH
    with open(csv_path, mode='rU') as csv_file:
        reader = csv.reader(csv_file)

        #skip the header
        next(reader, None)

        for group, model_file_name, source, age_group, inc_group, outcome, type, transformation, duan, two_part_model_calculation, calibration in reader:
            PublicHealthOutcomeAnalysis.objects.get_or_create(name=model_file_name,
                                                              source=source,
                                                              csv_path=csv_dir+source+'/' + model_file_name.strip(),
                                                              group=int(group),
                                                              age_group=age_group,
                                                              income_group=inc_group,
                                                              type=type,
                                                              duan=duan)


def process_UD4H_csvs():
    """
    standardizes filenames in the `UD4H_MODEL_PATH` directory
    :return:
    """
    CHIS = glob.iglob(UD4H_MODEL_PATH + '/CHIS/*')
    CHTS = glob.iglob(UD4H_MODEL_PATH + '/CHTS/*')

    csvs = list(CHTS) + list(CHIS)

    for pathAndFilename in csvs:
        dir = os.path.dirname(pathAndFilename)
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))

        newtitle = re.sub(r"\d+", "", title)
        newtitle = newtitle.replace('final', "").strip('_').replace('_adj', '')

        filename = newtitle + ext

        os.rename(pathAndFilename, os.path.join(dir, filename))
