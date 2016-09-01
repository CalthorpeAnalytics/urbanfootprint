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

sc_require('states/records_are_ready_state');

/***
 * The state that manages the projects pane at the top of the application
 * @type {Class}
 */

Footprint.ShowingAnalysisToolsState = SC.State.design({

    initialSubstate: 'readyAnalysisModuleState',

    analysisModuleDidChange: function() {
        var analysisModule =  F.analysisModulesController.getPath('selection.firstObject');
        // Load tool controllers--0 or more
        if (analysisModule) {
            var loadingControllers = analysisModule.get('analysis_tools').map(function (analysisTool) {
                // Look for a matching AnalysisTool controller
                return Footprint.analysisToolControllerLookup.get(analysisTool.get('key')) || null;
            }).compact();

            if (loadingControllers.get('length') == 0) {
                // Nothing to do. Go restart ShowingAnalysisToolsState to get to recordsAreReadyState
                Footprint.statechart.gotoState(this.get('fullPath'));
                return;
            }
            this.loadingAnalysisToolsState.set('loadingControllers', loadingControllers);
            Footprint.statechart.gotoState(this.loadingAnalysisToolsState);
        }
        return NO
    },

    readyAnalysisModuleState: SC.State,


    /***
     * Loads different records from different controllers concurrently. This is only used by
     * AnalysisTool to load supplemental data for each tool in an AnalysisModule
     */
    loadingAnalysisToolsState:  SC.State.extend({
        initialSubstate: 'readyState',
        loadingSubstate: 'Footprint.LoadingAnalysisToolState',

        allControllersDidLoad: function() {
            Footprint.statechart.gotoState('analysisToolsAreReady', SC.Object.create({
                content: F.analysisModulesController.getPath('selection.firstObject'),
            }));
        },

        // Required. The controllers to load concurrently
        // Each controller must have a recordType
        loadingControllers: null,

        enterState: function() {
            var substates = this.get('loadingControllers').map(function(loadingController) {
                // We assume loadingControllers have unique recordTypes, thus use it for the substate name
                var recordType = resolveObjectForPropertyPath(loadingController.get('recordType'));
                var substateName = 'loading%@State'.fmt(recordType.toString().split('.')[1]);
                var substate;
                substate = this.loadingChildrenState.getState(substateName);
                if (!substate) {
                    substate = this.loadingChildrenState.addSubstate(
                        substateName,
                        SC.requiredObjectForPropertyPath(this.get('loadingSubstate'))
                    );
                }
                substate.set('loadingController', loadingController);
                return substate;
            }, this);
            this.loadingChildrenState.set('activeSubstates', substates);
        },

        readyState: SC.State.extend({
            enterState: function() {
                this.gotoState('loadingChildrenState');
            },
        }),

        // Holds all the LoadingState subclasses. Sends events allControllersDidLoad when they all finish loading
        loadingChildrenState: SC.State.extend({
            substatesAreConcurrent: YES,
            // The substates active for this run (until we learn how to destroy child states)
            activeSubstates: [],

            // This is sent by each substate as it finishes
            // The event is defined on LoadingState so make sure the subclass of LoadingState
            // doesn't consume it
            didLoadAnalysisToolController: function(context) {
                var matchingSubstate = this.get('activeSubstates').find(function(substate) {
                    return substate.get('loadingController') == context;
                }, this);
                if (!matchingSubstate) {
                    // Probably the user switched Scenarios or similar while we awaited this event
                    logWarning('No substate loadingController matched the context given to didLoadController. Context: %@'.fmt(context));
                    return;
                }
                this.get('activeSubstates').removeObject(matchingSubstate);
                if (this.getPath('activeSubstates.length') == 0) {
                    this.get('statechart').sendEvent('allControllersDidLoad');
                }
            },
        }),
        exitState: function() {
            // TODO should destroy children
        },
    }),

    analysisToolsAreReady: Footprint.RecordsAreReadyState.extend({

        recordsDidUpdateEvent: 'analysisToolDidUpdate',
        recordsDidFailToUpdateEvent: 'analysisToolDidFailToUpdate',
        updateAction: 'doAnalysisToolUpdate',
        undoAction: 'doSupplementalAnalysisModuleUndo',

        doAnalysisToolUpdate: function(context) {
            // We need to explicitly make the active analysisModule dirty to get save to work
            var recordsEditController = this.getPath('recordsEditController');
            recordsEditController.set('recordsAreUpdating', YES);

            Footprint.changeRecordStatus(
                this.getPath('recordsEditController.store'),
                this.getPath('recordsEditController.firstObject'),
                SC.Record.READY_CLEAN,
                SC.Record.READY_DIRTY);

            this.updateRecords(SC.Object.create({
                content:this.getPath('recordsEditController.firstObject'),
                recordsEditController: this.get('recordsEditController'),
                recordType: this.get('recordType'),
            }));
        },

        doMergeLayer: function(context) {
            Footprint.mergeUpdaterToolEditController.setPath('content.firstObject.db_entity_key', context.get('activeLayer'));
            Footprint.mergeUpdaterToolEditController.setPath('content.firstObject.target_config_entity', context.get('targetConfigEntity'));
            Footprint.statechart.sendAction('doAnalysisToolUpdate', SC.Object.create({content: context.get('content')}));
        },

        analysisToolDidUpdate: function(context) {

            var recordsEditController = this.getPath('recordsEditController');
            recordsEditController.set('recordsAreUpdating', NO);

            Footprint.statechart.gotoState('%@.readyState'.fmt(this.get('fullPath')), context);
        },
        // React to DbEntity saves by refreshing our records if the behavior matches
        dbEntityDidUpdate: function(context) {
            var dbEntity = context.getPath('records.firstObject');
            var dbEntityBehavior = dbEntity.getPath('feature_behavior.behavior');
            Footprint.analysisModulesController.forEach(function(analysisModule) {
                (analysisModule.get('analysis_tools') || []).forEach(function(analysisTool) {
                    if (dbEntityBehavior == analysisTool.get('behavior')) {
                        analysisTool.refresh();
                    }
                }, this);
            }, this);
        },

        analysisToolDidFailToUpdate: function(context) {
            var recordsEditController = this.getPath('recordsEditController');
            recordsEditController.set('recordsAreUpdating', NO);
            Footprint.statechart.gotoState('%@.readyState'.fmt(this.get('fullPath')), context);
        },

        noAnalysisToolsState: SC.State,

        enterState: function(context) {
            var analysisTool = Footprint.analysisToolsController.getPath('selection.firstObject');
            if (!analysisTool) {
                Footprint.statechart.gotoState('noAnalysisToolsState');
                return;
            }
            var recordsEditController = Footprint.analysisToolEditControllerLookup.get(analysisTool.get('key'));
            this.set('recordsEditController', recordsEditController);
            this._recordsEditController = recordsEditController;

            this._context = context;
            this.set('content', this._content);
            this.set('recordType', this._context.get('recordType'));
            this.set('baseRecordType', this.get('recordType'));
            this._store = Footprint.store.get('autonomousStore');
            this._recordsEditController.set('store', this._store);
            this._content = this._recordsEditController.get('content');

            sc_super();
        },
        exitState: function() {
            this._recordsEditController = null;
            if (this._store) {
                this._store = null;
            }
            this.set('content', null);
            this.set('recordType', null);
            this.set('baseRecordType', null);
            this.set('recordsEditController', null);
            sc_super();
        },

        updateContext: function(context) {
            var recordContext = SC.ObjectController.create();
            return this.createModifyContext(recordContext, context);
        },
    }),
});


