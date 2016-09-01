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

sc_require('states/loading_scenario_dependency_states');
sc_require('states/records_are_ready_state');
sc_require('states/loading_state');
sc_require('states/loading_concurrent_dependencies_state');
sc_require('states/track_new_db_entities_state');

/***
 * The state that manages the DbEntities and their dependents.
 * DbEntity loading is triggered by changing scenarios
 * @type {Class}
 */
Footprint.ShowingDbEntitiesState = SC.State.design({

    /***
     * Whenever the Scenario changes we need to load DbEntities that aren't yet loaded
     * @param context
     * @returns {boolean}
     */
    scenarioDidChange: function(context) {
        // Start over and wait for to load
        this.gotoState(this.loadingDbEntitiesState, context);
        return NO;
    },

    initialSubstate: 'readyState',
    readyState: SC.State.extend({
        /***
         * If the Scenario is ready at this point (it should be) load the DbEntities
         * @param context
         */
        enterState: function(context) {
            if (Footprint.scenarioActiveController.getPath('status') & SC.Record.READY)
                this.gotoState('loadingDbEntitiesState');
        }
    }),

    loadingDbEntitiesState: Footprint.LoadingState.extend({
        didLoadEvent:'didLoadDbEntities',
        didFailEvent:'dbEntitiesDidFail',
        // Just use this controller to check the status and pass the context to the next state
        loadingController: SC.ArrayController.create(),
        enterState: function() {
            // Clear controllers in dependent states
            Footprint.featureBehaviorsController.set('content', null);
            sc_super();
        },
        recordArray:function() {
            return Footprint.scenarioActiveController.getPath('db_entities');
        },
        didLoadDbEntities: function() {
            this.get('statechart').sendEvent('dbEntitiesDidLoad');
            this.gotoState('loadingFeatureBehaviorsState', this.get('loadingController'));
        }
    }),

    /***
     * Force all db_entity.feature_behavior to load
     */
    loadingFeatureBehaviorsState: Footprint.LoadingState.extend({
        didLoadEvent: 'didLoadFeatureBehaviors',
        loadingController: Footprint.featureBehaviorsController,
        // This will set the loadingController to all the records upon completion, giving us
        checkRecordStatuses: YES,
        recordArray:function() {
            return Footprint.scenarioActiveController.getPath('db_entities').mapProperty('feature_behavior').compact();
        },
        /***
         * Once FeatureBehaviors are loaded, move on to loading Intersections
         */
        didLoadFeatureBehaviors: function(context) {
            this.invokeNext(function () {
                this.gotoState('loadingIntersectionsState', context);
                this.get('statechart').sendEvent('dbEntityDependenciesDidLoad', context);
            });
        }
    }),

    /***
     * Force all db_entity.feature_behavior.intersections to load
     */
    loadingIntersectionsState: Footprint.LoadingState.extend({
        didLoadEvent: 'didLoadIntersections',
        loadingController: SC.ArrayController.create(),
        // This will set the loadingController to all the records upon completion, giving us
        checkRecordStatuses: YES,
        recordArray:function() {
            return Footprint.scenarioActiveController.getPath('db_entities').mapProperty('feature_behavior').mapProperty('intersection').compact();
        },
        didLoadIntersections: function(context) {
            this.invokeNext(function () {
                this.gotoState('dbEntitiesAreReadyState', context);
                this.get('statechart').sendEvent('dbEntityDependenciesDidLoad', context);
            })
        }
    }),

    /***
     * This is extracted to a separate state because we track multiple DbEntities concurrently when we upload
     */
    dbEntitiesAreReadyState: SC.State.plugin('Footprint.DbEntitiesAreReadyState'),
});
