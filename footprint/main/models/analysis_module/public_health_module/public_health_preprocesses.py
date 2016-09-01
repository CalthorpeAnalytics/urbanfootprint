
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

from footprint.main.lib.functions import merge
from footprint.main.models.analysis_module.geoprocessing_functions import aggregate_within_distance, calculate_distance, \
    aggregate_within_variable_distance
from footprint.main.models.analysis_module.vmt_module.vmt_module_preprocesses import add_analysis_geom
from footprint.main.utils.uf_toolbox import execute_sql, add_geom_idx, add_attribute_idx, add_primary_key, table_exists, \
    drop_table

__author__ = 'calthorpe_analytics'


def populate_public_health_grid_relation_table(sql_config_dict):

    join_exists = table_exists(sql_config_dict['source_grid_table'] + '_join',
                               sql_config_dict['public_health_variables_schema'])

    if not join_exists:

        pSql = '''
        create table {public_health_variables_schema}.{source_grid_table}_join
            as select
                a.id as grid_id, b.id as primary_id, c.id as census_id,
                st_area(st_intersection(a.wkb_geometry, b.wkb_geometry)) / st_area(b.wkb_geometry) as primary_proportion
        from
             {source_grid_schema}.{source_grid_table} a,
             {uf_canvas_schema}.{uf_canvas_table} b,
             {census_rate_schema}.{census_rate_table} c
        where
            st_intersects(a.wkb_geometry, b.wkb_geometry) and
            st_intersects(st_centroid(a.wkb_geometry), c.wkb_geometry);
        '''.format(**sql_config_dict)

        execute_sql(pSql)

        add_attribute_idx(sql_config_dict['public_health_variables_schema'],
                          sql_config_dict['source_grid_table'] + '_join', 'grid_id')

        add_attribute_idx(sql_config_dict['public_health_variables_schema'],
                          sql_config_dict['source_grid_table'] + '_join', 'primary_id')

        add_attribute_idx(sql_config_dict['public_health_variables_schema'],
                          sql_config_dict['source_grid_table'] + '_join', 'census_id')


