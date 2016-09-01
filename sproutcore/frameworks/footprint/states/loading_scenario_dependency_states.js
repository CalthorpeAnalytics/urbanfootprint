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

sc_require('states/loading_state');

Footprint.LoadingScenarioDependencyState = Footprint.LoadingState.extend({

    loadingStatusValue:1,

    parameters: {},
    eventKey:null,
    recordArray:function() {
        return Footprint.store.find(SC.Query.create({
            recordType: this.get('recordType'),
            location: SC.Query.REMOTE,
            parameters:this.get('parameters')
        }));
    },
    didLoadEvent:function() {
        return '%@IsReady'.fmt(this.get('eventKey'));
    }.property('loadingController', 'eventKey').cacheable(),


    didFailEvent: function() {
        return '%@DidFail'.fmt(this.get('eventKey'));
    }.property('loadingController', 'eventKey').cacheable()
});

Footprint.LoadingConfigEntityCategoriesState = Footprint.LoadingScenarioDependencyState.extend({
    recordType: Footprint.ConfigEntityCategory,
    eventKey: 'configEntityCategories'
});

Footprint.LoadingBuiltFormTagsState = Footprint.LoadingScenarioDependencyState.extend({
    // BuiltFormTag isn't modeled on the server, but the API models it in
    // order to filter tags to those belonging to BuiltForms
    recordType: Footprint.BuiltFormTag,
    eventKey: 'builtFormTags'
});

Footprint.LoadingDbEntityTagsState = Footprint.LoadingScenarioDependencyState.extend({
    // DbEntityTag isn't modeled on the server, but the API models it in
    // order to filter tags to those belonging to DbEntities
    recordType: Footprint.DbEntityTag,
    eventKey: 'associatedItems'
});

Footprint.LoadingDbEntityCategoriesState = Footprint.LoadingScenarioDependencyState.extend({
    // DbEntityCategory isn't modeled on the server, but the API models it in
    // order to filter tags to those belonging to DbEntities
    recordType: Footprint.DbEntityCategory,
    eventKey: 'dbEntityCategories'
});

Footprint.LoadingBuildingUseDefinitionsState = Footprint.LoadingScenarioDependencyState.extend({
    recordType: Footprint.BuildingUseDefinition,
    eventKey: 'builtUseDefinitions'
});

// TODO: unwired
Footprint.LoadingPolicySetsState = Footprint.LoadingScenarioDependencyState.extend({
    recordType:Footprint.PolicySet,
});

/***
 * Loads all Behavior instances
 * @type {SC.RangeObserver}
 */
Footprint.LoadingBehaviorsState = Footprint.LoadingScenarioDependencyState.extend({
    recordType:Footprint.Behavior,
    eventKey: 'behaviors'
});

/***
 * Loads all Intersection instances
 * @type {SC.RangeObserver}
 */
Footprint.LoadingIntersectionsState = Footprint.LoadingScenarioDependencyState.extend({
    recordType:Footprint.Intersection,
    eventKey: 'intersections'
});
