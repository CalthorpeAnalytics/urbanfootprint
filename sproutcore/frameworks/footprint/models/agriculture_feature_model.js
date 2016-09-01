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

Footprint.AgricultureFeature = Footprint.Feature.extend({

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
    crop_yield: SC.Record.attr(Number),
    market_value: SC.Record.attr(Number),
    production_cost: SC.Record.attr(Number),
    water_consumption: SC.Record.attr(Number),
    labor_force: SC.Record.attr(Number),
    truck_trips: SC.Record.attr(Number)
});

Footprint.BaseAgricultureFeature = Footprint.AgricultureFeature.extend({
});

Footprint.FutureAgricultureFeature = Footprint.AgricultureFeature.extend({
});