def populate_grid_census_rate_attributes(sql_config_dict):

    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
        pop = b.pop,
        hh = b.hh,
        intersection_density_sqmi = b.intersection_density_sqmi,
        gender2 = (case when b.pop > 0 then b.pop_female_rate else 0 end),
        age_children = (case when b.pop > 0 then b.pop_avg_age5_11 else 0 end),
        age_teens = (case when b.pop > 0 then b.pop_avg_age12_17 else 0 end),
        age_adult = (case when b.pop > 0 then b.pop_avg_age18_64 else 0 end),
        age_seniors = (case when b.pop > 0 then b.pop_avg_age65_up else 0 end),
        racehisp1 = (case when b.pop > 0 then b.pop_white_rate else 0 end),
        racehisp2 = (case when b.pop > 0 then b.pop_black_rate else 0 end),
        racehisp4 = (case when b.pop > 0 then b.pop_asian_rate else 0 end),
        racehisp97 = (case when b.pop > 0 then b.pop_american_indian_rate + b.pop_hawaiian_islander_rate + b.pop_other_ethnicity_rate else 0 end),
        emply2 = (case when b.pop > 0 then b.pop_age16_up_rate * b.pop_unemployed_rate else 0 end),
        educa2 = (case when b.pop > 0 then b.pop_hs_diploma_rate else 0 end),
        educa3 = (case when b.pop > 0 then b.pop_assoc_some_coll_rate else 0 end),
        educa4 = (case when b.pop > 0 then b.pop_coll_degree_rate else 0 end),
        educa5 = (case when b.pop > 0 then b.pop_grad_degree_rate else 0 end),
        own2 = (case when b.hh > 0 then b.hh_rent_occ_rate else 0 end),
        hhveh = (case when b.hh > 0 then b.hh_agg_veh_rate else 0 end),
        hhsize = (case when b.hh > 0 then b.pop / b.hh else 0 end),
        incom2 = (case when b.hh > 0 then b.hh_inc_10_20_rate + b.hh_inc_20_30_rate + b.hh_inc_30_40_rate / 2  else 0 end),
        incom3 = (case when b.hh > 0 then hh_inc_30_40_rate / 2 + b.hh_inc_40_50_rate else 0 end),
        incom4 = (case when b.hh > 0 then hh_inc_50_60_rate + b.hh_inc_60_75_rate else 0 end),
        incom5 = (case when b.hh > 0 then hh_inc_75_100_rate else 0 end),
        incom6 = (case when b.hh > 0 then hh_inc_100_125_rate + b.hh_inc_125_150_rate else 0 end),
        incom7 = (case when b.hh > 0 then hh_inc_150_200_rate + b.hh_inc_200p_rate else 0 end),
        child_any1 = (case when b.hh > 0 then b.hh_with_children_under_18yr_rate else 0 end),
        disabled1_children = (case when b.pop > 0 then (b.pop_age5_17_disability_rate - b.pop_age5_17_ambulatory_disability_rate) / 2 else 0 end),
        disabled2_children = (case when b.pop > 0 then b.pop_age5_17_ambulatory_disability_rate / 2 else 0 end),
        disabled1_teens = (case when b.pop > 0 then (b.pop_age5_17_disability_rate - b.pop_age5_17_ambulatory_disability_rate) / 2 else 0 end),
        disabled2_teens = (case when b.pop > 0 then b.pop_age5_17_ambulatory_disability_rate / 2 else 0 end),
        disabled1_adult = (case when b.pop > 0 then b.pop_age18_64_disability_rate - b.pop_age18_64_ambulatory_disability_rate else 0 end),
        disabled2_adult = (case when b.pop > 0 then b.pop_age18_64_ambulatory_disability_rate else 0 end),
        disabled1_seniors = (case when b.pop > 0 then b.pop_age65up_disability_rate - b.pop_age65up_ambulatory_disability_rate else 0 end),
        disabled2_seniors = (case when b.pop > 0 then b.pop_age65up_ambulatory_disability_rate else 0 end),
        emply_hh = (case when b.hh > 0 then b.pop / b.hh * b.pop_employed_rate else 0 end),
        educa_hh2 = (case when b.pop > 0 then b.pop_hs_diploma_rate else 0 end),
        educa_hh3 = (case when b.pop > 0 then b.pop_assoc_some_coll_rate else 0 end),
        educa_hh4 = (case when b.pop > 0 then b.pop_coll_degree_rate else 0 end),
        educa_hh5 = (case when b.pop > 0 then b.pop_grad_degree_rate else 0 end),
        pop_age_children = (case when b.pop > 0 then pop_age_5_11_rate else 0 end),
        pop_age_teens = (case when b.pop > 0 then pop_age_12_17_rate else 0 end),
        pop_age_adult = (case when b.pop > 0 then pop_age_18_64_rate else 0 end),
        pop_age_seniors = (case when b.pop > 0 then pop_age65_up_rate else 0 end),

        -- unlike the fields above, these describe population counts for the analysis groups
        pop_children = (case when b.pop > 0 then b.pop * pop_age_5_11_rate else 0 end),
        pop_teen = (case when b.pop > 0 then b.pop * pop_age_12_17_rate else 0 end),
        pop_senior = (case when b.pop > 0 then b.pop * pop_age65_up_rate else 0 end),
        pop_adult = (case when b.pop > 0 then b.pop * pop_age_18_64_rate  else 0 end),

        pop_adult_low = (case when b.pop > 0 then b.pop * pop_age_18_64_rate * (hh_inc_00_10_rate + hh_inc_10_20_rate + hh_inc_20_30_rate + hh_inc_30_40_rate + hh_inc_40_50_rate) else 0 end),
        pop_adult_med = (case when b.pop > 0 then b.pop * pop_age_18_64_rate * (hh_inc_50_60_rate + hh_inc_60_75_rate + hh_inc_75_100_rate) else 0 end),
        pop_adult_high = (case when b.pop > 0 then b.pop * pop_age_18_64_rate * (hh_inc_100_125_rate + hh_inc_125_150_rate + hh_inc_150_200_rate + hh_inc_200p_rate) else 0 end)

    from (
        select a.grid_id, pop, hh, intersection_density_sqmi, c.*
        from (select grid_id, census_id, sum(pop * primary_proportion) as pop, sum(hh * primary_proportion) as hh,
        avg(intersection_density_sqmi) as intersection_density_sqmi
              from {public_health_variables_schema}.{source_grid_table}_join a
              left join {uf_canvas_schema}.{uf_canvas_table} b on a.primary_id = b.id group by grid_id, census_id) a
        LEFT JOIN {census_rate_schema}.{census_rate_table} c on a.census_id = c.id
    ) b where b.grid_id = a.id;
    '''.format(**sql_config_dict)

    execute_sql(pSql)


def run_distance_variables_processes(sql_config_dict):

    geom_analysis_tables = [
        (sql_config_dict['uf_canvas_schema'], sql_config_dict['uf_canvas_table']),
        (sql_config_dict['source_grid_schema'], sql_config_dict['source_grid_table']),
        (sql_config_dict['transit_stop_schema'], sql_config_dict['transit_stop_table']),
        (sql_config_dict['public_health_variables_schema'], sql_config_dict['public_health_variables_table'])
    ]

    add_analysis_geom = '''
    alter table {schema}.{table} drop column if exists analysis_geom cascade;
    alter table {schema}.{table} add column analysis_geom geometry;
    update {schema}.{table} set analysis_geom = st_setSRID(st_transform(wkb_geometry, 3310), 3310);
    create index {schema}_{table}_analysis_geom on {schema}.{table} using gist (analysis_geom);'''

    for schema, table in geom_analysis_tables:
        execute_sql(add_analysis_geom.format(schema=schema, table=table))

    ph_distance_calcs = dict(
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['public_health_variables_schema'],
        target_table=sql_config_dict['public_health_variables_table'],
        target_table_pk='id',
        target_table_query='pop > 0',
        target_geometry_column='analysis_geom',
        maximum_distance=2000
    )

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='emp_education > 0',
        column='school_distance'
    )))

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='emp_restaurant > 0',
        column='restaurant_distance'
    )))

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='emp_retail_services > 0',
        column='retail_distance'
    )))

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['source_grid_schema'] + '.' + sql_config_dict['source_grid_table'],
        source_table_query='acres_parcel_park_open_space > 0',
        column='park_open_space_distance'
    )))

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['source_grid_schema'] + '.' + sql_config_dict['source_grid_table'],
        source_table_query='freeway_arterial_length_feet > 0',
        maximum_distance=500,
        column='freeway_arterial_any'
    )))

    calculate_distance(merge(ph_distance_calcs, dict(
        source_table=sql_config_dict['transit_stop_schema'] + '.' + sql_config_dict['transit_stop_table'],
        source_table_query='route_type = 0 or route_type = 1 or route_type = 2 or route_type = 3',
        column='transit_distance'
    )))


def run_aggregate_within_distance_processes(sql_config_dict):

    aggregate_within_distance(dict(
        source_table=sql_config_dict['uf_canvas_schema'] + '.' + sql_config_dict['uf_canvas_table'],
        source_table_query='du + emp > 0',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['public_health_variables_schema'],
        target_table=sql_config_dict['public_health_variables_table'],
        target_geometry_column='analysis_geom',
        target_table_query='pop > 0',
        target_table_pk='id',
        distance=1000,
        suffix='bldg_sqft',
        aggregation_type='sum',
        variable_field_dict=dict(
            bldg_sqft_res=['bldg_sqft_detsf_sl', 'bldg_sqft_detsf_ll', 'bldg_sqft_attsf', 'bldg_sqft_mf'],
            bldg_sqft_ret1=['bldg_sqft_retail_services', 'bldg_sqft_restaurant', 'bldg_sqft_accommodation',
                            'bldg_sqft_arts_entertainment', 'bldg_sqft_other_services'],
            bldg_sqft_ret=['bldg_sqft_retail_services', 'bldg_sqft_restaurant', 'bldg_sqft_arts_entertainment',
                           'bldg_sqft_other_services'],
            bldg_sqft_off=['bldg_sqft_office_services', 'bldg_sqft_public_admin', 'bldg_sqft_education',
                           'bldg_sqft_medical_services'],
            b1=['bldg_sqft_detsf_sl', 'bldg_sqft_detsf_ll', 'bldg_sqft_attsf', 'bldg_sqft_mf'],
            b2=['bldg_sqft_retail_services', 'bldg_sqft_other_services'],
            b3=['bldg_sqft_restaurant', 'bldg_sqft_arts_entertainment'],
            b4=['bldg_sqft_office_services'],
            b5=['bldg_sqft_public_admin'],
            du_1km_tr=['du'],
            resmix_dens=['acres_parcel_res', 'acres_parcel_mixed_use'],
            far_nonres=['acres_parcel_emp', 'acres_parcel_mixed_use'])
        ))

    aggregate_within_distance(dict(
        source_table=sql_config_dict['source_grid_schema'] + '.' + sql_config_dict['source_grid_table'],
        source_table_query='local_roads_length_feet + secondary_roads_length_feet + freeway_arterial_length_feet + acres_parcel_park_open_space > 0',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['public_health_variables_schema'],
        target_table=sql_config_dict['public_health_variables_table'],
        target_geometry_column='analysis_geom',
        target_table_query='pop > 0',
        target_table_pk='id',
        distance=1000,
        suffix='grid',
        aggregation_type='sum',
        variable_field_dict=dict(
            local_street=['local_roads_length_feet', 'secondary_roads_length_feet'],
            major_street=['freeway_arterial_length_feet'],
            acres_parcel_park_open_space=['acres_parcel_park_open_space'])
    ))

    aggregate_within_distance(dict(
        source_table=sql_config_dict['transit_stop_schema'] + '.' + sql_config_dict['transit_stop_table'],
        source_table_query='route_type = 0 or route_type = 1 or route_type = 2 or route_type = 3',
        source_geometry_column='analysis_geom',
        target_table_schema=sql_config_dict['public_health_variables_schema'],
        target_table=sql_config_dict['public_health_variables_table'],
        target_geometry_column='analysis_geom',
        target_table_query='pop > 0',
        target_table_pk='id',
        distance=1000,
        suffix='transit',
        aggregation_type='count',
        variable_field_dict=dict(
            transit_count=['wkb_geometry'])
    ))

    geom_analysis_tables = [
        (sql_config_dict['uf_canvas_schema'], sql_config_dict['uf_canvas_table']),
        (sql_config_dict['source_grid_schema'], sql_config_dict['source_grid_table']),
        (sql_config_dict['transit_stop_schema'], sql_config_dict['transit_stop_table']),
        (sql_config_dict['public_health_variables_schema'], sql_config_dict['public_health_variables_table'])
    ]

    for schema, table in geom_analysis_tables:
        execute_sql('''DROP INDEX {schema}.{schema}_{table}_analysis_geom;
            Alter Table {schema}.{table} drop column analysis_geom;'''.format(schema=schema, table=table))


def run_aggregate_within_variable_distance_processes(sql_config_dict):

    drop_table('{public_health_variables_schema}.{uf_canvas_table}_variable'.format(
        public_health_variables_schema=sql_config_dict['public_health_variables_schema'],
        uf_canvas_table=sql_config_dict['uf_canvas_table']))

    pSql = '''
    create table {public_health_variables_schema}.{uf_canvas_table}_variable
    as select
      a.id, st_transform(a.wkb_geometry, 3310) as wkb_geometry, cast(a.attractions_hbw * 1609.0 as float) as distance,
      sum(du * st_area(st_intersection(a.wkb_geometry, b.wkb_geometry)) / st_area(b.wkb_geometry)) as du_variable,
      sum(emp * st_area(st_intersection(a.wkb_geometry, b.wkb_geometry)) / st_area(b.wkb_geometry)) as emp_variable
    from
      (select id, wkb_geometry, attractions_hbw from {trip_lengths_schema}.{trip_lengths_table}) a,
      (select wkb_geometry, du, emp from {uf_canvas_schema}.{uf_canvas_table} where du + emp > 0) b
    where st_intersects(b.wkb_geometry, a.wkb_geometry) group by a.id, a.wkb_geometry, a.attractions_hbw;
    '''.format(public_health_variables_schema=sql_config_dict['public_health_variables_schema'],
               uf_canvas_schema=sql_config_dict['uf_canvas_schema'],
               uf_canvas_table=sql_config_dict['uf_canvas_table'],
               trip_lengths_schema=sql_config_dict['trip_lengths_schema'],
               trip_lengths_table=sql_config_dict['trip_lengths_table'])

    execute_sql(pSql)

    add_geom_idx(sql_config_dict['public_health_variables_schema'], sql_config_dict['uf_canvas_table'] + '_variable')
    add_primary_key(sql_config_dict['public_health_variables_schema'], sql_config_dict['uf_canvas_table'] + '_variable', 'id')

    add_analysis_geom(sql_config_dict['public_health_variables_schema'], sql_config_dict['public_health_variables_table'])

    aggregate_within_variable_distance(dict(
        source_table=sql_config_dict['public_health_variables_schema'] + '.' + sql_config_dict['uf_canvas_table'] + '_variable',
        source_table_query='id is not null',
        target_table_schema=sql_config_dict['public_health_variables_schema'],
        target_table=sql_config_dict['public_health_variables_table'],
        target_table_query='pop > 0',
        target_table_pk='id',
        suffix='variable',
        aggregation_type='sum',
        variable_field_list=['du_variable', 'emp_variable']
    ))

    drop_table('{public_health_variables_schema}.{uf_canvas_table}_variable'.format(
        public_health_variables_schema=sql_config_dict['public_health_variables_schema'],
        uf_canvas_table=sql_config_dict['uf_canvas_table']))


def populate_transformations_and_indices(sql_config_dict):

    ##TRANSFORMING PRELIMINARY AND MODEL VARIABLES STEPS 1 AND 2
    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
        resmix_dens = (case
          when resmix_dens = 0
            then 0
          else ln((du_1km_tr / resmix_dens) + 1) end),
        bldg_sqft_ret = bldg_sqft_ret ^ 0.25,
        b1 = (case when b1 = 0 then 1E-24 else b1 end),
        b2 = (case when b2 = 0 then 1E-24 else b2 end),
        b3 = (case when b3 = 0 then 1E-24 else b3 end),
        b4 = (case when b4 = 0 then 1E-24 else b4 end),
        b5 = (case when b5 = 0 then 1E-24 else b5 end),
        local_street = local_street / 5280,
        major_street = (major_street / 5280) ^ 0.5,
        far_nonres = (case when far_nonres = 0 then 0 else ((bldg_sqft_ret1 + bldg_sqft_off) / (far_nonres * 43560)) ^ 0.25 end),
        rail_any = (case when rail_any > 0 then 1 else 0 end),
        freeway_arterial_any = (case when freeway_arterial_any <500 then 1 else 0 end),
        transit_distance = transit_distance ^ 0.25,
        transit_count = transit_count ^ 0.5,
        school_distance = school_distance ^ 0.25,
        retail_distance = retail_distance ^ 0.5,
        intersection_density_sqmi = intersection_density_sqmi ^ 0.5,
        park_open_space_distance = park_open_space_distance ^ 0.5,
        acres_parcel_park_open_space = acres_parcel_park_open_space ^ 0.25,
        du_variable = du_variable ^ 0.25,
        emp_variable = emp_variable ^ 0.25
    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)

    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
    du_1km_tr = du_1km_tr ^ 0.25,
    a = b1 + b2 + b3 + b4 + b5
    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)

    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
    mix5 = (case
          when a > 0 and ((b1/a)*LN(b1/a) + (b2/a)*LN(b2/a) + (b3/a)*LN(b3/a) + (b4/a)*LN(b4/a) + (b5/a)*LN(b5/a)) / (-1 * ln(5)) < 0.0001
            then 0
          when a > 0 and ((b1/a)*LN(b1/a) + (b2/a)*LN(b2/a) + (b3/a)*LN(b3/a) + (b4/a)*LN(b4/a) + (b5/a)*LN(b5/a)) / (-1 * ln(5)) > 0.999
            then 0
          when a > 0 and ((b1/a)*LN(b1/a) + (b2/a)*LN(b2/a) + (b3/a)*LN(b3/a) + (b4/a)*LN(b4/a) + (b5/a)*LN(b5/a)) / (-1 * ln(5)) > 0.0001 and
            ((b1/a)*LN(b1/a) + (b2/a)*LN(b2/a) + (b3/a)*LN(b3/a) + (b4/a)*LN(b4/a) + (b5/a)*LN(b5/a)) / (-1 * ln(5)) < 0.999
            then ((((b1/a)*LN(b1/a) + (b2/a)*LN(b2/a) + (b3/a)*LN(b3/a) + (b4/a)*LN(b4/a) + (b5/a)*LN(b5/a))) / (-1 * ln(5))) ^ 0.5
          else 0
          end)
    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)

    ##CALCULATING PRELIMINARY INDEX VARIABLES

    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
        res_index = (resmix_dens - 1.82) / 0.9478 + (du_1km_tr - 7.451) / 1.8664,
        com_index = 2 * ((bldg_sqft_ret - 24.38) / 10.4543) + 2 * ((far_nonres - 0.5938) / 0.2064) - (retail_distance - 13.91) / 13.5014 - (restaurant_distance - 599.4) / 670.6584,
        park_access = (acres_parcel_park_open_space - 1.704) / 1.0956 - (park_open_space_distance - 18.48) / 11.3701,
        regional_access = (du_variable - 24.92) / 6.0667 + (emp_variable - 26.13) / 7.2701,
        network_index = (intersection_density_sqmi - 9.186) / 3.5870 + (local_street - 29.73) / 10.5599,
        transit_access = 2*((transit_count - 3.769) / 3.9104) - (transit_distance - 4.602) / 1.8653,
        major_road_index = (major_street - 0.6099) / 0.8575 + (freeway_arterial_any - 0.2126) / 0.4092
    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)


    ##CALCULATING WALK INDEX VARIABLE
    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
        walk_index = 2 * ((res_index - 0.000221) / 1.9586) + 1.5 * ((network_index - 1.65E-16) / 1.846573714) + (com_index - 0.0005076) / 5.3122 + 0.5*((mix5 - 0.4379) / 0.1840)
    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)


    ##CALCULATING WALK INDEX VARIATIONS
    pSql = '''
    update {public_health_variables_schema}.{public_health_variables_table} a set
      walk_index_chts_senior_walk_any = (12.69/6.59) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_senior_auto_min = (7.09/2.63) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_teens_walk_any = (8.24/3.34) * ((walk_index - 0.0005914) / 4.4684) + (4.91/3.34) * ((transit_access - 2.727E-16) / 2.8399) + (rail_any - 0.09589) / 0.2944,
      walk_index_chts_child_walk_any = (8.94/5.81) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_adult_bike_any = (8.22/2.19) * ((walk_index - 0.0005914) / 4.4684) + (regional_access) / 1.9944,
      walk_index_chts_adult_walk_min = (9.79/5.56) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_senior_walk_min = (2.43/2.34) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_teens_walk_min = (5.12/2.42) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chts_adult_auto_min = (7.99/2.11) * ((walk_index - 0.0005914) / 4.4684) + (rail_any - 0.09589) / 0.2944,
      walk_index_chis_adult_modPA_any = (8.57/2.94) * ((walk_index - 0.0005914) / 4.4684) + (4.36/2.94) * ((transit_access - 2.727E-16) / 2.8399) + ((rail_any - 0.09589) / 0.2944) + (3.22/2.94) * ((regional_access) / 1.9944),
      walk_index_chis_adult_overweight = (walk_index - 0.0005914) / 4.4684 + (7.92/3.15) * ((regional_access) / 1.9944),
      walk_index_chis_senior_overweight = (walk_index - 0.0005914) / 4.4684 + (3.15/2.01) * ((regional_access) / 1.9944),
      walk_index_chis_adult_obese = (walk_index - 0.0005914) / 4.4684 + (6.07/2.58) * ((regional_access) / 1.9944),
      walk_index_chis_senior_gh = (2.74/2.14) * ((walk_index - 0.0005914) / 4.4684) + (regional_access) / 1.9944,
      walk_index_chis_senior_walk_le_min = (2.82/2.08) * ((walk_index - 0.0005914) / 4.4684) + (transit_access - 2.727E-16) / 2.8399,
      walk_index_chis_adult_modPA_min = (7.96/1.98) * ((walk_index - 0.0005914) / 4.4684) + (4.32/1.98) * ((transit_access - 2.727E-16) / 2.8399) + (rail_any - 0.09589) / 0.2944,
      walk_index_chis_adult_bmi = (walk_index - 0.0005914) / 4.4684 + (4.47/3.50) * ((transit_access - 2.727E-16) / 2.8399) + (8.94/3.50) * ((regional_access) / 1.9944),
      walk_index_chis_child_PA60 =(4.25/2.12) * ((walk_index - 0.0005914) / 4.4684) + (regional_access) / 1.9944,
      walk_index_chis_child_walk_school = (8.13/3.17)*((walk_index - 0.0005914) / 4.4684) + (regional_access) / 1.9944

    where pop > 0;
    '''.format(**sql_config_dict)

    execute_sql(pSql)
