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

Footprint.IncrementsFeature = Footprint.Feature.extend({
    land_development_category: SC.Record.attr(String),
    refill_flag: SC.Record.attr(Number),
    pop: SC.Record.attr(Number),
    hh: SC.Record.attr(Number),
    du: SC.Record.attr(Number),
    du_detsf: SC.Record.attr(Number),
    du_detsf_ll: SC.Record.attr(Number),
    du_detsf_sl: SC.Record.attr(Number),
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
    emp_education: SC.Record.attr(Number),
    emp_public_admin: SC.Record.attr(Number),
    emp_medical_services: SC.Record.attr(Number),
    emp_ind: SC.Record.attr(Number),
    emp_wholesale: SC.Record.attr(Number),
    emp_transport_warehousing: SC.Record.attr(Number),
    emp_manufacturing: SC.Record.attr(Number),
    emp_utilities: SC.Record.attr(Number),
    emp_construction: SC.Record.attr(Number),
    emp_ag: SC.Record.attr(Number),
    emp_agriculture: SC.Record.attr(Number),
    emp_extraction: SC.Record.attr(Number),
    emp_military: SC.Record.attr(Number)

});


Footprint.EndStateDemographicFeature = Footprint.Feature.extend({})
