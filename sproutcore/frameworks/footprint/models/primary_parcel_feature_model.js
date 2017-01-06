/*
 * UrbanFootprint v1.5
 * Copyright (C) 2017 Calthorpe Analytics
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
sc_require('models/client_land_use_definition_model');

// TODO All Feature subclasses should come from the Tastypie /schema data instead of being hard coded here
Footprint.PrimaryParcelFeature = Footprint.Feature.extend({

    land_use_definition: SC.Record.toOne("Footprint.ClientLandUseDefinition", {
        isMaster: YES
    }),
    geography: SC.Record.toOne("Footprint.Geography", {
        isMaster: YES,
        nested: YES
    }),
    census_block: SC.Record.toOne("Footprint.CensusBlock", {
        isMaster: YES,
        nested: YES
    })
});

// Use this name in all subclasses for the api resource name
SC.mixin(Footprint.PrimaryParcelFeature, {
    apiClassName: function() {
        return 'existing_land_use_parcel';
    }
});
