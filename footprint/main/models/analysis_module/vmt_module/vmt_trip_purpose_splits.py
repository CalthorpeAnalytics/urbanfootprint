
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

__author__ = 'calthorpe_analytics'

from footprint.main.models.analysis_module.vmt_module.vmt_model_constants import cProd_perc_per_hh, cProd_perc_hbw, cAttractions_per_hh_hbw, cAttractions_per_ret_emp_hbw, cAttractions_per_service_emp_hbw, cAttractions_per_ind_emp_hbw, cProd_perc_hbo, cAttractions_per_hh_hbo, cAttractions_per_ret_emp_hbo, cAttractions_per_service_emp_hbo, cAttractions_per_ind_emp_hbo, cProd_perc_nhb, cAttractions_per_hh_nhb, cAttractions_per_ret_emp_nhb, cAttractions_per_service_emp_nhb, cAttractions_per_ind_emp_nhb, c_nhbtgph_within_project, c_nhbtgph_in_to_out_project, cProd_school_hbw, cProd_school_hbo, cProd_school_nhb, cAttractions_school_hbw, cAttractions_school_hbo, cAttractions_school_nhb


##-------------------------------
def calculate_trip_purpose_splits(vmt_feature):
    tDTPD_residential = vmt_feature['du_detsf'] + vmt_feature['du_mf']
    ##--
    tDTPD_retail = vmt_feature['emp_retail'] + vmt_feature['emp_restaccom'] + vmt_feature['emp_arts_entertainment']
    ##--
    tDTPD_office = vmt_feature['emp_office'] + vmt_feature['emp_public']
    tDTPD_industrial_other = vmt_feature['emp_industry']

    B64 = cProd_perc_per_hh
    B69 = float(tDTPD_residential)
    B70 = float(tDTPD_retail)
    B71 = float(tDTPD_office)
    B72 = float(tDTPD_industrial_other)
    B73 = 0.0 # TODO Schools

    C33 = cProd_perc_hbw
    C36 = cAttractions_per_hh_hbw
    C37 = cAttractions_per_ret_emp_hbw
    C38 = cAttractions_per_service_emp_hbw
    C39 = cAttractions_per_ind_emp_hbw
    D33 = cProd_perc_hbo
    D36 = cAttractions_per_hh_hbo
    D37 = cAttractions_per_ret_emp_hbo
    D38 = cAttractions_per_service_emp_hbo
    D39 = cAttractions_per_ind_emp_hbo
    E33 = cProd_perc_nhb
    E36 = cAttractions_per_hh_nhb
    E37 = cAttractions_per_ret_emp_nhb
    E38 = cAttractions_per_service_emp_nhb
    E39 = cAttractions_per_ind_emp_nhb

    B50 = c_nhbtgph_within_project
    B51 = c_nhbtgph_in_to_out_project

    K69 = vmt_feature['raw_trips_sf'] + vmt_feature['raw_trips_mf24'] + vmt_feature['raw_trips_mf5']
    K70 = vmt_feature['raw_trips_retail'] + vmt_feature['raw_trips_restaurant'] + vmt_feature['raw_trips_entertainment']
    K71 = vmt_feature['raw_trips_office'] + vmt_feature['raw_trips_public']
    K72 = vmt_feature['raw_trips_industry']
    K73 = vmt_feature['raw_trips_k12'] + vmt_feature['raw_trips_h_ed']

    #--------------
    tNHCRP_PROD_residential_hbw = B69 * B64 * C33
    tNHCRP_PROD_residential_hbo = B69 * B64 * D33
    tNHCRP_PROD_residential_nhb = B69 * B64 * E33 * (B50 + B51)

    tNHCRP_ATTR_residential_hbw = B69 * C36
    tNHCRP_ATTR_residential_hbo = B69 * D36
    tNHCRP_ATTR_residential_nhb = B69 * E36

    #--------------------------------------------------------

    tNHCRP_PROD_retail_hbw = 0
    tNHCRP_PROD_retail_hbo = 0
    tNHCRP_PROD_retail_nhb = (B70 * E37) / 2

    tNHCRP_ATTR_retail_hbw = B70 * C37
    tNHCRP_ATTR_retail_hbo = B70 * D37
    tNHCRP_ATTR_retail_nhb = (B70 * E37) / 2

    #--------------
    tNHCRP_PROD_office_hbw = 0
    tNHCRP_PROD_office_hbo = 0
    tNHCRP_PROD_office_nhb = (B71 * E38) / 2

    tNHCRP_ATTR_office_hbw = B71 * C38
    tNHCRP_ATTR_office_hbo = B71 * D38
    tNHCRP_ATTR_office_nhb = (B71 * E38) / 2

    #--------------
    tNHCRP_PROD_industrial_hbw = 0
    tNHCRP_PROD_industrial_hbo = 0
    tNHCRP_PROD_industrial_nhb = (B72 * E39) / 2

    tNHCRP_ATTR_industrial_hbw = B72 * C39
    tNHCRP_ATTR_industrial_hbo = B72 * D39
    tNHCRP_ATTR_industrial_nhb = (B72 * E39) / 2

    #----------------------------------------
    tSum = tNHCRP_PROD_residential_hbw + tNHCRP_PROD_residential_hbo + tNHCRP_PROD_residential_nhb + \
           tNHCRP_ATTR_residential_hbw + tNHCRP_ATTR_residential_hbo + tNHCRP_ATTR_residential_nhb

    if tSum > 0:
        tITE_PROD_residential_hbw = (K69 * tNHCRP_PROD_residential_hbw) / tSum
        tITE_PROD_residential_hbo = (K69 * tNHCRP_PROD_residential_hbo) / tSum
        tITE_PROD_residential_nhb = (K69 * tNHCRP_PROD_residential_nhb) / tSum
        tITE_ATTR_residential_hbw = (K69 * tNHCRP_ATTR_residential_hbw) / tSum
        tITE_ATTR_residential_hbo = (K69 * tNHCRP_ATTR_residential_hbo) / tSum
        tITE_ATTR_residential_nhb = (K69 * tNHCRP_ATTR_residential_nhb) / tSum
    else:
        tITE_PROD_residential_hbw = 0
        tITE_PROD_residential_hbo = 0
        tITE_PROD_residential_nhb = 0
        tITE_ATTR_residential_hbw = 0
        tITE_ATTR_residential_hbo = 0
        tITE_ATTR_residential_nhb = 0

        #----------------------------------------
    tSum = tNHCRP_PROD_retail_hbw + tNHCRP_PROD_retail_hbo + tNHCRP_PROD_retail_nhb + \
           tNHCRP_ATTR_retail_hbw + tNHCRP_ATTR_retail_hbo + tNHCRP_ATTR_retail_nhb

    if tSum > 0:
        tITE_PROD_retail_hbw = (K70 * tNHCRP_PROD_retail_hbw) / tSum
        tITE_PROD_retail_hbo = (K70 * tNHCRP_PROD_retail_hbo) / tSum
        tITE_PROD_retail_nhb = (K70 * tNHCRP_PROD_retail_nhb) / tSum
        tITE_ATTR_retail_hbw = (K70 * tNHCRP_ATTR_retail_hbw) / tSum
        tITE_ATTR_retail_hbo = (K70 * tNHCRP_ATTR_retail_hbo) / tSum
        tITE_ATTR_retail_nhb = (K70 * tNHCRP_ATTR_retail_nhb) / tSum
    else:
        tITE_PROD_retail_hbw = 0
        tITE_PROD_retail_hbo = 0
        tITE_PROD_retail_nhb = 0
        tITE_ATTR_retail_hbw = 0
        tITE_ATTR_retail_hbo = 0
        tITE_ATTR_retail_nhb = 0

        #----------------------------------------

    tSum = tNHCRP_PROD_office_hbw + tNHCRP_PROD_office_hbo + tNHCRP_PROD_office_nhb + \
           tNHCRP_ATTR_office_hbw + tNHCRP_ATTR_office_hbo + tNHCRP_ATTR_office_nhb

    if tSum > 0:
        tITE_PROD_office_hbw = (K71 * tNHCRP_PROD_office_hbw) / tSum
        tITE_PROD_office_hbo = (K71 * tNHCRP_PROD_office_hbo) / tSum
        tITE_PROD_office_nhb = (K71 * tNHCRP_PROD_office_nhb) / tSum
        tITE_ATTR_office_hbw = (K71 * tNHCRP_ATTR_office_hbw) / tSum
        tITE_ATTR_office_hbo = (K71 * tNHCRP_ATTR_office_hbo) / tSum
        tITE_ATTR_office_nhb = (K71 * tNHCRP_ATTR_office_nhb) / tSum
    else:
        tITE_PROD_office_hbw = 0
        tITE_PROD_office_hbo = 0
        tITE_PROD_office_nhb = 0
        tITE_ATTR_office_hbw = 0
        tITE_ATTR_office_hbo = 0
        tITE_ATTR_office_nhb = 0

        #----------------------------------------

    tSum = tNHCRP_PROD_industrial_hbw + tNHCRP_PROD_industrial_hbo + tNHCRP_PROD_industrial_nhb + \
           tNHCRP_ATTR_industrial_hbw + tNHCRP_ATTR_industrial_hbo + tNHCRP_ATTR_industrial_nhb

    if tSum > 0:
        tITE_PROD_industrial_hbw = (K72 * tNHCRP_PROD_industrial_hbw) / tSum
        tITE_PROD_industrial_hbo = (K72 * tNHCRP_PROD_industrial_hbo) / tSum
        tITE_PROD_industrial_nhb = (K72 * tNHCRP_PROD_industrial_nhb) / tSum
        tITE_ATTR_industrial_hbw = (K72 * tNHCRP_ATTR_industrial_hbw) / tSum
        tITE_ATTR_industrial_hbo = (K72 * tNHCRP_ATTR_industrial_hbo) / tSum
        tITE_ATTR_industrial_nhb = (K72 * tNHCRP_ATTR_industrial_nhb) / tSum
    else:
        tITE_PROD_industrial_hbw = 0
        tITE_PROD_industrial_hbo = 0
        tITE_PROD_industrial_nhb = 0
        tITE_ATTR_industrial_hbw = 0
        tITE_ATTR_industrial_hbo = 0
        tITE_ATTR_industrial_nhb = 0

        #--------------
    tITE_PROD_school_hbw = K73 * cProd_school_hbw
    tITE_PROD_school_hbo = K73 * cProd_school_hbo
    tITE_PROD_school_nhb = K73 * cProd_school_nhb
    tITE_ATTR_school_hbw = K73 * cAttractions_school_hbw
    tITE_ATTR_school_hbo = K73 * cAttractions_school_hbo
    tITE_ATTR_school_nhb = K73 * cAttractions_school_nhb

    #--------------
    tITE_PROD_hbw_all = tITE_PROD_residential_hbw + tITE_PROD_retail_hbw + tITE_PROD_office_hbw + \
                        tITE_PROD_industrial_hbw + tITE_PROD_school_hbw

    tITE_PROD_hbo_all = tITE_PROD_residential_hbo + tITE_PROD_retail_hbo + tITE_PROD_office_hbo + \
                        tITE_PROD_industrial_hbo + tITE_PROD_school_hbo

    tITE_PROD_nhb_all = tITE_PROD_residential_nhb + tITE_PROD_retail_nhb + tITE_PROD_office_nhb + \
                        tITE_PROD_industrial_nhb + tITE_PROD_school_nhb

    tITE_ATTR_hbw_all = tITE_ATTR_residential_hbw + tITE_ATTR_retail_hbw + tITE_ATTR_office_hbw + \
                        tITE_ATTR_industrial_hbw + tITE_ATTR_school_hbw

    tITE_ATTR_hbo_all = tITE_ATTR_residential_hbo + tITE_ATTR_retail_hbo + tITE_ATTR_office_hbo + \
                        tITE_ATTR_industrial_hbo + tITE_ATTR_school_hbo

    tITE_ATTR_nhb_all = tITE_ATTR_residential_nhb + tITE_ATTR_retail_nhb + tITE_ATTR_office_nhb + \
                        tITE_ATTR_industrial_nhb + tITE_ATTR_school_nhb

    #--------------
    tTP_residential_hbw_all = tITE_PROD_residential_hbw + tITE_ATTR_residential_hbw
    tTP_residential_hbo_all = tITE_PROD_residential_hbo + tITE_ATTR_residential_hbo
    tTP_residential_nhb_all = tITE_PROD_residential_nhb + tITE_ATTR_residential_nhb

    tTP_retail_hbw_all = tITE_PROD_retail_hbw + tITE_ATTR_retail_hbw
    tTP_retail_hbo_all = tITE_PROD_retail_hbo + tITE_ATTR_retail_hbo
    tTP_retail_nhb_all = tITE_PROD_retail_nhb + tITE_ATTR_retail_nhb

    tTP_office_hbw_all = tITE_PROD_office_hbw + tITE_ATTR_office_hbw
    tTP_office_hbo_all = tITE_PROD_office_hbo + tITE_ATTR_office_hbo
    tTP_office_nhb_all = tITE_PROD_office_nhb + tITE_ATTR_office_nhb

    tTP_industrial_hbw_all = tITE_PROD_industrial_hbw + tITE_ATTR_industrial_hbw
    tTP_industrial_hbo_all = tITE_PROD_industrial_hbo + tITE_ATTR_industrial_hbo
    tTP_industrial_nhb_all = tITE_PROD_industrial_nhb + tITE_ATTR_industrial_nhb

    tTP_school_hbw_all = tITE_PROD_school_hbw + tITE_ATTR_school_hbw
    tTP_school_hbo_all = tITE_PROD_school_hbo + tITE_ATTR_school_hbo
    tTP_school_nhb_all = tITE_PROD_school_nhb + tITE_ATTR_school_nhb

    #--------------
    tTP_hbw_all = tTP_residential_hbw_all + tTP_retail_hbw_all + tTP_office_hbw_all + tTP_industrial_hbw_all + tTP_school_hbw_all
    tTP_hbo_all = tTP_residential_hbo_all + tTP_retail_hbo_all + tTP_office_hbo_all + tTP_industrial_hbo_all + tTP_school_hbo_all
    tTP_nhb_all = tTP_residential_nhb_all + tTP_retail_nhb_all + tTP_office_nhb_all + tTP_industrial_nhb_all + tTP_school_nhb_all

    ##==========================================

    vmt_feature['trips_hbw'] = tTP_hbw_all
    vmt_feature['trips_hbo'] = tTP_hbo_all
    vmt_feature['trips_nhb'] = tTP_nhb_all
    vmt_feature['ite_attr_hbw'] = tITE_ATTR_hbw_all
    vmt_feature['ite_attr_hbo'] = tITE_ATTR_hbo_all
    vmt_feature['ite_attr_nhb'] = tITE_ATTR_nhb_all
    vmt_feature['ite_prod_hbw'] = tITE_PROD_hbw_all
    vmt_feature['ite_prod_hbo'] = tITE_PROD_hbo_all
    vmt_feature['ite_prod_nhb'] = tITE_PROD_nhb_all

    return vmt_feature
