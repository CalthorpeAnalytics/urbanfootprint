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
Footprint.ShowingAnalysisModulesState = SC.State.design({

    initialSubstate: 'analysisModulesPrepareState',

    scenarioDidChange: function() {
        // Hack to close the crud_state on scenario switch. This allows the nestedStore
        // to be reset on the recordsEditController, which we require to load the new analysis_modules locally
        Footprint.analysisModulesController.set('content', null);
        this.gotoState(this.analysisModulesPrepareState);
        return NO;
    },

    analysisModulesPrepareState: SC.State.plugin('Footprint.AnalysisModulesPrepareState'),

    /***
     * We go to this state when the AnalysisModules and AnalysisTools are loaded
     */
    analysisModulesAreReadyState: Footprint.RecordsAreReadyState.extend({
        baseRecordType: Footprint.AnalysisModule,
        recordsDidUpdateEvent: 'analysisModulesDidUpdate',
        recordsDidFailToUpdateEvent: 'analysisModulesDidFailToUpdate',
        updateAction: 'doAnalysisModuleUpdate',
        undoAction: 'doAnalysisModuleUndo',
        crudParams: function() {
            return {
                recordType: Footprint.AnalysisModule,
                recordsEditController: Footprint.analysisModulesEditController
            }
        }.property().cacheable(),

        doUpdateAnalysisModule: function(context) {
            // We need to explicitly make the active analysisModule dirty to get save to work
            Footprint.changeRecordStatus(
                Footprint.analysisModulesEditController.get('store'),
                Footprint.analysisModulesEditController.getPath('selection.firstObject'),
                SC.Record.READY_CLEAN,
                SC.Record.READY_DIRTY);

            this.updateRecords($.extend(
                this.get('crudParams'),
                toArrayController({content:Footprint.analysisModulesEditController.getPath('selection.firstObject')})));
        },
        /***
        * After saving of the AnalysisModule completes. Call crudDidStart and crudDidFinish.
        * Since there is no modal to attach to the CrudState, we have to do this manually
        * Obviously this needs a minor refactor
        * @param context
        */
        analysisModulesDidUpdate: function(context) {
            this.crudDidStart(context);
            this.crudDidFinish(context);
        },

        // Post-processing
        //

        // Override success message. We return null for the core to suppress the message on painting
        successMessage: function(context) {
            if (['core', 'agriculture'].contains(context.get('key')))
                return null;
            var recordType = context.get('recordType');
            return "Successfully completed %@ Module".fmt(context.get('key').titleize());
        },
        failureMessage: function(context) {
            var recordType = context.get('recordType');
            return "Failed to run analysis %@ Module".fmt(context.get('key').titleize());
        },

        postSavePublishingFinished: function(context) {
            var analysisModule = context.get('records')[0];
            if (['core', 'agriculture'].contains(context.get('key'))) {
                // TODO we still react to core differently than the other modules. It will all coalesce soon
                var scenarios = Footprint.scenariosController.filter(function(scenario) {
                    return scenario.get('id')==context.get('config_entity_id');
                });

                scenarios.forEach(function(scenario) {
                    SC.Logger.debug('Core Complete for Scenario: %@'.fmt(scenario.name));
                    scenario.getPath('presentations.results').forEach(function(resultLibrary) {
                        SC.run(function() {
                            (resultLibrary.get('results') || []).forEach(function(result) {
                                result.refresh(YES);
                            });
                        });
                    }, this);
                }, this);
                // Refresh
                if (context.get('key')=='core')
                    // TODO increment was the old name
                    Footprint.mapLayerGroupsController.refreshLayers(['scenario_increment', 'increment']);
                else if (context.get('key')=='agriculture')
                    // TODO does a DbEntity with this key ever exist?
                    Footprint.mapLayerGroupsController.refreshLayers(['agriculture']);
            }
            else {
                // Update the progress.
                analysisModule.set('progress', Math.min(1, analysisModule.get('progress') + context.get('proportion')));
                // If progress is complete, refresh everybody.
                if (analysisModule.get('progress') == 1) {

                    if (context.get('key') == 'vmt') {
                        Footprint.mapLayerGroupsController.refreshLayers(['vehicle_miles_traveled']);
                    }

                    if (context.get('key') == 'water') {
                        Footprint.mapLayerGroupsController.refreshLayers(['water']);
                    }

                    if (context.get('key') == 'energy') {
                        Footprint.mapLayerGroupsController.refreshLayers(['energy']);
                    }

                    if (context.get('key') == 'agriculture_analysis') {
                        Footprint.mapLayerGroupsController.refreshLayers(['agriculture']);
                    }

                    if (context.get('key') == 'public_health') {
                        Footprint.mapLayerGroupsController.refreshLayers(['ph_block_group_outcomes']);
                    }

                    var library_key = 'result_library__%@'.fmt(context.get('key'));
                    var resultLibraries = Footprint.resultLibrariesController.get('content').filter(function (library) {
                        return library.getPath('key') == library_key || library.getPath('key') == 'result_library__default';
                    });
                    resultLibraries.forEach(function(library) {
                        library.get('results').forEach(function(result) {
                            result.refresh();
                        })
                    });
                }
            }
            return NO;
        },

        enterState: function(context) {
            this._context = toArrayController(context, this.get('crudParams'));
            this._recordsEditController = Footprint.analysisModulesEditController;
            this._store = Footprint.store.get('autonomousStore');
            this._recordsEditController.set('store', this._store);
            this._content = this._recordsEditController.get('content');
            sc_super();
        },
        exitState: function() {
            this._recordsEditController = null;
            this._store = null;
            sc_super()
        },

        /***
         *
         * The undoManager property on each analysis_module
         */
        undoManagerProperty: 'undoManager',

        updateContext: function(context) {
            var recordContext = SC.ObjectController.create();
            return this.createModifyContext(recordContext, context)
        }
    })
});