// Loads each controller to get the subclass version of the AnalysisTool instance
// We already have the nested base instances, but we need the specific of the subclass instances
// We rely on the configured AnalysisTool controllers to specify the correct recordType
Footprint.LoadingAnalysisToolState = Footprint.LoadingState.extend({
    didLoadControllerEvent: 'didLoadAnalysisToolController',

    recordArray: function() {
        var configEntity = Footprint.scenariosController.getPath('selection.firstObject');
        if (!configEntity)
            return;

        var localResults = Footprint.store.find(SC.Query.create({
            recordType: this.getPath('loadingController.recordType'),
            location: SC.Query.LOCAL,
            conditions: 'config_entity = {configEntity}',
            configEntity: configEntity,
        }));
        if (localResults.get('length') > 0) {
            return localResults;
        }
        return Footprint.store.find(SC.Query.create({
            recordType: this.getPath('loadingController.recordType'),
            location: SC.Query.REMOTE,
            parameters: {
                config_entity: configEntity,
            },
        }));
    },

    loadingAnalysisModuleControllerIsReady: function() {
        // Start over now that we have a analysis_moduleSelection
        // invokeLast to allow the active controller to bind
        this.invokeNext(function() {
            Footprint.statechart.gotoState(this.parentState.analysisToolsAreReady, this.get('loadingController'));
        });
    },
});
