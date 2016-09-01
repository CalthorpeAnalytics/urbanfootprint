
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

from footprint.main.models.analysis_module.geoprocessing_functions import aggregate_within_distance, \
    aggregate_within_variable_distance, calculate_distance
from footprint.main.utils.uf_toolbox import drop_table, execute_sql, add_geom_idx, add_primary_key

__author__ = 'calthorpe_analytics'

def add_analysis_geom(schema, table):

    pSql = '''
    DROP INDEX {schema}.{schema}_{table}_analysis_geom;
    Alter Table {schema}.{table} drop column analysis_geom;'''.format(schema=schema, table=table)
    try:
        execute_sql(pSql)
    except:
        print "analysis column did not exist... removing"

    pSql = '''alter table {schema}.{table} add column analysis_geom geometry;'''.format(schema=schema, table=table)
    try:
        execute_sql(pSql)
    except:
        print "analysis column already exists... continuing"


    pSql = '''update {schema}.{table} set analysis_geom = st_setSRID(st_transform(wkb_geometry, 3310), 3310);
    create index {schema}_{table}_analysis_geom on {schema}.{table} using gist (analysis_geom);
    '''.format(schema=schema, table=table)

    execute_sql(pSql)

def run_vmt_one_mile_buffers(sql_config_dict):

    add_analysis_geom(sql_config_dict['uf_canvas_schema'], sql_config_dict['uf_canvas_table'])
    add_analysis_geom(sql_config_dict['vmt_variables_schema'], sql_config_dict['vmt_variables_table'])
    add_analysis_geom(sql_config_dict['transit_stop_schema'], sql_config_dict['transit_stop_table'])

    pSql = '''
    update {vmt_variables_schema}.{vmt_variables_table} a set du = b.du, emp = b.emp
    from (select id, du, emp from {uf_canvas_schema}.{uf_canvas_table}) b where a.id = b.id;
    '''.format(vmt_variables_schema=sql_config_dict['vmt_variables_schema'],
               vmt_variables_table=sql_config_dict['vmt_variables_table'],
               uf_canvas_schema=sql_config_dict['uf_canvas_schema'],
               uf_canvas_table=sql_config_dict['uf_canvas_table'])

    execute_sql(pSql)

    aggregate_within_distance(dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='emp > 0',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['vmt_variables_schema'],
        target_table=sql_config_dict['vmt_variables_table'],
        target_table_query='du + emp > 0',
        target_geometry_column='analysis_geom',
        target_table_pk='id',
        distance=1609,
        suffix='one_mi',
        aggregation_type='sum',
        variable_field_dict=dict(
            emp_1mile=['emp'])
    ))


def run_transit_proximity(sql_config_dict):
    calculate_distance(dict(
        source_table=sql_config_dict['transit_stop_schema'] + '.' + sql_config_dict['transit_stop_table'],
        source_table_query='route_type = 0 or route_type = 1 or route_type = 2',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['vmt_variables_schema'],
        target_table=sql_config_dict['vmt_variables_table'],
        target_geometry_column='analysis_geom',
        target_table_query='du > 0',
        target_table_pk='id',
        maximum_distance=403,
        column='transit_1km'
    ))


def run_vmt_quarter_mile_buffers(sql_config_dict):

    aggregate_within_distance(dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='pop + emp > 0',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['vmt_variables_schema'],
        target_table=sql_config_dict['vmt_variables_table'],
        target_table_query='du + emp > 0',
        target_geometry_column='analysis_geom',
        target_table_pk='id',
        distance=403,
        suffix='qtr_mi',
        aggregation_type='sum',
        variable_field_dict=dict(
            acres_parcel_res_qtrmi=['acres_parcel_res'],
            acres_parcel_emp_qtrmi=['acres_parcel_emp'],
            acres_parcel_mixed_use_qtrmi=['acres_parcel_mixed_use'],
            du_qtrmi=['du'],
            pop_qtrmi=['pop'],
            emp_qtrmi=['emp'],
            emp_ret_qtrmi=['emp_ret'])
    ))

    pSql = '''DROP INDEX {schema}.{schema}_{table}_analysis_geom;
    Alter Table {schema}.{table} drop column analysis_geom;'''.format(schema=sql_config_dict['transit_stop_schema'],
                                                                   table=sql_config_dict['transit_stop_table'])
    execute_sql(pSql)

