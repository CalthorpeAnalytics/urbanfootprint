/*
 * UrbanFootprint v1.5
 * Copyright (C) 2016 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */

sc_require('models/feature_model');

Footprint.BaseFeature = Footprint.Feature.extend({

    geography_id: SC.Record.attr(String),
    built_form: SC.Record.toOne("Footprint.BuiltForm", {
        isMaster: YES
    }),
    sqft_parcel: SC.Record.attr(Number),
    acres_parcel: SC.Record.attr(Number),
    acres_gross: SC.Record.attr(Number),
    acres_developable: SC.Record.attr(Number),
    land_development_category: SC.Record.attr(String),
    region_lu_code: SC.Record.attr(String),

    pop: SC.Record.attr(Number),
    hh: SC.Record.attr(Number),

    du: SC.Record.attr(Number),
    du_detsf_sl: SC.Record.attr(Number),
    du_detsf_ll: SC.Record.attr(Number),
    du_attsf: SC.Record.attr(Number),
    du_mf: SC.Record.attr(Number),
    du_mf2to4: SC.Record.attr(Number),
    du_mf5p: SC.Record.attr(Number),

    emp: SC.Record.attr(Number),
    emp_ret: SC.Record.attr(Number),
    emp_retail_services: SC.Record.attr(Number),
    emp_restaurant: SC.Record.attr(Number),
    emp_accommodation: SC.Record.attr(Number),
    emp_arts_entertainment: SC.Record.attr(Number),
    emp_other_services: SC.Record.attr(Number),
    emp_off: SC.Record.attr(Number),
    emp_office_services: SC.Record.attr(Number),
    emp_public_admin: SC.Record.attr(Number),
    emp_education: SC.Record.attr(Number),
    emp_medical_services: SC.Record.attr(Number),
    emp_ind: SC.Record.attr(Number),
    emp_manufacturing: SC.Record.attr(Number),
    emp_wholesale: SC.Record.attr(Number),
    emp_transport_warehousing: SC.Record.attr(Number),
    emp_utilities: SC.Record.attr(Number),
    emp_construction: SC.Record.attr(Number),
    emp_ag: SC.Record.attr(Number),
    emp_agriculture: SC.Record.attr(Number),
    emp_extraction: SC.Record.attr(Number),
    emp_military: SC.Record.attr(Number),

    bldg_sqft_detsf_sl: SC.Record.attr(Number),
    bldg_sqft_detsf_ll: SC.Record.attr(Number),
    bldg_sqft_attsf: SC.Record.attr(Number),
    bldg_sqft_mf2to4: SC.Record.attr(Number),
    bldg_sqft_mf5p: SC.Record.attr(Number),

    bldg_sqft_retail_services: SC.Record.attr(Number),
    bldg_sqft_restaurant: SC.Record.attr(Number),
    bldg_sqft_accommodation: SC.Record.attr(Number),
    bldg_sqft_arts_entertainment: SC.Record.attr(Number),
    bldg_sqft_other_services: SC.Record.attr(Number),
    bldg_sqft_office_services: SC.Record.attr(Number),
    bldg_sqft_public_admin: SC.Record.attr(Number),
    bldg_sqft_education: SC.Record.attr(Number),
    bldg_sqft_medical_services: SC.Record.attr(Number),
    bldg_sqft_wholesale: SC.Record.attr(Number),
    bldg_sqft_transport_warehousing: SC.Record.attr(Number),
    residential_irrigated_sqft: SC.Record.attr(Number),
    commercial_irrigated_sqft: SC.Record.attr(Number),
    acres_parcel_res: SC.Record.attr(Number),
    acres_parcel_res_detsf_sl: SC.Record.attr(Number),
    acres_parcel_res_detsf_ll: SC.Record.attr(Number),
    acres_parcel_res_attsf: SC.Record.attr(Number),
    acres_parcel_res_mf: SC.Record.attr(Number),
    acres_parcel_emp: SC.Record.attr(Number),
    acres_parcel_emp_off: SC.Record.attr(Number),
    acres_parcel_emp_ret: SC.Record.attr(Number),
    acres_parcel_emp_ind: SC.Record.attr(Number),
    acres_parcel_emp_ag: SC.Record.attr(Number),
    acres_parcel_emp_mixed: SC.Record.attr(Number),
    acres_parcel_mixed_use: SC.Record.attr(Number),
    acres_parcel_mixed_w_off: SC.Record.attr(Number),
    acres_parcel_mixed_no_off: SC.Record.attr(Number),
    acres_parcel_no_use: SC.Record.attr(Number)
});
