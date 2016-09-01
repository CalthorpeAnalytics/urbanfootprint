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

Footprint.ShowingScenariosState = SC.State.extend({

    scenarioDidChange: function(context) {
        // Let this propagate through to other listeners
        return NO;
    },
    scenariosDidChange: function(context) {
        this.gotoState('scenariosAreReadyState', context);
        return NO;
    },

    /***
     * Export the Scenario record in the context.
     * @param context - context.content contains the Scenario to export
     * @returns {*} YES if the context contains a Scenario, else NO
     */
    doExportRecord: function(context) {
        if (context.get('activeRecord')) {
            if (context.get('activeRecord').kindOf(Footprint.Scenario)) {
                // TODO export something!
                return YES;
            }}
        return NO;
    },

    initialSubstate: 'readyState',
    readyState: SC.State.extend({
        enterState: function() {
            if ([SC.Record.READY_CLEAN, SC.Record.READY_DIRTY].contains(Footprint.scenariosController.get('status'))) {
                this.gotoState('scenariosAreReadyState', Footprint.scenariosController);
            }
        }
    }),

    scenariosAreReadyState: Footprint.RecordsAreReadyState.extend({
        baseRecordType: Footprint.Scenario,
        recordsDidUpdateEvent: 'scenariosDidChange',
        recordsDidFailToUpdateEvent: 'scenariosDidFailToUpdate',
        updateAction: 'doScenarioUpdate',
        undoAction: 'doScenarioUndo',
        undoAttributes: ['name', 'year', 'description'],

        crudParams: function() {
            return {
                infoPane: 'Footprint.ScenarioInfoPane',
                recordsEditController: Footprint.scenariosEditController,
                recordType: Footprint.Scenario
            };
        }.property().cacheable(),

        doManageScenarios: function() {
            this.doViewScenario();
        },

        doCreateScenario: function() {
            this.get('statechart').sendAction('doCreateRecord', this.get('crudParams'));
        },
        doCloneScenario: function() {
            this.get('statechart').sendAction('doCloneRecord',  this.get('crudParams'));
        },
        doEditScenario: function() {
            this.get('statechart').sendAction('doUpdateRecord',  this.get('crudParams'));
        },
        doViewScenario: function() {
            this.get('statechart').sendAction('doViewRecord',  this.get('crudParams'));
        },

        editScenarioDidChange: function(context) {
            // Send the generic action. The modal_crud_state will respond and
            // check that the context equals the recordsEditController
            this.get('statechart').sendAction('selectedEditRecordDidChange', context);
        },

        /***
         * Respond to postSavePulishing finishing by refreshing the Scenario
         * @param context
         */
        postSavePublishingFinished: function(context) {
            this.commitConflictingNestedStores([context.get('records')[0]]);
            context.get('records')[0].refresh();
        },

        undoManagerProperty: 'undoManager',

        /***
         * Scenarios have a basic update context. No flags are passed in for bulk updates
         * @returns {*}
         */
        updateContext: function(context) {
            var recordContext = SC.ObjectController.create();
            return this.createModifyContext(recordContext, context);
        },

        enterState: function(context) {
            // Make the default selection
            Footprint.scenariosController.deselectObjects(
                Footprint.scenariosController.get('selection')
            );
            Footprint.scenariosController.updateSelectionAfterContentChange();
        }
    })
});
