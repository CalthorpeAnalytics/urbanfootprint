
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

from footprint.main.models.analysis_module.vmt_module.vmt_model_constants import cICPM_hbw_110, cICPM_hbw_113, cICPM_hbw_114, cICPM_hbw_107, cICPM_hbo_109, cICPM_hbo_110, cICPM_hbo_112, cICPM_hbo_113, cICPM_hbo_114, cICPM_hbo_107, cICPM_nhb_107, cICPM_nhb_108, cICPM_nhb_109, cICPM_nhb_112, cICPM_nhb_113, cICPM_nhb_114, cWTPM_hbw_121, cWTPM_hbw_124, cWTPM_hbw_127, cWTPM_hbw_128, cWTPM_hbw_129, cWTPM_hbo_121, cWTPM_hbo_122, cWTPM_hbo_123, cWTPM_hbo_124, cWTPM_hbo_126, cWTPM_hbo_127, cWTPM_hbo_128, cWTPM_hbo_129, cWTPM_nhb_121, cWTPM_nhb_123, cWTPM_nhb_126, cWTPM_nhb_127, cWTPM_nhb_128, cWTPM_nhb_129, cTTPM_hbw_138, cTTPM_hbw_136, cTTPM_hbw_139, cTTPM_hbw_140, cTTPM_hbw_141, cTTPM_hbw_142, cTTPM_hbo_136, cTTPM_hbo_137, cTTPM_hbo_140, cTTPM_hbo_141, cTTPM_hbo_142, cTTPM_nhb_136, cTTPM_nhb_139, cTTPM_nhb_142
from footprint.main.models.analysis_module.vmt_module.vmt_auto_ownership_model import generate_predicted_auto_ownership

__author__ = 'calthorpe_analytics'


