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


sc_require('models/sacog_existing_land_use_parcel_feature_model');
sc_require('models/sacog_hardwood_feature_model');
sc_require('models/sacog_stream_feature_model');
sc_require('models/sacog_vernal_pool_feature_model');
sc_require('models/sacog_wetland_feature_model');

FootprintSacog.SacogDelegate = Footprint.DefaultDelegate.extend({
    dbEntityKeyToFeatureRecordType: function() {
        return SC.Object.create(sc_super(), {
            existing_land_use_parcels: FootprintSacog.SacogExistingLandUseParcelFeature,
            streams: FootprintSacog.SacogStreamFeature,
            wetlands: FootprintSacog.SacogWetlandFeature,
            vernal_pools: FootprintSacog.SacogVernalPoolFeature,
            hardwoods: FootprintSacog.SacogHardwoodFeature,
            light_rail:FootprintSacog.SacogLightRailFeature,
            light_rail_stops:FootprintSacog.SacogLightRailStopsFeature,
            light_rail_stops_one_mile:FootprintSacog.SacogLightRailStopsOneMileFeature,
            light_rail_stops_half_mile:FootprintSacog.SacogLightRailStopsHalfMileFeature,
            light_rail_stops_quarter_mile: FootprintSacog.SacogLightRailStopsQuarterMileFeature
        });
    }.property('parentDelegate').cacheable(),

    loadingRegionStateClass: function() {
        return SC.objectForPropertyPath('FootprintSacog.LoadingRegionSacogState')
    }.property().cacheable()
});
