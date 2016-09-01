
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
from footprint.main.models.analysis_module.vmt_module.vmt_model_constants import cAuto_const, cAuto_const_coef, cAuto_workers_per_hh_coef, cAuto_non_workers_16_64_hh_coef, cAuto_non_workers_65_hh_coef, cAuto_hh_income_coef, cAuto_hh_income_gt_100k_coef, cAuto_hh_mfdu_coef, cAuto_log_net_hu_dens_coef, cAuto_log_net_retail_dens_coef, cAuto_jobs_45_trans_coef

__author__ = 'calthorpe_analytics'


def generate_predicted_auto_ownership(vmt_feature):
    tRaw_trips_residential = vmt_feature['raw_trips_sf'] + vmt_feature['raw_trips_mf24'] + vmt_feature['raw_trips_mf5']
    tRaw_trips_nonresidential = vmt_feature['raw_trips_retail'] + vmt_feature['raw_trips_restaurant'] + vmt_feature[
        'raw_trips_entertainment'] + \
                                vmt_feature['raw_trips_office'] + vmt_feature['raw_trips_public'] + vmt_feature[
                                    'raw_trips_industry'] + \
                                vmt_feature['raw_trips_k12'] + vmt_feature['raw_trips_h_ed']

    if vmt_feature['vb_du_total'] == 0 or vmt_feature['vb_du_total'] is None \
        or vmt_feature['hh'] == 0 or vmt_feature['hh'] is None:
        tWorkers_per_HH = 0
        tNonWorkers_16_64_per_HH = 0
        tNonWorkers_65_per_HH = 0
        tMFU = 0

    else:
        if tRaw_trips_residential == 0 or tRaw_trips_nonresidential == 0:
            tWorkers_per_HH = 0
            tNonWorkers_16_64_per_HH = 0
            tNonWorkers_65_per_HH = 0
            tMFU = 0
        else:
            tAtmp = (vmt_feature['pop_employed'] / vmt_feature['hh']) * tRaw_trips_residential
            tBtmp = (vmt_feature['vb_pop_employed_total'] / vmt_feature[
                'vb_du_total']) * tRaw_trips_nonresidential  ## 11may
            tWorkers_per_HH = ( tAtmp + tBtmp ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)   ## 11may

            ## 11may
            if vmt_feature['pop_age16_up'] - vmt_feature['pop_employed'] - vmt_feature['pop_age65_up'] < 0:
                tAtmp = 0
            else:
                tAtmp = ((vmt_feature['pop_age16_up'] - vmt_feature['pop_employed'] - vmt_feature[
                    'pop_age65_up']) / float(
                    vmt_feature['hh'])) * tRaw_trips_residential

            if vmt_feature['vb_pop_age16_up_total'] - vmt_feature['vb_pop_employed_total'] - vmt_feature[
                'vb_pop_age65_up_total'] < 0:
                tBtmp = 0
            else:
                tBtmp = ((vmt_feature['vb_pop_age16_up_total'] - vmt_feature['vb_pop_employed_total'] - vmt_feature[
                    'vb_pop_age65_up_total']) / float(vmt_feature['vb_hh_total'])) * tRaw_trips_nonresidential
            tNonWorkers_16_64_per_HH = ( tAtmp + tBtmp ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)

            tAtmp = (vmt_feature['pop_age65_up'] / float(vmt_feature['hh'])) * tRaw_trips_residential
            tBtmp = ((vmt_feature['vb_pop_age65_up_total']) / float(
                vmt_feature['vb_hh_total'])) * tRaw_trips_nonresidential
            tNonWorkers_65_per_HH = ( tAtmp + tBtmp ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)

            tAtmp = ((vmt_feature['du_mf2to4'] + vmt_feature['du_mf5p']) / float(
                vmt_feature['du']) ) * tRaw_trips_residential
            tBtmp = ((vmt_feature['vb_du_mf_total']) / float(
                vmt_feature['vb_du_total'])) * tRaw_trips_nonresidential
            tMFU = ( tAtmp + tBtmp ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)


    ## --------------------------------------------------------------------------------------------
    ## -- [ indicator - income > 100k ] --
    if vmt_feature['hh_inc_00_10'] == None or vmt_feature['hh_inc_10_20'] == None or vmt_feature[
        'hh_inc_20_30'] == None or vmt_feature[
        'hh_inc_30_40'] == None or vmt_feature['hh_inc_40_50'] == None or vmt_feature['hh_inc_50_60'] == None or \
                    vmt_feature['hh_inc_60_75'] == None or vmt_feature['hh_inc_75_100'] == None or vmt_feature[
        'hh_inc_100p'] == None:
        tSum = 0
    else:
        tSum = \
            float(vmt_feature['hh_inc_00_10']) + float(vmt_feature['hh_inc_10_20']) + float(
                vmt_feature['hh_inc_20_30']) + float(
                vmt_feature['hh_inc_30_40']) + \
            float(vmt_feature['hh_inc_40_50']) + float(vmt_feature['hh_inc_50_60']) + float(
                vmt_feature['hh_inc_60_75']) + float(
                vmt_feature['hh_inc_75_100']) + \
            float(vmt_feature['hh_inc_100p'])

    if tSum == 0:
        w89 = 0
    else:
        w89 = vmt_feature['hh_inc_100p'] / float(tSum)

    if vmt_feature['vb_hh_inc_00_10_total'] == None or vmt_feature['vb_hh_inc_100p_total'] == None or vmt_feature[
        'vb_hh_inc_10_20_total'] == None \
        or vmt_feature['vb_hh_inc_20_30_total'] == None or vmt_feature['vb_hh_inc_30_40_total'] == None or vmt_feature[
        'vb_hh_inc_40_50_total'] == None or vmt_feature == None or ['vb_hh_inc_50_60_total'] == None or vmt_feature[
        'vb_hh_inc_60_75_total'] == None or vmt_feature['vb_hh_inc_75_100_total'] == None:
        tSum = 0
    else:
        tSum = \
            vmt_feature['vb_hh_inc_00_10_total'] + vmt_feature['vb_hh_inc_10_20_total'] + vmt_feature[
                'vb_hh_inc_20_30_total'] + vmt_feature[
                'vb_hh_inc_30_40_total'] + \
            vmt_feature['vb_hh_inc_40_50_total'] + vmt_feature['vb_hh_inc_50_60_total'] + vmt_feature[
                'vb_hh_inc_60_75_total'] + vmt_feature[
                'vb_hh_inc_75_100_total'] + \
            vmt_feature['vb_hh_inc_100p_total']

    if tSum == 0 or (tRaw_trips_residential + tRaw_trips_nonresidential) == 0:
        tIncome100kPlus = 0
    else:
        af89 = vmt_feature['vb_hh_inc_100p_total'] / float(tSum)
        if af89 == 0 or tRaw_trips_nonresidential == 0:
            tIncome100kPlus = 0
        else:
            tAtmp = (w89 * tRaw_trips_residential)
            tBtmp = (af89 * tRaw_trips_nonresidential)
            tIncome100kPlus = ( tAtmp + tBtmp ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)

    ## --------------------------------------------------------------------------------------------
    ## -- [ income category ] --

    if vmt_feature['hh_inc_00_10'] == None or vmt_feature['hh_inc_10_20'] == None or vmt_feature[
        'hh_inc_20_30'] == None or vmt_feature[
        'hh_inc_30_40'] == None or vmt_feature['hh_inc_40_50'] == None or vmt_feature['hh_inc_50_60'] == None or \
                    vmt_feature['hh_inc_60_75'] == None or vmt_feature['hh_inc_75_100'] == None or vmt_feature[
        'hh_inc_100p'] == None:
        tSum_O3W3 = 0
    else:
        tSum_O3W3 = float(vmt_feature['hh_inc_00_10']) + float(vmt_feature['hh_inc_10_20']) + float(
            vmt_feature['hh_inc_20_30']) + \
                    float(vmt_feature['hh_inc_30_40']) + float(vmt_feature['hh_inc_40_50']) + float(
            vmt_feature['hh_inc_50_60']) + \
                    float(vmt_feature['hh_inc_60_75']) + float(vmt_feature['hh_inc_75_100']) + float(
            vmt_feature['hh_inc_100p'])
        #----------------
    if vmt_feature['vb_hh_inc_00_10_total'] == None or vmt_feature['vb_hh_inc_100p_total'] == None or vmt_feature[
        'vb_hh_inc_10_20_total'] == None \
        or vmt_feature['vb_hh_inc_20_30_total'] == None or vmt_feature['vb_hh_inc_30_40_total'] == None or vmt_feature[
        'vb_hh_inc_40_50_total'] == None or vmt_feature == None or ['vb_hh_inc_50_60_total'] == None or vmt_feature[
        'vb_hh_inc_60_75_total'] == None or vmt_feature['vb_hh_inc_75_100_total'] == None:
        tSum_AY3BG3 = 0
    else:
        tSum_AY3BG3 = float(
            vmt_feature['vb_hh_inc_00_10_total'] + vmt_feature['vb_hh_inc_10_20_total'] + vmt_feature[
                'vb_hh_inc_20_30_total'] + \
            vmt_feature['vb_hh_inc_30_40_total'] + vmt_feature['vb_hh_inc_40_50_total'] + vmt_feature[
                'vb_hh_inc_50_60_total'] + \
            vmt_feature['vb_hh_inc_60_75_total'] + vmt_feature['vb_hh_inc_75_100_total'] + vmt_feature[
                'vb_hh_inc_100p_total'])
        #----------------
    if tSum_O3W3 == 0:
        o89 = 0
        p89 = 0
        q89 = 0
        r89 = 0
        s89 = 0
        t89 = 0
        u89 = 0
        v89 = 0
        w89 = 0
    else:
        o89 = vmt_feature['hh_inc_00_10'] / tSum_O3W3
        p89 = vmt_feature['hh_inc_10_20'] / tSum_O3W3
        q89 = vmt_feature['hh_inc_20_30'] / tSum_O3W3
        r89 = vmt_feature['hh_inc_30_40'] / tSum_O3W3
        s89 = vmt_feature['hh_inc_40_50'] / tSum_O3W3
        t89 = vmt_feature['hh_inc_50_60'] / tSum_O3W3
        u89 = vmt_feature['hh_inc_60_75'] / tSum_O3W3
        v89 = vmt_feature['hh_inc_75_100'] / tSum_O3W3
        w89 = vmt_feature['hh_inc_100p'] / tSum_O3W3
        #----------------
    if tSum_AY3BG3 == 0:
        x89 = 0
        y89 = 0
        z89 = 0
        aa89 = 0
        ab89 = 0
        ac89 = 0
        ad89 = 0
        ae89 = 0
        af89 = 0
    else:
        x89 = vmt_feature['vb_hh_inc_00_10_total'] / tSum_AY3BG3
        y89 = vmt_feature['vb_hh_inc_10_20_total'] / tSum_AY3BG3
        z89 = vmt_feature['vb_hh_inc_20_30_total'] / tSum_AY3BG3
        aa89 = vmt_feature['vb_hh_inc_30_40_total'] / tSum_AY3BG3
        ab89 = vmt_feature['vb_hh_inc_40_50_total'] / tSum_AY3BG3
        ac89 = vmt_feature['vb_hh_inc_50_60_total'] / tSum_AY3BG3
        ad89 = vmt_feature['vb_hh_inc_60_75_total'] / tSum_AY3BG3
        ae89 = vmt_feature['vb_hh_inc_75_100_total'] / tSum_AY3BG3
        af89 = vmt_feature['vb_hh_inc_100p_total'] / tSum_AY3BG3
        #----------------
    tIC_upper = (  1 * o89 + \
                   2 * ( p89 + q89 / 2.0 ) + \
                   3 * ( q89 / 2.0 + r89 / 2.0 ) + \
                   4 * ( r89 / 2.0 + s89 ) + \
                   5 * ( t89 + u89 ) + \
                   6 * v89 + \
                   7 * w89 / 2.0 + \
                   8 * w89 / 2.0 ) * tRaw_trips_residential
    #----------------
    tIC_lower = (  1 * x89 + \
                   2 * (  y89 + z89 / 2.0 ) + \
                   3 * (  z89 / 2.0 + aa89 / 2.0 ) + \
                   4 * ( aa89 / 2.0 + ab89 ) + \
                   5 * ( ac89 + ad89 ) + \
                   6 * ae89 + \
                   7 * w89 / 2.0 + \
                   8 * w89 / 2.0 ) * tRaw_trips_nonresidential
    #----------------
    if (tRaw_trips_residential + tRaw_trips_nonresidential) == 0:
        tIncomeCategory = 0
    else:
        tIncomeCategory = ( tIC_upper + tIC_lower ) / float(tRaw_trips_residential + tRaw_trips_nonresidential)

        ## --------------------------------------------------------------------------------------------
        ## -- [ Log( net housing density ) ] --
    if vmt_feature['vb_du_total'] is None:
        vmt_feature['vb_du_total'] = 0

    if vmt_feature['vb_acres_parcel_res_total'] is None:
        vmt_feature['vb_acres_parcel_res_total'] = 0

    if vmt_feature['vb_acres_parcel_mixed_total'] is None:
        vmt_feature['vb_acres_parcel_mixed_total'] = 0

    if vmt_feature['acres_parcel_emp'] is None:
        vmt_feature['acres_parcel_emp'] = 0

    if vmt_feature['acres_parcel_mixed'] is None:
        vmt_feature['acres_parcel_mixed'] = 0

    tUpperSum = (vmt_feature['vb_du_total'] * float(tRaw_trips_nonresidential)) + (
    float(vmt_feature['du']) * float(tRaw_trips_residential))
    tLowerSum = ((vmt_feature['vb_acres_parcel_res_total'] + vmt_feature[
        'vb_acres_parcel_mixed_total']) * float(tRaw_trips_nonresidential)) + (
                    (vmt_feature['acres_parcel_res'] + vmt_feature['acres_parcel_mixed']) * float(
                        tRaw_trips_residential))

    if tUpperSum <= 0 or tLowerSum <= 0:
        tLogNetHousingDensity = 0
    else:
        tLogNetHousingDensity = math.log(tUpperSum / float(tLowerSum))

    ## --------------------------------------------------------------------------------------------
    ## -- [ Log( net retail density ) ] --
    if vmt_feature['vb_emp_retail_total'] is None:
        vmt_feature['vb_emp_retail_total'] = 0

    if vmt_feature['vb_acres_parcel_emp_total'] is None:
        vmt_feature['vb_acres_parcel_emp_total'] = 0


    ##-- 30Aug11 raw_trips_residential/non is replaced by a new formula, only in the case of retail
    E15 = vmt_feature['raw_trips_retail']
    tAllTrips = vmt_feature['raw_trips_sf'] + vmt_feature['raw_trips_mf24'] + vmt_feature['raw_trips_mf5'] + \
                vmt_feature['raw_trips_retail'] + vmt_feature['raw_trips_restaurant'] + vmt_feature[
                    'raw_trips_entertainment'] + \
                vmt_feature['raw_trips_office'] + vmt_feature['raw_trips_public'] + vmt_feature['raw_trips_industry'] + \
                vmt_feature['raw_trips_k12'] + vmt_feature['raw_trips_h_ed']

    tXRawResSub = vmt_feature['raw_trips_sf'] + vmt_feature['raw_trips_mf24'] + vmt_feature['raw_trips_mf5']
    tXRawNonResSub = vmt_feature['raw_trips_retail'] + vmt_feature['raw_trips_office'] + \
                     vmt_feature['raw_trips_public'] + vmt_feature['raw_trips_industry'] + \
                     vmt_feature['raw_trips_k12'] + vmt_feature['raw_trips_h_ed']

    tUpperSum = (vmt_feature['vb_emp_retail_total'] * (tAllTrips - E15)) + (vmt_feature['vb_emp_retail_total'] * E15)
    tLowerSum = (vmt_feature['vb_acres_parcel_emp_total'] + (vmt_feature['vb_acres_parcel_mixed_total']) * (
        tAllTrips - E15)) + (
                    ( vmt_feature['acres_parcel_emp'] + vmt_feature['acres_parcel_mixed']) * E15 )

    if tUpperSum <= 0 or tLowerSum <= 0:
        tLogNetRetailDensity = 0
    else:
        tLogNetRetailDensity = math.log(tUpperSum / float(tLowerSum))

    ## --------------------------------------------------------------------------------------------
    ## -- [ # of jobs within 45m of transit ] --

    if vmt_feature['emp45m_transit'] is None:
        tJobs45min = 0
    else:
        tJobs45min = vmt_feature['emp45m_transit']

    ## --------------------------------------------------------------------------------------------
    if (cAuto_const * cAuto_const_coef) + \
            (tWorkers_per_HH * cAuto_workers_per_hh_coef) + \
            (tNonWorkers_16_64_per_HH * cAuto_non_workers_16_64_hh_coef) + \
            (tNonWorkers_65_per_HH * cAuto_non_workers_65_hh_coef) + \
            (tIncomeCategory * cAuto_hh_income_coef) + \
            (tIncome100kPlus * cAuto_hh_income_gt_100k_coef) + \
            (tMFU * cAuto_hh_mfdu_coef) + \
            (tLogNetHousingDensity * cAuto_log_net_hu_dens_coef) + \
            (tLogNetRetailDensity * cAuto_log_net_retail_dens_coef) + \
            (tJobs45min * cAuto_jobs_45_trans_coef) < 0:
        autos_per_hh = 0
    else:
        autos_per_hh = (cAuto_const * cAuto_const_coef) + \
                       (tWorkers_per_HH * cAuto_workers_per_hh_coef) + \
                       (tNonWorkers_16_64_per_HH * cAuto_non_workers_16_64_hh_coef) + \
                       (tNonWorkers_65_per_HH * cAuto_non_workers_65_hh_coef) + \
                       (tIncomeCategory * cAuto_hh_income_coef) + \
                       (tIncome100kPlus * cAuto_hh_income_gt_100k_coef) + \
                       (tMFU * cAuto_hh_mfdu_coef) + \
                       (tLogNetHousingDensity * cAuto_log_net_hu_dens_coef) + \
                       (tLogNetRetailDensity * cAuto_log_net_retail_dens_coef) + \
                       (tJobs45min * cAuto_jobs_45_trans_coef)

    return autos_per_hh