def calculate_log_odds(vmt_feature):
    autos_per_hh = generate_predicted_auto_ownership(vmt_feature)
    if autos_per_hh < vmt_feature['hh_avg_veh'] * 0.5 or autos_per_hh > 5.0:
        autos_per_hh = vmt_feature['hh_avg_veh']

    tRes = 0

    ##-- use qmb
    tMXD_total_pop = vmt_feature['qmb_pop_total']

    ##-- use single cell and qmb
    tMXD_total_emp_qmb = vmt_feature['qmb_emp_total']
    if vmt_feature['emp_retail'] is None: vmt_feature['emp_retail'] = 0

    ##-- 30Aug11 no more service category, restaurant is added
    if vmt_feature['emp_restaccom'] is None: vmt_feature['emp_restaccom'] = 0
    if vmt_feature['emp_arts_entertainment'] is None: vmt_feature['emp_arts_entertainment'] = 0

    if vmt_feature['emp_office'] is None: vmt_feature['emp_office'] = 0
    if vmt_feature['emp_public'] is None: vmt_feature['emp_public'] = 0
    if vmt_feature['emp_industry'] is None: vmt_feature['emp_industry'] = 0

    tMXD_total_emp_cell = vmt_feature['emp_retail'] + vmt_feature['emp_arts_entertainment'] + vmt_feature[
        'emp_restaccom'] + \
                          vmt_feature['emp_office'] \
                          + vmt_feature['emp_public'] + vmt_feature['emp_industry']

    if (float(vmt_feature['acres_parcel_res']) + float(vmt_feature['acres_parcel_emp']) + float(
            vmt_feature['acres_parcel_mixed'])) <= 0:
        tMXD_area = 0
    else:
        tMXD_area = (float(vmt_feature['acres_parcel_res']) + float(vmt_feature['acres_parcel_emp']) + float(
            vmt_feature['acres_parcel_mixed'])) / 640.0

    if (0.2 * (tMXD_total_pop + tMXD_total_emp_qmb) ) <= 0:
        tCT = 0
    else:
        tCT = ( 1.0 - abs(0.2 * tMXD_total_pop - tMXD_total_emp_qmb) / (0.2 * tMXD_total_pop + tMXD_total_emp_qmb))
    tMXD_jobs_v_pop = max(tCT, 0.01)

    tMXD_retail_jobs_v_pop = 0

    if vmt_feature['intersections_qtrmi'] > 0:
        tMXD_intersections = float(vmt_feature['intersections_qtrmi'])
    else:
        tMXD_intersections = 0.0

    ## Q. if hh_avg_size is not available, should that be a fatal error?
    ##     well, about two--thirds of records have hh_avg_size == 0
    tMXD_hh_avg_size = vmt_feature['hh_avg_size']
    if tMXD_hh_avg_size == 0:
        tMXD_vehicles_per_capita = 0.8 #12nov10
        tMXD_hh_avg_size = 2.577
    else:
        tMXD_vehicles_per_capita = autos_per_hh / tMXD_hh_avg_size

    if tMXD_vehicles_per_capita < 0: tMXD_vehicles_per_capita = 0

    if tMXD_jobs_v_pop > 0:
        tICPM_hbw_jobs_pop = math.log(tMXD_jobs_v_pop) * cICPM_hbw_110
    else:
        tICPM_hbw_jobs_pop = 0.0

    if tMXD_hh_avg_size > 0:
        tICPM_hbw_hhsize = math.log(tMXD_hh_avg_size) * cICPM_hbw_113
    else:
        tICPM_hbw_hhsize = 0.0

    if tMXD_vehicles_per_capita > 0:
        tICPM_hbw_veh = math.log(tMXD_vehicles_per_capita) * cICPM_hbw_114
    else:
        tICPM_hbw_veh = 0.0

    tICPM_hbw = cICPM_hbw_107 + tICPM_hbw_jobs_pop + tICPM_hbw_hhsize + tICPM_hbw_veh

    if tMXD_area > 0:
        tICPM_hbo_area = math.log(tMXD_area) * cICPM_hbo_109
    else:
        tICPM_hbo_area = 0.0

    if tMXD_jobs_v_pop > 0:
        tICPM_hbo_jobs = math.log(tMXD_jobs_v_pop) * cICPM_hbo_110
    else:
        tICPM_hbo_jobs = 0.0

    if tMXD_intersections > 0:
        tICPM_hbo_int = math.log(tMXD_intersections) * cICPM_hbo_112
    else:
        tICPM_hbo_int = 0.0

    if tMXD_hh_avg_size > 0:
        tICPM_hbo_hhavg = math.log(tMXD_hh_avg_size) * cICPM_hbo_113
    else:
        tICPM_hbo_hhavg = 0.0

    if tMXD_vehicles_per_capita > 0:
        tICPM_hbo_veh = math.log(tMXD_vehicles_per_capita) * cICPM_hbo_114
    else:
        tICPM_hbo_veh = 0.0

    tICPM_hbo = cICPM_hbo_107 + tICPM_hbo_area + tICPM_hbo_jobs + tICPM_hbo_int + tICPM_hbo_hhavg + tICPM_hbo_veh


    #----------------------------------------------------------
    tICPM_nhb = cICPM_nhb_107
    if tMXD_total_emp_cell > 0:
        tICPM_nhb = tICPM_nhb + ( math.log(tMXD_total_emp_cell) * cICPM_nhb_108 )
    if tMXD_area > 0:
        tICPM_nhb = tICPM_nhb + ( math.log(tMXD_area) * cICPM_nhb_109 )
    if tMXD_intersections > 0:
        tICPM_nhb = tICPM_nhb + ( math.log(tMXD_intersections) * cICPM_nhb_112 )
    if tMXD_hh_avg_size > 0:
        tICPM_nhb = tICPM_nhb + ( math.log(tMXD_hh_avg_size) * cICPM_nhb_113 )
    if tMXD_vehicles_per_capita > 0:
        tICPM_nhb = tICPM_nhb + ( math.log(tMXD_vehicles_per_capita) * cICPM_nhb_114 )


    #-- Walking Trip Probability Model --------------------
    if (vmt_feature['qmb_acres_parcel_res_total'] + vmt_feature['qmb_acres_parcel_emp_total'] + vmt_feature[
        'qmb_acres_parcel_mixed_total']) != 0:
        tMXD_pop_emp_m_sq = ( tMXD_total_pop + tMXD_total_emp_qmb) / (
            vmt_feature['qmb_acres_parcel_res_total'] + vmt_feature['qmb_acres_parcel_emp_total'] + vmt_feature[
                'qmb_acres_parcel_mixed_total'] ) * 640.0
    else:
        tMXD_pop_emp_m_sq = 0
    if vmt_feature['emp_within_1mile'] == 0 or vmt_feature['emp_within_1mile'] is None:
        tMXD_emp_1m = 0
    else:
        tMXD_emp_1m = float(vmt_feature['emp_within_1mile'])

    #----------------------------------------------------------
    tWTPM_hbw = cWTPM_hbw_121
    if tMXD_jobs_v_pop > 0:
        tWTPM_hbw = tWTPM_hbw + ( math.log(tMXD_jobs_v_pop) * cWTPM_hbw_124 )
    if tMXD_emp_1m > 0:
        tWTPM_hbw = tWTPM_hbw + ( math.log(tMXD_emp_1m) * cWTPM_hbw_127 )
    if tMXD_hh_avg_size > 0:
        tWTPM_hbw = tWTPM_hbw + ( math.log(tMXD_hh_avg_size) * cWTPM_hbw_128 )
    if tMXD_vehicles_per_capita > 0:
        tWTPM_hbw = tWTPM_hbw + ( math.log(tMXD_vehicles_per_capita) * cWTPM_hbw_129 )

    #----------------------------------------------------------
    tWTPM_hbo = cWTPM_hbo_121
    if tMXD_area > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_area) * cWTPM_hbo_122 )
    if tMXD_pop_emp_m_sq > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_pop_emp_m_sq) * cWTPM_hbo_123 )
    if tMXD_jobs_v_pop > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_jobs_v_pop) * cWTPM_hbo_124 )
    if tMXD_intersections > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_intersections) * cWTPM_hbo_126 )
    if tMXD_emp_1m > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_emp_1m) * cWTPM_hbo_127 )
    if tMXD_hh_avg_size > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_hh_avg_size) * cWTPM_hbo_128 )
    if tMXD_vehicles_per_capita > 0:
        tWTPM_hbo = tWTPM_hbo + ( math.log(tMXD_vehicles_per_capita) * cWTPM_hbo_129 )

    #----------------------------------------------------------
    tWTPM_nhb = cWTPM_nhb_121
    if tMXD_pop_emp_m_sq > 0:
        tWTPM_nhb = tWTPM_nhb + ( math.log(tMXD_pop_emp_m_sq) * cWTPM_nhb_123 )
    if tMXD_intersections > 0:
        tWTPM_nhb = tWTPM_nhb + ( math.log(tMXD_intersections) * cWTPM_nhb_126 )
    if tMXD_emp_1m > 0:
        tWTPM_nhb = tWTPM_nhb + ( math.log(tMXD_emp_1m) * cWTPM_nhb_127 )
    if tMXD_hh_avg_size > 0:
        tWTPM_nhb = tWTPM_nhb + ( math.log(tMXD_hh_avg_size) * cWTPM_nhb_128 )
    if tMXD_vehicles_per_capita > 0:
        tWTPM_nhb = tWTPM_nhb + ( math.log(tMXD_vehicles_per_capita) * cWTPM_nhb_129 )

    #-- Transit Trip Probability Model --------------------
    if vmt_feature['emp30m_transit'] is not None and vmt_feature['total_employment'] > 0:
        tMXD_emp_30_min_transit = vmt_feature['emp30m_transit'] / vmt_feature['total_employment']   ##13May
    else:
        tMXD_emp_30_min_transit = 0

    if vmt_feature['hh_within_quarter_mile_trans'] > 0:   ##23mar
        tMXD_hh_quarter_m_transit = 1.0
    else:
        tMXD_hh_quarter_m_transit = 0.0

    #----------------------------------------------------------
    tTTPM_hbw = cTTPM_hbw_136
    if tMXD_intersections > 0:
        tTTPM_hbw = tTTPM_hbw + ( math.log(tMXD_intersections) * cTTPM_hbw_138 )
        #--------------------------------
    ## 26apr11 - divide by gTotalAreaEmployment as per mk
    if tMXD_emp_30_min_transit > 0:
        tTTPM_hbw = tTTPM_hbw + ( math.log(tMXD_emp_30_min_transit) * cTTPM_hbw_139 )
    if tMXD_hh_quarter_m_transit > 0:
        tTTPM_hbw = tTTPM_hbw + ( math.log(tMXD_hh_quarter_m_transit) * cTTPM_hbw_140 )
    if tMXD_hh_avg_size > 0:
        tTTPM_hbw = tTTPM_hbw + ( math.log(tMXD_hh_avg_size) * cTTPM_hbw_141 )
    if tMXD_vehicles_per_capita > 0:
        tTTPM_hbw = tTTPM_hbw + ( math.log(tMXD_vehicles_per_capita) * cTTPM_hbw_142 )

    #----------------------------------------------------------
    tTTPM_hbo = cTTPM_hbo_136
    if tMXD_pop_emp_m_sq > 0:
        tTTPM_hbo = tTTPM_hbo + ( math.log(tMXD_pop_emp_m_sq) * cTTPM_hbo_137 )
    if tMXD_hh_quarter_m_transit > 0:
        tTTPM_hbo = tTTPM_hbo + ( math.log(tMXD_hh_quarter_m_transit) * cTTPM_hbo_140 )
    if tMXD_hh_avg_size > 0:
        tTTPM_hbo = tTTPM_hbo + ( math.log(tMXD_hh_avg_size) * cTTPM_hbo_141 )
    if tMXD_vehicles_per_capita > 0:
        tTTPM_hbo = tTTPM_hbo + ( math.log(tMXD_vehicles_per_capita) * cTTPM_hbo_142 )

    #----------------------------------------------------------
    tTTPM_nhb = cTTPM_nhb_136
    if tMXD_emp_30_min_transit > 0:
        tTTPM_nhb = tTTPM_nhb + ( math.log(tMXD_emp_30_min_transit) * cTTPM_nhb_139 )
    if tMXD_vehicles_per_capita > 0:
        tTTPM_nhb = tTTPM_nhb + ( math.log(tMXD_vehicles_per_capita) * cTTPM_nhb_142 )

    vmt_feature['autos_per_hh'] = autos_per_hh
    vmt_feature['icpm_hbw'] = tICPM_hbw
    vmt_feature['icpm_hbo'] = tICPM_hbo
    vmt_feature['icpm_nhb'] = tICPM_nhb
    vmt_feature['wtpm_hbw'] = tWTPM_hbw
    vmt_feature['wtpm_hbo'] = tWTPM_hbo
    vmt_feature['wtpm_nhb'] = tWTPM_nhb
    vmt_feature['ttpm_hbw'] = tTTPM_hbw
    vmt_feature['ttpm_hbo'] = tTTPM_hbo
    vmt_feature['ttpm_nhb'] = tTTPM_nhb

    return vmt_feature
