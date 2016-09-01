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


Footprint.EndStateFeature = Footprint.Feature.extend({

    clear_flag: SC.Record.attr(Number),
    redevelopment_flag: SC.Record.attr(Number),
    dev_pct: SC.Record.attr(Number),
    density_pct: SC.Record.attr(Number),
    gross_net_pct: SC.Record.attr(Number),
    developable_proportion: SC.Record.attr(Number),
    acres_developable: SC.Record.attr(Number),

    built_form: SC.Record.toOne("Footprint.BuiltForm", {
        isMaster: YES
    }),
    // Keep the built_form_key synced to the built_form
    builtFormObserver: function() {
        if (this.getPath('built_form.status') & SC.Record.READY) {
            this.setPathIfChanged('built_form_key', this.getPath('built_form.key'))
        }
    }.observes('.built_form'),

    built_form_key: SC.Record.attr(String),
    land_development_category: SC.Record.attr(String),
    acres_parcel: SC.Record.attr(Number),

    pop: SC.Record.attr(Number),
    hh: SC.Record.attr(Number),
    du: SC.Record.attr(Number),
    du_detsf: SC.Record.attr(Number),
    du_detsf_sl: SC.Record.attr(Number),
    du_detsf_ll: SC.Record.attr(Number),
    du_attsf: SC.Record.attr(Number),
    du_mf: SC.Record.attr(Number),

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
    bldg_sqft_mf: SC.Record.attr(Number),

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
    acres_parcel_res_detsf: SC.Record.attr(Number),
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

Footprint.EndStateFeature.mixin({
    priorityProperties: function () {
        return ['built_form', 'pop', 'du', 'emp'];
    },
    excludeProperties: function () {
        return ['config_entity', 'geometry']
    }
});