def run_vmt_variable_trip_length_buffers(sql_config_dict):

    drop_table('{vmt_variables_schema}.{vmt_variables_table}_vmt_variable'.format(
        vmt_variables_schema=sql_config_dict['vmt_variables_schema'],
        vmt_variables_table=sql_config_dict['vmt_variables_table']))

    pSql = '''
    create table {vmt_variables_schema}.{vmt_variables_table}_vmt_variable
    as select
      a.id, st_transform(a.wkb_geometry, 3310) as wkb_geometry, cast(a.attractions_hbw * 1609.0 as float) as distance,
      sum(acres_parcel_res) as acres_parcel_res_vb,
      sum(acres_parcel_emp) as acres_parcel_emp_vb,
      sum(acres_parcel_mixed_use) as acres_parcel_mixed_use_vb,
      sum(pop) as pop_vb,
      sum(hh) as hh_vb,
      sum(du) as du_vb,
      sum(du_mf) as du_mf_vb,
      sum(emp) as emp_vb,
      sum(emp_ret) as emp_ret_vb,
      sum(hh_inc_00_10) as hh_inc_00_10_vb,
      sum(hh_inc_10_20) as hh_inc_10_20_vb,
      sum(hh_inc_20_30) as hh_inc_20_30_vb,
      sum(hh_inc_30_40) as hh_inc_30_40_vb,
      sum(hh_inc_40_50) as hh_inc_40_50_vb,
      sum(hh_inc_50_60) as hh_inc_50_60_vb,
      sum(hh_inc_60_75) as hh_inc_60_75_vb,
      sum(hh_inc_75_100) as hh_inc_75_100_vb,
      sum(hh_inc_100p) as hh_inc_100p_vb,
      sum(pop_employed) as pop_employed_vb,
      sum(pop_age16_up) as pop_age16_up_vb,
      sum(pop_age65_up) as pop_age65_up_vb

    from
      (select id, wkb_geometry, attractions_hbw from {trip_lengths_schema}.{trip_lengths_table}) a,
      (select point, acres_parcel_res, acres_parcel_emp, acres_parcel_mixed_use, pop, hh, du, du_mf, emp, emp_ret,
            hh * hh_inc_00_10_rate as hh_inc_00_10,
            hh * hh_inc_10_20_rate as hh_inc_10_20,
            hh * hh_inc_20_30_rate as hh_inc_20_30,
            hh * hh_inc_30_40_rate as hh_inc_30_40,
            hh * hh_inc_40_50_rate as hh_inc_40_50,
            hh * hh_inc_50_60_rate as hh_inc_50_60,
            hh * hh_inc_60_75_rate as hh_inc_60_75,
            hh * hh_inc_75_100_rate as hh_inc_75_100,
            hh * hh_inc_100p_rate as hh_inc_100p,
            pop * pop_age16_up_rate * pop_employed_rate as pop_employed,
            pop * pop_age16_up_rate as pop_age16_up,
            pop * pop_age65_up_rate as pop_age65_up

        from (select st_centroid(wkb_geometry) as point, pop, hh, du, du_mf, emp, emp_ret, acres_parcel_res,
        acres_parcel_emp, acres_parcel_mixed_use
        from {uf_canvas_schema}.{uf_canvas_table}) a,
             (select wkb_geometry, hh_inc_00_10_rate, hh_inc_10_20_rate, hh_inc_20_30_rate,
              hh_inc_30_40_rate, hh_inc_40_50_rate, hh_inc_50_60_rate, hh_inc_60_75_rate,
              hh_inc_75_100_rate, hh_inc_100_125_rate + hh_inc_125_150_rate + hh_inc_150_200_rate + hh_inc_200p_rate as hh_inc_100p_rate,
              pop_employed_rate, pop_age16_up_rate, pop_age65_up_rate from {census_rates_schema}.{census_rates_table}) c
          where st_intersects(point, c.wkb_geometry)
          ) b
    where st_intersects(point, a.wkb_geometry) group by a.id, a.wkb_geometry, a.attractions_hbw;
    '''.format(vmt_variables_schema=sql_config_dict['vmt_variables_schema'],
               vmt_variables_table=sql_config_dict['vmt_variables_table'],
               uf_canvas_schema=sql_config_dict['uf_canvas_schema'],
               uf_canvas_table=sql_config_dict['uf_canvas_table'],
               census_rates_schema=sql_config_dict['census_rates_schema'],
               census_rates_table=sql_config_dict['census_rates_table'],
               trip_lengths_schema=sql_config_dict['trip_lengths_schema'],
               trip_lengths_table=sql_config_dict['trip_lengths_table'])

    execute_sql(pSql)

    add_geom_idx(sql_config_dict['vmt_variables_schema'], sql_config_dict['vmt_variables_table'] + '_vmt_variable')
    add_primary_key(sql_config_dict['vmt_variables_schema'], sql_config_dict['vmt_variables_table'] + '_vmt_variable', 'id')

    aggregate_within_variable_distance(dict(
        source_table=sql_config_dict['vmt_variables_schema'] + '.' + sql_config_dict['vmt_variables_table'] + '_vmt_variable',
        source_table_query='du_vb + emp_vb > 0',
        target_table_schema=sql_config_dict['vmt_variables_schema'],
        target_table=sql_config_dict['vmt_variables_table'],
        target_table_query='id is not null',
        target_table_pk='id',
        suffix='vmt_vb',
        aggregation_type='sum',
        variable_field_list=['acres_parcel_res_vb', 'acres_parcel_emp_vb', 'acres_parcel_mixed_use_vb', 'du_vb', 'pop_vb',
                             'emp_vb', 'emp_ret_vb', 'hh_vb', 'du_mf_vb', 'hh_inc_00_10_vb', 'hh_inc_10_20_vb',
                             'hh_inc_20_30_vb', 'hh_inc_30_40_vb', 'hh_inc_40_50_vb', 'hh_inc_50_60_vb',
                             'hh_inc_60_75_vb', 'hh_inc_75_100_vb', 'hh_inc_100p_vb', 'pop_employed_vb',
                             'pop_age16_up_vb', 'pop_age65_up_vb']
    ))

    pSql = '''DROP INDEX {schema}.{schema}_{table}_analysis_geom;
    Alter Table {schema}.{table} drop column analysis_geom;'''.format(schema=sql_config_dict['vmt_variables_schema'],
                                                                   table=sql_config_dict['vmt_variables_table'])
    execute_sql(pSql)
