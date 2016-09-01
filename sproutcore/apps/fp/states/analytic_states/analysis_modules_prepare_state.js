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


Footprint.AnalysisModulesPrepareState = SC.State.extend({
    initialSubstate: 'choicepointState',

    /***
     * On entry, decides which peer substate we should end up in.
     */
    choicepointState: SC.State.extend({
        enterState: function(context) {
            if (!(Footprint.analysisModulesController.get('status') & SC.Record.READY)) {
                Footprint.statechart.gotoState('loadingAnalysisModulesState');
            }
            else {
                Footprint.statechart.gotoState('analysisModulesAreReadyState', context);
            }
        }
    }),

    /***
     * No analysis_module selection because no analysis_module! Once it loads, we will reenter choicepointState.
     */
    analysisModuleNotReadyState: SC.State,

    /***
     * AnalysisModule selection is loading.
     */
    loadingAnalysisModulesState: Footprint.LoadingState.extend({
        recordType:Footprint.AnalysisModule,
        loadingController: Footprint.analysisModulesController,
        didLoadEvent:'analysisModulesControllerIsReady',
        didFailEvent:'analysisModulesControllerDidFail',

        recordArray: function(context) {
            var configEntity = Footprint.scenariosController.getPath('selection.firstObject');
            if (!configEntity)
                return;

            // Check to see if these are already loaded
            var localResults = Footprint.store.find(SC.Query.create({
                recordType: this.get('recordType'),
                location: SC.Query.LOCAL,
                conditions: 'config_entity $ {configEntity}',
                configEntity: configEntity,
                orderBy: 'id'
            }));
            if (localResults.get('length') > 0) {
                return localResults;
            }

            return Footprint.store.find(SC.Query.create({
                recordType: this.get('recordType'),
                location: SC.Query.REMOTE,
                parameters: {
                    config_entity: configEntity
                }
            }));
        },
        analysisModulesControllerIsReady: function() {
            // Once the AnalysisModules load, load all of their AnalysisTools
            this.invokeNext(function() {
                this.gotoState('loadingAnalysisToolsState');
            }, this);
        }
    }),
    loadingAnalysisToolsState: Footprint.LoadingState.extend({
        recordType: Footprint.AnalysisTool,
        didLoadEvent:'analysisToolsDidLoad',
        didFailEvent:'analysisToolsDidFail',
        // Check each record since we have to SC.RecordArray
        checkRecordStatuses: YES,

        /***
         * Load the AnalysisTools of each AnalysisModule. We don't set a controller here.
         *
         * @returns {*|Array}
         */
        recordArray: function() {
            return Footprint.analysisModulesController.mapProperty('analysis_tools').flatten()
        },

        analysisToolsDidLoad: function() {
            // Start over now that we have a analysis_module Selection
            // invokeLast to allow the active controller to bind
            this.invokeNext(function() {
                Footprint.analysisModulesEditController.deselectObjects(
                    Footprint.analysisModulesEditController.get('selection')
                );
                Footprint.analysisModulesEditController.updateSelectionAfterContentChange();
                // Force this controller to update
                Footprint.analysisModulesRightSideEditController.propertyDidChange('allContent');
                Footprint.statechart.gotoState(
                    'analysisModulesAreReadyState',
                    SC.ArrayController.create({content:Footprint.analysisModulesController.get('content')}));
            });
        }
    }),
});
