
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
from StringIO import StringIO

import datetime
import os
from django.db.models import Sum, Q

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.analysis_module.vmt_module.vmt_module_preprocesses import run_vmt_one_mile_buffers, \
    run_vmt_quarter_mile_buffers, run_vmt_variable_trip_length_buffers, run_transit_proximity
from footprint.main.models.config.scenario import FutureScenario
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.utils.query_parsing import annotated_related_feature_class_pk_via_geographies
from footprint.main.utils.uf_toolbox import drop_table, execute_sql, copy_from_text_to_db, create_sql_calculations, \
    truncate_table
from footprint.main.utils.utils import parse_schema_and_table
from footprint.utils.websockets import send_message_to_client
from vmt_calculate_final_results import calculate_final_vmt_results
from vmt_calculate_log_odds import calculate_log_odds
from vmt_model_constants import vmt_output_field_list
from vmt_raw_trip_generation import generate_raw_trips
from vmt_trip_purpose_splits import calculate_trip_purpose_splits

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


class VmtUpdaterTool(AnalysisTool):

    objects = GeoInheritanceManager()
    JOB_SIZE = 10000

    class Meta(object):
        app_label = 'main'
        abstract = False

    def vmt_progress(self, proportion, **kwargs):

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

    def run_vmt_preprocesses(self, sql_config_dict, **kwargs):
        run_vmt_one_mile_buffers(sql_config_dict)
        self.vmt_progress(0.1, **kwargs)

        run_transit_proximity(sql_config_dict)
        self.vmt_progress(0.1, **kwargs)

        run_vmt_quarter_mile_buffers(sql_config_dict)

        self.vmt_progress(0.4, **kwargs)

        run_vmt_variable_trip_length_buffers(sql_config_dict)

        self.vmt_progress(0.2, **kwargs)

    def update(self, **kwargs):

        # Make sure all related models have been created before querying
        logger.info("Executing Vmt using {0}".format(self.config_entity))

        self.vmt_progress(0.1, **kwargs)

        vmt_result_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT)
        vmt_variables_feature_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT_VARIABLES)
        census_rates_feature_class = self.config_entity.db_entity_feature_class(DbEntityKey.CENSUS_RATES)

        if isinstance(self.config_entity.subclassed, FutureScenario):
            scenario_class = self.config_entity.db_entity_feature_class(DbEntityKey.END_STATE)
            trip_lengths_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT_FUTURE_TRIP_LENGTHS)
            transit_stop_class = self.config_entity.db_entity_feature_class(DbEntityKey.FUTURE_TRANSIT_STOPS)
            is_future = True
        else:
            scenario_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
            trip_lengths_class = self.config_entity.db_entity_feature_class(DbEntityKey.VMT_BASE_TRIP_LENGTHS)
            transit_stop_class = self.config_entity.db_entity_feature_class(DbEntityKey.BASE_TRANSIT_STOPS)
            is_future = False

        sql_config_dict = dict(
            vmt_result_table=vmt_result_class.db_entity_key,
            vmt_schema=parse_schema_and_table(vmt_result_class._meta.db_table)[0],
            uf_canvas_table=scenario_class.db_entity_key,
            uf_canvas_schema=parse_schema_and_table(scenario_class._meta.db_table)[0],
            census_rates_table=census_rates_feature_class.db_entity_key,
            census_rates_schema=parse_schema_and_table(census_rates_feature_class._meta.db_table)[0],
            trip_lengths_table=trip_lengths_class.db_entity_key,
            trip_lengths_schema=parse_schema_and_table(trip_lengths_class._meta.db_table)[0],
            vmt_variables_table=vmt_variables_feature_class.db_entity_key,
            vmt_variables_schema=parse_schema_and_table(vmt_variables_feature_class._meta.db_table)[0],
            vmt_rel_table=parse_schema_and_table(vmt_result_class._meta.db_table)[1],
            vmt_rel_column=vmt_result_class._meta.parents.values()[0].column,
            transit_stop_schema=parse_schema_and_table(transit_stop_class._meta.db_table)[0],
            transit_stop_table=transit_stop_class.db_entity_key,
            config_entity=self.config_entity
        )
        #
        if not kwargs.get('postprocess_only'):
            self.run_vmt_preprocesses(sql_config_dict, **kwargs)

        drop_table('{vmt_schema}.{vmt_result_table}'.format(**sql_config_dict))
        truncate_table('{vmt_schema}.{vmt_rel_table}'.format(**sql_config_dict))

        attribute_list = filter(lambda x: x != 'id', vmt_output_field_list)
        output_field_syntax = 'id int, ' + create_sql_calculations(attribute_list, '{0} numeric(14, 4)')

        pSql = '''
        create table {vmt_schema}.{vmt_result_table} ({output_field_syntax});'''.format(
            output_field_syntax=output_field_syntax, **sql_config_dict)
        execute_sql(pSql)

        trip_lengths = DbEntityKey.VMT_FUTURE_TRIP_LENGTHS if is_future else DbEntityKey.VMT_BASE_TRIP_LENGTHS
        total_employment = scenario_class.objects.aggregate(Sum('emp'))
        all_features = scenario_class.objects.filter(Q(du__gt=0) | Q(emp__gt=0))
        all_features_length = len(all_features)

        max_id = scenario_class.objects.all().order_by("-id")[0].id
        min_id = scenario_class.objects.all().order_by("id")[0].id

         # This section of the model passes data from POSTGRES into Python and is saved in memory before being committed
        # back to the database. In order to not use all memory with large datasets, jobs are broken up with a maximum
        # job size of JOB_SIZE rows before being committed to the database. It will iterate through until all rows are
        # calculated and committed.
        if all_features_length > self.JOB_SIZE:
            job_count = all_features_length / self.JOB_SIZE
            rows_per_range = (max_id - min_id) / job_count
        else:
            rows_per_range = max_id - min_id
            job_count = 1
        print 'Job Count: {0}'.format(job_count)
        start_id = min_id

        for i in range(job_count):
            if i == job_count - 1:
                end_id = max_id
            else:
                end_id = start_id + rows_per_range - 1
            logger.info('Job: {0}'.format(i))
            logger.info('Start Id: {0}'.format(start_id))
            logger.info('End Id: {0}'.format(end_id))

            vmt_output_list = []

            features = all_features.filter(id__range=(start_id, end_id))
            annotated_features = annotated_related_feature_class_pk_via_geographies(features, self.config_entity, [
                DbEntityKey.VMT_VARIABLES, DbEntityKey.CENSUS_RATES, DbEntityKey.VMT_FUTURE_TRIP_LENGTHS, DbEntityKey.VMT_BASE_TRIP_LENGTHS, trip_lengths])

            assert annotated_features.exists(), "VMT is about to process 0 results"

            failed_features = []

            for feature in annotated_features:
                trip_length_id = feature.vmt_future_trip_lengths if is_future else feature.vmt_base_trip_lengths
                try:
                    trip_lengths_feature = trip_lengths_class.objects.get(id=trip_length_id)
                except trip_lengths_class.DoesNotExist, e:
                    failed_features.append(feature)
                    logger.error('Cannot find trip lengths for geography with id = {0}'.format(feature.id))
                    continue

                vmt_variables_feature = vmt_variables_feature_class.objects.get(id=feature.vmt_variables)

                try:
                    census_rates_feature = census_rates_feature_class.objects.get(id=feature.census_rates)
                except census_rates_feature_class.DoesNotExist, e:
                    logger.error('Cannot find census rate with id = {0}'.format(feature.census_rates))
                    continue

                vmt_feature = dict(
                    id=int(feature.id),
                    acres_gross=float(feature.acres_gross) or 0,
                    acres_parcel=float(feature.acres_parcel) or 0,
                    acres_parcel_res=float(feature.acres_parcel_res) or 0,
                    acres_parcel_emp=float(feature.acres_parcel_emp) or 0,
                    acres_parcel_mixed=float(feature.acres_parcel_mixed_use) or 0,
                    intersections_qtrmi=float(feature.intersection_density_sqmi) or 0,
                    du=float(feature.du) or 0,
                    du_occupancy_rate=float(feature.hh / feature.du if feature.du else 0),
                    du_detsf=float(feature.du_detsf) or 0,
                    du_attsf=float(feature.du_attsf) or 0,

                    du_mf=float(feature.du_mf) or 0,
                    du_mf2to4=float(feature.du_mf2to4) or 0,
                    du_mf5p=float(feature.du_mf5p) or 0,
                    hh=float(feature.hh) or 0,
                    hh_avg_size=float(feature.pop / feature.hh if feature.hh > 0 else 0),
                    hh_avg_inc=float(census_rates_feature.hh_agg_inc_rate) or 0,

                    hh_inc_00_10=float(feature.hh * census_rates_feature.hh_inc_00_10_rate) or 0,
                    hh_inc_10_20=float(feature.hh * census_rates_feature.hh_inc_10_20_rate) or 0,
                    hh_inc_20_30=float(feature.hh * census_rates_feature.hh_inc_20_30_rate) or 0,
                    hh_inc_30_40=float(feature.hh * census_rates_feature.hh_inc_30_40_rate) or 0,
                    hh_inc_40_50=float(feature.hh * census_rates_feature.hh_inc_40_50_rate) or 0,
                    hh_inc_50_60=float(feature.hh * census_rates_feature.hh_inc_50_60_rate) or 0,
                    hh_inc_60_75=float(feature.hh * census_rates_feature.hh_inc_60_75_rate) or 0,
                    hh_inc_75_100=float(feature.hh * census_rates_feature.hh_inc_75_100_rate) or 0,
                    hh_inc_100p=float(feature.hh * (census_rates_feature.hh_inc_100_125_rate +
                                                                     census_rates_feature.hh_inc_125_150_rate +
                                                                     census_rates_feature.hh_inc_150_200_rate +
                                                                     census_rates_feature.hh_inc_200p_rate)) or 0,

                    pop=float(feature.pop) or 0,
                    pop_employed=float(feature.pop * census_rates_feature.pop_age16_up_rate *
                                       census_rates_feature.pop_employed_rate) or 0,
                    pop_age16_up=float(feature.pop * census_rates_feature.pop_age16_up_rate) or 0,
                    pop_age65_up=float(feature.pop * census_rates_feature.pop_age65_up_rate) or 0,

                    emp=float(feature.emp) or 0,
                    emp_retail=float(feature.emp_retail_services + feature.emp_other_services) or 0,
                    emp_restaccom=float(feature.emp_accommodation + feature.emp_restaurant) or 0,
                    emp_arts_entertainment=float(feature.emp_arts_entertainment) or 0,
                    emp_office=float(feature.emp_off) or 0,
                    emp_public=float(feature.emp_public_admin + feature.emp_education) or 0,
                    emp_industry=float(feature.emp_ind + feature.emp_ag) or 0,

                    emp_within_1mile=float(vmt_variables_feature.emp_1mile) or 0,
                    hh_within_quarter_mile_trans=1 if vmt_variables_feature.transit_1km > 0 else 0,

                    vb_acres_parcel_res_total=float(vmt_variables_feature.acres_parcel_res_vb) or 0,
                    vb_acres_parcel_emp_total=float(vmt_variables_feature.acres_parcel_emp_vb) or 0,
                    vb_acres_parcel_mixed_total=float(vmt_variables_feature.acres_parcel_mixed_use_vb) or 0,
                    vb_du_total=float(vmt_variables_feature.du_vb) or 0,
                    vb_pop_total=float(vmt_variables_feature.pop_vb) or 0,
                    vb_emp_total=float(vmt_variables_feature.emp_vb) or 0,
                    vb_emp_retail_total=float(vmt_variables_feature.emp_ret_vb) or 0,
                    vb_hh_total=float(vmt_variables_feature.hh_vb) or 0,
                    vb_du_mf_total=float(vmt_variables_feature.du_mf_vb) or 0,
                    vb_hh_inc_00_10_total=float(vmt_variables_feature.hh_inc_00_10_vb) or 0,
                    vb_hh_inc_10_20_total=float(vmt_variables_feature.hh_inc_10_20_vb) or 0,
                    vb_hh_inc_20_30_total=float(vmt_variables_feature.hh_inc_20_30_vb) or 0,
                    vb_hh_inc_30_40_total=float(vmt_variables_feature.hh_inc_30_40_vb) or 0,
                    vb_hh_inc_40_50_total=float(vmt_variables_feature.hh_inc_40_50_vb) or 0,
                    vb_hh_inc_50_60_total=float(vmt_variables_feature.hh_inc_50_60_vb) or 0,
                    vb_hh_inc_60_75_total=float(vmt_variables_feature.hh_inc_60_75_vb) or 0,
                    vb_hh_inc_75_100_total=float(vmt_variables_feature.hh_inc_75_100_vb) or 0,
                    vb_hh_inc_100p_total=float(vmt_variables_feature.hh_inc_100p_vb) or 0,

                    vb_pop_employed_total=float(vmt_variables_feature.pop_employed_vb) or 0,
                    vb_pop_age16_up_total=float(vmt_variables_feature.pop_age16_up_vb) or 0,
                    vb_pop_age65_up_total=float(vmt_variables_feature.pop_age65_up_vb) or 0,

                    emp30m_transit=float(trip_lengths_feature.emp_30min_transit) or 0,
                    emp45m_transit=float(trip_lengths_feature.emp_45min_transit) or 0,
                    prod_hbw=float(trip_lengths_feature.productions_hbw) or 0,
                    prod_hbo=float(trip_lengths_feature.productions_hbo) or 0,
                    prod_nhb=float(trip_lengths_feature.productions_nhb) or 0,
                    attr_hbw=float(trip_lengths_feature.attractions_hbw) or 0,
                    attr_hbo=float(trip_lengths_feature.attractions_hbo) or 0,
                    attr_nhb=float(trip_lengths_feature.attractions_nhb) or 0,

                    qmb_acres_parcel_res_total=float(vmt_variables_feature.acres_parcel_res_qtrmi) or 0,
                    qmb_acres_parcel_emp_total=float(vmt_variables_feature.acres_parcel_emp_qtrmi) or 0,
                    qmb_acres_parcel_mixed_total=float(vmt_variables_feature.acres_parcel_mixed_use_qtrmi) or 0,
                    qmb_du_total=float(vmt_variables_feature.du_qtrmi) or 0,
                    qmb_pop_total=float(vmt_variables_feature.pop_qtrmi) or 0,
                    qmb_emp_total=float(vmt_variables_feature.emp_qtrmi) or 0,
                    qmb_emp_retail=float(vmt_variables_feature.emp_ret_qtrmi) or 0,
                    hh_avg_veh=float(census_rates_feature.hh_agg_veh_rate) or 0,

                    truck_adjustment_factor=0.031,
                    total_employment=float(total_employment['emp__sum']) or 0)

                # run raw trip generation
                vmt_feature_trips = generate_raw_trips(vmt_feature)

                # run trip purpose splits
                vmt_feature_trip_purposes = calculate_trip_purpose_splits(vmt_feature_trips)

                # run log odds
                vmt_feature_log_odds = calculate_log_odds(vmt_feature_trip_purposes)

                # run vmt equations
                vmt_output = calculate_final_vmt_results(vmt_feature_log_odds)

                # filters the vmt feature dictionary for specific output fields for writing to the database
                output_list = map(lambda key: vmt_output[key], vmt_output_field_list)
                vmt_output_list.append(output_list)

            # write result db table
            self.write_vmt_results_to_database(sql_config_dict, vmt_output_list)
            start_id += rows_per_range
        self.vmt_progress(0.05, **kwargs)
        self.update_result_table_geometry_column(sql_config_dict)
        self.vmt_progress(0.05, **kwargs)

        logger.info("Done executing Vmt")
        logger.info("Executed Vmt using {0}".format(self.config_entity))

        if failed_features:
            logger.error("Failed to process {0} features: {1}".format(len(failed_features), [f.id for f in failed_features]))


    def write_vmt_results_to_database(self, options, vmt_output_list):

        vmt_output_text_file = StringIO("")

        for row in vmt_output_list:
            stringrow = []
            for item in row:
                if isinstance(item, int):
                    stringrow.append(str(item))
                else:
                    stringrow.append(str(round(item, 4)))
            vmt_output_text_file.write("\t".join(stringrow,) + "\n")

        vmt_output_text_file.seek(os.SEEK_SET)
        #copy text file output back into Postgres
        copy_from_text_to_db(vmt_output_text_file, '{vmt_schema}.{vmt_result_table}'.format(**options))
        vmt_output_text_file.close()

    def update_result_table_geometry_column(self, options):
        pSql = '''alter table {vmt_schema}.{vmt_result_table} add column wkb_geometry geometry (GEOMETRY, 4326);
        '''.format(**options)
        execute_sql(pSql)

        pSql = '''
        update {vmt_schema}.{vmt_result_table} b set wkb_geometry = a.wkb_geometry
            from (select id, wkb_geometry from {uf_canvas_schema}.{uf_canvas_table}) a
            where cast(a.id as int) = cast(b.id as int);
        CREATE INDEX ON {vmt_schema}.{vmt_result_table}  USING gist (wkb_geometry);
        '''.format(**options)

        execute_sql(pSql)

        updated = datetime.datetime.now()
        truncate_table(options['vmt_schema'] + '.' + options['vmt_rel_table'])

        pSql = '''
        insert into {vmt_schema}.{rel_table} ({rel_column}, updated)
          select id, '{updated}' from {vmt_schema}.{vmt_result_table};'''.format(
            vmt_schema=options['vmt_schema'],
            vmt_result_table=options['vmt_result_table'],
            rel_table=options['vmt_rel_table'],
            rel_column=options['vmt_rel_column'],
            updated=updated)

        execute_sql(pSql)

        from footprint.main.publishing.data_import_publishing import create_and_populate_relations
        create_and_populate_relations(options['config_entity'], options['config_entity'].computed_db_entities(key=DbEntityKey.VMT)[0])
