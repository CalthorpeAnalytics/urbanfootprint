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



sc_require('models/presentation_medium_model');

// Result is a subclass class that supports charts and grids
Footprint.Result = Footprint.PresentationMedium.extend({
    presentation: SC.Record.toOne("Footprint.ResultLibrary", {
        isMaster: NO
    })
});

// A grid (table) result based on a data table, view, or query
Footprint.Grid = Footprint.Result.extend();
// A chart result based on a data table, view, or query
Footprint.Chart = Footprint.Result.extend();
// A chart that is displayed on a map as one or more layers
Footprint.LayerChart = Footprint.Result.extend();

// ResultLibrary is configuration of various results
Footprint.ResultLibrary = Footprint.Presentation.extend({
    // We currently use the results attribute instead of presentation_media. In theory Sproutcore supports subclassing on nested records, so we should be able to use the presentation_media attribute instead of results. A Result is a subclass of PresentationMedium
    results: SC.Record.toMany("Footprint.Result", {
        isMaster:YES,
        inverse: 'presentation'
    }),

    _copyProperties: function () {
        return sc_super().concat([]);
    },
    _cloneProperties: function () {
         return sc_super().concat(['results']);
    }
});
