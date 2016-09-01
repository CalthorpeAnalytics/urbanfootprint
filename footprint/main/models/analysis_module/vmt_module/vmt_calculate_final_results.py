
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

import math

__author__ = 'calthorpe_analytics'


def calculate_final_vmt_results(vmt_feature):
    tF_trips_total = vmt_feature['trips_hbw'] + vmt_feature['trips_hbo'] + vmt_feature['trips_nhb']
    if tF_trips_total == 0:
        vmt_feature['final_prod_hbw'] = 0.0
        vmt_feature['final_prod_hbo'] = 0.0
        vmt_feature['final_prod_nhb'] = 0.0

        vmt_feature['final_attr_hbw'] = 0.0
        vmt_feature['final_attr_hbo'] = 0.0
        vmt_feature['final_attr_nhb'] = 0.0

        vmt_feature['raw_trips_total'] = 0.0
        vmt_feature['vmt_daily'] = 0.0
        vmt_feature['vmt_daily_w_trucks'] = 0.0
        vmt_feature['vmt_daily_per_capita'] = 0.0
        vmt_feature['vmt_daily_per_hh'] = 0.0
        vmt_feature['vmt_annual'] = 0.0
        vmt_feature['vmt_annual_w_trucks'] = 0.0
        vmt_feature['vmt_annual_per_capita'] = 0.0
        vmt_feature['vmt_annual_per_hh'] = 0.0
        vmt_feature['vmt_daily_regression'] = 0.0
        vmt_feature['vmt_daily_mxd'] = 0.0
        vmt_feature['vmt_daily_raw'] = 0.0
        vmt_feature['regression_ratio'] = 0.0
        vmt_feature['pop_den_ratio'] = 0.0
        vmt_feature['hh_den_ratio'] = 0.0
        vmt_feature['emp_den_ratio'] = 0.0
        vmt_feature['emp30m_ratio'] = 0.0
        vmt_feature['auto_ownshp_ratio'] = 0
        vmt_feature['pop_den'] = 0.0
        vmt_feature['hh_den'] = 0.0
        vmt_feature['emp_den'] = 0.0
        vmt_feature['emp30m_den'] = 0.0
        vmt_feature['auto_ownshp_den'] = 0
        vmt_feature['external_veh_trips_reduction'] = 0.0
        vmt_feature['internal_capture_trips_total'] = 0.0
        vmt_feature['walking_trips_total'] = 0.0
        vmt_feature['transit_trips_total'] = 0.0
        vmt_feature['icpm_hbw'] = 0.0
        vmt_feature['icpm_hbo'] = 0.0
        vmt_feature['icpm_nhb'] = 0.0
        vmt_feature['wtpm_hbw'] = 0.0
        vmt_feature['wtpm_hbo'] = 0.0
        vmt_feature['wtpm_nhb'] = 0.0
        vmt_feature['ttpm_hbw'] = 0.0
        vmt_feature['ttpm_hbo'] = 0.0
        vmt_feature['ttpm_nhb'] = 0.0
        vmt_feature['trips_hbw_w_trucks'] = 0.0
        vmt_feature['trips_hbo_w_trucks'] = 0.0
        vmt_feature['trips_nhb_w_trucks'] = 0.0
        vmt_feature['trips_hbw_regression'] = 0.0
        vmt_feature['trips_hbo_regression'] = 0.0
        vmt_feature['trips_nhb_regression'] = 0.0


        return vmt_feature

    tF_num_icpm_hbw = vmt_feature['trips_hbw'] * (
        math.exp(vmt_feature['icpm_hbw']) / (math.exp(vmt_feature['icpm_hbw']) + 1.0))
    tF_num_icpm_hbo = vmt_feature['trips_hbo'] * (
        math.exp(vmt_feature['icpm_hbo']) / (math.exp(vmt_feature['icpm_hbo']) + 1.0))
    tF_num_icpm_nhb = vmt_feature['trips_nhb'] * (
        math.exp(vmt_feature['icpm_nhb']) / (math.exp(vmt_feature['icpm_nhb']) + 1.0))
    tF_num_icpm_total = tF_num_icpm_hbw + tF_num_icpm_hbo + tF_num_icpm_nhb

    tF_num_wtpm_hbw = (vmt_feature['trips_hbw'] - tF_num_icpm_hbw) * (
        math.exp(vmt_feature['wtpm_hbw']) / (math.exp(vmt_feature['wtpm_hbw']) + 1.0))
    tF_num_wtpm_hbo = (vmt_feature['trips_hbo'] - tF_num_icpm_hbo) * (
        math.exp(vmt_feature['wtpm_hbo']) / (math.exp(vmt_feature['wtpm_hbo']) + 1.0))
    tF_num_wtpm_nhb = (vmt_feature['trips_nhb'] - tF_num_icpm_nhb) * (
        math.exp(vmt_feature['wtpm_nhb']) / (math.exp(vmt_feature['wtpm_nhb']) + 1.0))
    tF_num_wtpm_total = tF_num_wtpm_hbw + tF_num_wtpm_hbo + tF_num_wtpm_nhb

    tF_num_ttpm_hbw = (vmt_feature['trips_hbw'] - tF_num_icpm_hbw) * (
        math.exp(vmt_feature['ttpm_hbw']) / (math.exp(vmt_feature['ttpm_hbw']) + 1.0))
    tF_num_ttpm_hbo = (vmt_feature['trips_hbo'] - tF_num_icpm_hbo) * (
        math.exp(vmt_feature['ttpm_hbo']) / (math.exp(vmt_feature['ttpm_hbo']) + 1.0))
    tF_num_ttpm_nhb = (vmt_feature['trips_nhb'] - tF_num_icpm_nhb) * (
        math.exp(vmt_feature['ttpm_nhb']) / (math.exp(vmt_feature['ttpm_nhb']) + 1.0))

    tF_num_ttpm_total = tF_num_ttpm_hbw + tF_num_ttpm_hbo + tF_num_ttpm_nhb

    tF_net_ixxi_hbw = vmt_feature['trips_hbw'] - (tF_num_icpm_hbw + tF_num_wtpm_hbw + tF_num_ttpm_hbw)
    tF_net_ixxi_hbo = vmt_feature['trips_hbo'] - (tF_num_icpm_hbo + tF_num_wtpm_hbo + tF_num_ttpm_hbo)
    tF_net_ixxi_nhb = vmt_feature['trips_nhb'] - (tF_num_icpm_nhb + tF_num_wtpm_nhb + tF_num_ttpm_nhb)
    tF_net_ixxi_total = tF_net_ixxi_hbw + tF_net_ixxi_hbo + tF_net_ixxi_nhb

    tF_external_veh_trips_reduction = 1.0 - (tF_net_ixxi_total / tF_trips_total)

    ##---------------------------------------------------

    if vmt_feature['prod_hbw'] is not None:
        tF_prod_trips_hbw = vmt_feature['prod_hbw']
    else:
        tF_prod_trips_hbw = 0.0

    if vmt_feature['prod_hbo'] is not None:
        tF_prod_trips_hbo = vmt_feature['prod_hbo']
    else:
        tF_prod_trips_hbo = 0.0

    if vmt_feature['prod_nhb'] is not None:
        tF_prod_trips_nhb = vmt_feature['prod_nhb']
    else:
        tF_prod_trips_nhb = 0.0

    ##------------
    if vmt_feature['attr_hbw'] is not None:
        tF_attr_trips_hbw = vmt_feature['attr_hbw']
    else:
        tF_attr_trips_hbw = 0

    if vmt_feature['attr_hbo'] is not None:
        tF_attr_trips_hbo = vmt_feature['attr_hbo']
    else:
        tF_attr_trips_hbo = 0

    if vmt_feature['attr_nhb'] is not None:
        tF_attr_trips_nhb = vmt_feature['attr_nhb']
    else:
        tF_attr_trips_nhb = 0

    ##------------

    tF_prod_hbw = tF_net_ixxi_hbw * vmt_feature['ite_prod_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * tF_prod_trips_hbw / 2.0
    tF_prod_hbo = tF_net_ixxi_hbo * vmt_feature['ite_prod_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_prod_trips_hbo / 2.0
    tF_prod_nhb = tF_net_ixxi_nhb * vmt_feature['ite_prod_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_prod_trips_nhb / 2.0

    tF_attr_hbw = tF_net_ixxi_hbw * vmt_feature['ite_attr_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * (tF_attr_trips_hbw / 2.0)
    tF_attr_hbo = tF_net_ixxi_hbo * vmt_feature['ite_attr_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_attr_trips_hbo / 2.0
    tF_attr_nhb = tF_net_ixxi_nhb * vmt_feature['ite_attr_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_attr_trips_nhb / 2.0

    tF_hbw_total = tF_prod_hbw + tF_attr_hbw
    tF_hbo_total = tF_prod_hbo + tF_attr_hbo
    tF_nhb_total = tF_prod_nhb + tF_attr_nhb

    tF_grand_total = tF_hbw_total + tF_hbo_total + tF_nhb_total
    tF_grand_total_trucks = tF_grand_total * (1 + float(vmt_feature['truck_adjustment_factor']))


    ##------------Raw VMT

    tF_prod_hbw_raw = vmt_feature['trips_hbw'] * vmt_feature['ite_prod_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * tF_prod_trips_hbw / 2.0
    tF_prod_hbo_raw = vmt_feature['trips_hbo'] * vmt_feature['ite_prod_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_prod_trips_hbo / 2.0
    tF_prod_nhb_raw = vmt_feature['trips_nhb'] * vmt_feature['ite_prod_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_prod_trips_nhb / 2.0

    tF_attr_hbw_raw = vmt_feature['trips_hbw'] * vmt_feature['ite_attr_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * (tF_attr_trips_hbw / 2.0)
    tF_attr_hbo_raw = vmt_feature['trips_hbo'] * vmt_feature['ite_attr_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_attr_trips_hbo / 2.0
    tF_attr_nhb_raw = vmt_feature['trips_nhb'] * vmt_feature['ite_attr_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_attr_trips_nhb / 2.0

    tF_hbw_total_raw = tF_prod_hbw_raw + tF_attr_hbw_raw
    tF_hbo_total_raw = tF_prod_hbo_raw + tF_attr_hbo_raw
    tF_nhb_total_raw = tF_prod_nhb_raw + tF_attr_nhb_raw

    tF_grand_total_raw = tF_hbw_total_raw + tF_hbo_total_raw + tF_nhb_total_raw


    #regression calculations for adjustment to vmt

    auto_ownshp = vmt_feature['autos_per_hh']
    if vmt_feature['hh'] > 0.0:
        hh_den = vmt_feature['pop'] / vmt_feature['hh']
    elif vmt_feature['pop'] is None or vmt_feature['hh'] is None:
        hh_den = 0.0
    else:
        hh_den = 0.0

    if vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_emp'] + vmt_feature['acres_parcel_mixed'] > 0.0:
        pop_den = vmt_feature['pop'] / (
            vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_emp'] + vmt_feature['acres_parcel_mixed'])
    elif vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_emp'] + vmt_feature[
        'acres_parcel_mixed'] is None or vmt_feature[
        'pop'] is None:
        pop_den = 0.0
    else:
        pop_den = 0.0

    if vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_emp'] + vmt_feature['acres_parcel_mixed'] > 0.0:
        emp_den = (vmt_feature['emp_retail'] + vmt_feature['emp_restaccom'] + vmt_feature['emp_arts_entertainment'] +
                   vmt_feature['emp_office'] + vmt_feature['emp_public'] + vmt_feature['emp_industry']) / (
                      vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_emp'] + vmt_feature['acres_parcel_mixed'])
    elif (vmt_feature['emp_retail'] + vmt_feature['emp_restaccom'] + vmt_feature['emp_arts_entertainment'] +
              vmt_feature[
                  'emp_office'] + vmt_feature[
        'emp_public'] + vmt_feature['emp_industry']) is None or vmt_feature['acres_parcel_res'] + vmt_feature[
        'acres_parcel_emp'] + \
            vmt_feature['acres_parcel_mixed'] is None:
        emp_den = 0.0
    else:
        emp_den = 0.0

    if vmt_feature['emp30m_transit'] is None or vmt_feature['total_employment']==0:
        emp30m_den = 0.0
    else:
        emp30m_den = vmt_feature['emp30m_transit'] / vmt_feature['total_employment']

    # todo: document what these numbers are :)
    auto_ownshp_ratio = (auto_ownshp / 1.89) * 0.446
    hh_den_ratio = (hh_den / 2.33) * 0.371
    pop_den_ratio = (pop_den / 10.957) * -0.023
    emp_den_ratio = (emp_den / 5.055) * -0.015
    emp30m_ratio = emp30m_den * -0.439

    regression_ratio = 0.225 + auto_ownshp_ratio + hh_den_ratio + pop_den_ratio + emp_den_ratio + emp30m_ratio

    if 1 - regression_ratio > tF_external_veh_trips_reduction:
        auto_ownshp_ratio = vmt_feature['hh_avg_veh']
        regression_ratio = 0.225 + auto_ownshp_ratio + hh_den_ratio + pop_den_ratio + emp_den_ratio + emp30m_ratio

        if regression_ratio < 1 - tF_external_veh_trips_reduction:
            regression_ratio = 1 - tF_external_veh_trips_reduction
            vmt_feature['regression_ratio'] = regression_ratio
        else:
            vmt_feature['regression_ratio'] = regression_ratio
    else:
        vmt_feature['regression_ratio'] = regression_ratio

        #if regression_ratio < 1.3:
        #regression_ratio = 1.3
        #vmt_feature['regression_ratio'] = regression_ratio
        #else:
        #vmt_feature['regression_ratio'] = regression_ratio

    vmt_feature['pop_den_ratio'] = pop_den_ratio
    vmt_feature['hh_den_ratio'] = hh_den_ratio
    vmt_feature['emp_den_ratio'] = emp_den_ratio
    vmt_feature['emp30m_ratio'] = emp30m_ratio
    vmt_feature['auto_ownshp_ratio'] = auto_ownshp_ratio

    vmt_feature['pop_den'] = pop_den
    vmt_feature['hh_den'] = hh_den
    vmt_feature['emp_den'] = emp_den
    vmt_feature['emp30m_den'] = emp30m_den
    vmt_feature['auto_ownshp_den'] = (auto_ownshp / 1.89)
    #regression adjusted vmt

    tF_prod_hbw_rg = (vmt_feature['trips_hbw'] * regression_ratio) * vmt_feature['ite_prod_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * tF_prod_trips_hbw / 2.0
    tF_prod_hbo_rg = (vmt_feature['trips_hbo'] * regression_ratio) * vmt_feature['ite_prod_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_prod_trips_hbo / 2.0
    tF_prod_nhb_rg = (vmt_feature['trips_nhb'] * regression_ratio) * vmt_feature['ite_prod_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_prod_trips_nhb / 2.0

    tF_attr_hbw_rg = (vmt_feature['trips_hbw'] * regression_ratio) * vmt_feature['ite_attr_hbw'] / (
        vmt_feature['ite_prod_hbw'] + vmt_feature['ite_attr_hbw'] ) * tF_attr_trips_hbw / 2.0
    tF_attr_hbo_rg = (vmt_feature['trips_hbo'] * regression_ratio) * vmt_feature['ite_attr_hbo'] / (
        vmt_feature['ite_prod_hbo'] + vmt_feature['ite_attr_hbo'] ) * tF_attr_trips_hbo / 2.0
    tF_attr_nhb_rg = (vmt_feature['trips_nhb'] * regression_ratio) * vmt_feature['ite_attr_nhb'] / (
        vmt_feature['ite_prod_nhb'] + vmt_feature['ite_attr_nhb'] ) * tF_attr_trips_nhb / 2.0

    tF_hbw_total_rg = tF_prod_hbw_rg + tF_attr_hbw_rg
    tF_hbo_total_rg = tF_prod_hbo_rg + tF_attr_hbo_rg
    tF_nhb_total_rg = tF_prod_nhb_rg + tF_attr_nhb_rg

    tF_grand_total_rg = tF_hbw_total_rg + tF_hbo_total_rg + tF_nhb_total_rg
    tF_grand_total_rg_trucks = tF_grand_total_rg * (1 + float(vmt_feature['truck_adjustment_factor']))

    if tF_external_veh_trips_reduction < 0.1:
        final_vmt_total = tF_grand_total_rg
    else:
        final_vmt_total = tF_grand_total

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_hbw_w_trucks'] = vmt_feature['trips_hbw'] * regression_ratio * (
            1 + float(vmt_feature['truck_adjustment_factor']))
    else:
        vmt_feature['trips_hbw_w_trucks'] = vmt_feature['trips_hbw'] * (1 + float(vmt_feature['truck_adjustment_factor']))
    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_hbo_w_trucks'] = vmt_feature['trips_hbo'] * regression_ratio * (
            1 + float(vmt_feature['truck_adjustment_factor']))
    else:
        vmt_feature['trips_hbo_w_trucks'] = vmt_feature['trips_hbo'] * (1 + float(vmt_feature['truck_adjustment_factor']))

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_nhb_w_trucks'] = vmt_feature['trips_nhb'] * regression_ratio * (
            1 + float(vmt_feature['truck_adjustment_factor']))
    else:
        vmt_feature['trips_nhb_w_trucks'] = vmt_feature['trips_nhb'] * (1 + float(vmt_feature['truck_adjustment_factor']))

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_hbw_regression'] = vmt_feature['trips_hbw'] * regression_ratio
    else:
        vmt_feature['trips_hbw_regression'] = vmt_feature['trips_hbw']

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_hbo_regression'] = vmt_feature['trips_hbo'] * regression_ratio
    else:
        vmt_feature['trips_hbo_regression'] = vmt_feature['trips_hbo']

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['trips_nhb_regression'] = vmt_feature['trips_nhb'] * regression_ratio
    else:
        vmt_feature['trips_nhb_regression'] = vmt_feature['trips_nhb']

    if tF_external_veh_trips_reduction < 0.1:
        final_vmt_total_trucks = tF_grand_total_rg_trucks
    else:
        final_vmt_total_trucks = tF_grand_total_trucks

    #productions by type
    if tF_external_veh_trips_reduction < 0.1:
        final_prod_hbw = tF_prod_hbw_rg
    else:
        final_prod_hbw = tF_prod_hbw

    if tF_external_veh_trips_reduction < 0.1:
        final_prod_hbo = tF_prod_hbo_rg
    else:
        final_prod_hbo = tF_prod_hbo

    if tF_external_veh_trips_reduction < 0.1:
        final_prod_nhb = tF_prod_nhb_rg
    else:
        final_prod_nhb = tF_prod_nhb

    #attractions by type
    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['final_attr_hbw'] = tF_attr_hbw_rg
    else:
        vmt_feature['final_attr_hbw'] = tF_attr_hbw

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['final_attr_hbo'] = tF_attr_hbo_rg
    else:
        vmt_feature['final_attr_hbo'] = tF_attr_hbo

    if tF_external_veh_trips_reduction < 0.1:
        vmt_feature['final_attr_nhb'] = tF_attr_nhb_rg
    else:
        vmt_feature['final_attr_nhb'] = tF_attr_nhb

    if (vmt_feature['qmb_acres_parcel_res_total'] + vmt_feature['qmb_acres_parcel_emp_total'] + vmt_feature[
        'qmb_acres_parcel_mixed_total']) != 0:
        vmt_feature['pop_emp_sqmi'] = ( vmt_feature['qmb_pop_total'] + vmt_feature['qmb_pop_total']) / (
            vmt_feature['qmb_acres_parcel_res_total'] + vmt_feature['qmb_acres_parcel_emp_total'] + vmt_feature[
                'qmb_acres_parcel_mixed_total'] ) * 640.0
    else:
        vmt_feature['pop_emp_sqmi'] = 0

    vmt_feature['intersections_sqmi'] = vmt_feature['intersections_qtrmi']

    vmt_feature['prop_regional_emp30m_transit'] = emp30m_den

    if vmt_feature['hh_within_quarter_mile_trans'] > 0:   ##23mar
        vmt_feature['prop_hh_within_quarter_mile_trans'] = 1.0
    else:
        vmt_feature['prop_hh_within_quarter_mile_trans'] = 0.0

    vmt_feature['icpm_hbw'] = tF_num_icpm_hbw
    vmt_feature['icpm_hbo'] = tF_num_icpm_hbo
    vmt_feature['icpm_nhb'] = tF_num_icpm_nhb
    vmt_feature['wtpm_hbw'] = tF_num_wtpm_hbw
    vmt_feature['wtpm_hbo'] = tF_num_wtpm_hbo
    vmt_feature['wtpm_nhb'] = tF_num_wtpm_nhb
    vmt_feature['ttpm_hbw'] = tF_num_ttpm_hbw
    vmt_feature['ttpm_hbo'] = tF_num_ttpm_hbo
    vmt_feature['ttpm_nhb'] = tF_num_ttpm_nhb
    vmt_feature['external_veh_trips_reduction'] = tF_external_veh_trips_reduction

    vmt_feature['vmt_daily_regression'] = tF_grand_total_rg
    vmt_feature['vmt_daily_mxd'] = tF_grand_total
    vmt_feature['vmt_daily_raw'] = tF_grand_total_raw

    ##----------------------------------------
    vmt_feature['final_prod_hbw'] = final_prod_hbw
    vmt_feature['final_prod_hbo'] = final_prod_hbo
    vmt_feature['final_prod_nhb'] = final_prod_nhb

    ##-----------------------------------------
    vmt_feature['internal_capture_trips_total'] = tF_num_icpm_total
    vmt_feature['walking_trips_total'] = tF_num_wtpm_total
    vmt_feature['transit_trips_total'] = tF_num_ttpm_total

    vmt_feature['raw_trips_total'] = tF_trips_total
    vmt_feature['vmt_daily'] = final_vmt_total
    vmt_feature['vmt_daily_w_trucks'] = final_vmt_total_trucks

    if float(vmt_feature['pop']) > 0:
        vmt_feature['vmt_daily_per_capita'] = (
            float(((final_prod_hbw + final_prod_hbo) * 2)) / float(vmt_feature['pop']))
    else:
        vmt_feature['vmt_daily_per_capita'] = 0

    if float(vmt_feature['hh']) > 0:
        vmt_feature['vmt_daily_per_hh'] = (
            float(((final_prod_hbw + final_prod_hbo) * 2)) / float(vmt_feature['hh']))
    else:
        vmt_feature['vmt_daily_per_hh'] = 0

    vmt_feature['vmt_annual'] = final_vmt_total * 347.0
    vmt_feature['vmt_annual_w_trucks'] = final_vmt_total_trucks * 347.0

    if float(vmt_feature['pop']) > 0:
        vmt_feature['vmt_annual_per_capita'] = (
            float((((final_prod_hbw + final_prod_hbo) * 2) * 347.0)) / float(vmt_feature['pop']))
    else:
        vmt_feature['vmt_annual_per_capita'] = 0

    if float(vmt_feature['hh']) > 0:
        vmt_feature['vmt_annual_per_hh'] = (
            float((((final_prod_hbw + final_prod_hbo) * 2) * 347.0)) / float(vmt_feature['hh']))
    else:
        vmt_feature['vmt_annual_per_hh'] = 0

    return vmt_feature
