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

Footprint.CpadHoldingsFeature = Footprint.Feature.extend({

    agency_name: SC.Record.attr(String),
    unit_name: SC.Record.attr(String),
    access_type: SC.Record.attr(String),
    acres: SC.Record.attr(Number),
    county: SC.Record.attr(String),
    agency_level: SC.Record.attr(String),
    agency_website: SC.Record.attr(String),
    site_website: SC.Record.attr(String),
    layer: SC.Record.attr(String),
    management_agency: SC.Record.attr(String),
    label_name: SC.Record.attr(String),
    ownership_type: SC.Record.attr(String),
    site_name: SC.Record.attr(String),
    alternate_site_name: SC.Record.attr(String),
    land_water: SC.Record.attr(String),
    special_use: SC.Record.attr(String),
    hold_notes: SC.Record.attr(String),
    city: SC.Record.attr(String),

    desg_agncy: SC.Record.attr(String),
    desg_nat: SC.Record.attr(String),
    prim_purp: SC.Record.attr(String),
    apn: SC.Record.attr(String),
    holding_id: SC.Record.attr(String),
    unit_id: SC.Record.attr(String),

    superunit: SC.Record.attr(String),
    agency_id: SC.Record.attr(String),
    mng_ag_id: SC.Record.attr(String),
    al_av_parc: SC.Record.attr(String),
    date_revised: SC.Record.attr(String),
    src_align: SC.Record.attr(String),
    src_attr: SC.Record.attr(String),
    d_acq_yr: SC.Record.attr(String)
});
