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


Footprint.DefaultDelegate = SC.Object.extend({

    /***
     * If YES, the client Delegate represents a data manager site, as opposed to the default scenarios site
     */
    isDataManager: NO,

    dbEntityKeyToFeatureRecordType: function() {
        return SC.Object.create({
            base_feature: Footprint.BaseFeature,
            cpad_holdings: Footprint.CpadHoldingsFeature,
            scenario_increment: Footprint.IncrementsFeature,
            scenario_end_state: Footprint.EndStateFeature,
            base_agriculture_canvas: Footprint.BaseAgricultureFeature,
            future_agriculture_canvas: Footprint.FutureAgricultureFeature,
            census_tract: Footprint.CensusTract,
            census_blockgroup: Footprint.CensusBlockgroup,
            census_block: Footprint.CensusBlock,
            vehicle_miles_traveled: Footprint.VmtFeature,
            ph_block_group_outcomes: Footprint.PhBlockGroupOutcomesFeature
        });
    }.property().cacheable(),

    defaultsControllers: function() {
        return SC.Object.create({
            future_agriculture_canvas: Footprint.agricultureFeatureDefaultsController,
            base_agriculture_canvas: Footprint.agricultureFeatureDefaultsController,
            scenario_end_state: Footprint.endStateDefaultsController
        })
    }.property().cacheable(),

    loadingRegionStateClass: function() {
        return null;
    }.property().cacheable()
});
