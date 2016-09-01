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

Footprint.VmtFeature = Footprint.Feature.extend({

    acres_gross: SC.Record.attr(Number),
    pop: SC.Record.attr(Number),
    du: SC.Record.attr(Number),
    hh: SC.Record.attr(Number),
    emp: SC.Record.attr(Number),
    final_prod_hbo: SC.Record.attr(Number),
    final_prod_hbw: SC.Record.attr(Number),
    final_prod_nhb: SC.Record.attr(Number),
    final_attr_hbo: SC.Record.attr(Number),
    final_attr_hbw: SC.Record.attr(Number),
    final_attr_nhb: SC.Record.attr(Number),
    vmt_daily: SC.Record.attr(Number),
    vmt_daily_w_trucks: SC.Record.attr(Number),
    vmt_daily_per_capita: SC.Record.attr(Number),
    vmt_daily_per_hh: SC.Record.attr(Number),
    vmt_annual: SC.Record.attr(Number),
    vmt_annual_w_trucks: SC.Record.attr(Number),
    vmt_annual_per_capita: SC.Record.attr(Number),
    vmt_annual_per_hh: SC.Record.attr(Number),
    raw_trips_total: SC.Record.attr(Number),
    internal_capture_trips_total: SC.Record.attr(Number),
    walking_trips_total: SC.Record.attr(Number),
    transit_trips_total: SC.Record.attr(Number)
});
