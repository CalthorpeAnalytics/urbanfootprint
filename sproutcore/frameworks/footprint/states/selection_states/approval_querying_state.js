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

sc_require('states/selection_states/layer_selection_is_ready_state');

Footprint.ApprovalQueryingState = Footprint.LayerSelectionIsReadyState.extend({
    /***
     * Handles a change in the selected approval query by restarting the state with the new
     * corresponding LayerSelection
     * @param context
     */

    reenterApprovalFromMerge: function(context) {
        //re-enters the approval from merge and updates the query to null
        var content = Footprint.approvalQueriesController.get('content');
        Footprint.approvalQueriesController.selectObject(content.find(function(obj) {
            return obj.getPath('query_strings.filter_string')===undefined;})
        );
        this.doExecuteApprovalQuery(context);
    },

    activateMergeModule: function(context) {
        var merge_module = F.analysisModulesEditController.get('content').find(function(content) {
                return content.get('key')==='merge_module';
            }),
            content = Footprint.approvalQueriesController.get('content');
        //set the active analysis module to the merge module
        F.analysisModulesEditController.selectObject(merge_module);
        //set the approval query to all approved records
        Footprint.approvalQueriesController.selectObject(content.find(function(obj) {
            return obj.getPath('name')==='Load Edited Features - Approved';})
        );
        //load all records that have been approved and will be merged
        this.doExecuteApprovalQuery(context);
    },

    //for rentry after being in the merge module, reset query to empty to start again
    activateApprovalModule: function(context) {
        var content = Footprint.approvalQueriesController.get('content');
        Footprint.approvalQueriesController.selectObject(content.find(function(obj) {
            return obj.getPath('query_strings.filter_string')===undefined;})
        );
        this.enterState(SC.ObjectController.create({content: Footprint.approvalQueriesController.getPath('selection.firstObject')}));
    },

    doUpdateLayerSelectionContent: function(context) {
        // Modify the edit LayerSelection with our context LayerSelection.
        var layerSelectionFields = Footprint.LayerSelection.allRecordAttributeProperties();
        var queryStringFields = Footprint.QueryStringDictionary.allRecordAttributeProperties();

        layerSelectionFields.forEach(function(field) {
            this._content.set(field, context.get(field));
            if (field = 'query_strings') {
                queryStringFields.forEach(function(queryField) {
                    this._content.setPath('%@.%@'.fmt(field, queryField), context.getPath('%@.%@'.fmt(field, queryField)));
                }, this);
            }
        }, this);
    },

    exitApprovalState: function(context) {
        this.exitState(context);
    },

    doExecuteApprovalQuery: function(context) {
        // Re-enter state to execute new query
        this.enterState(SC.ObjectController.create({content:Footprint.approvalQueriesController.getPath('selection.firstObject')}));
    },

     /***
     * EnterState handles updating the layerSelection configuration to the selected Approval Query and executes
     * @param context
     */
    enterState: function(context) {
        // Get the current layerSelection
        var layerSelection = Footprint.layerSelectionActiveController.get('content');
        // Call the parent manually, since we need ot pass the default layerSelection
        arguments.callee.base.apply(this, [SC.ObjectController.create({content: layerSelection})]);
        this.doUpdateLayerSelectionContent(context.get('content'));
        //Disable selector tools if the selected query is no selection
        Footprint.toolController.set('selectorIsEnabled', this._content.getPath('query_strings.filter_string') !== undefined);
        //reset the selectAll toggle to false on enter
        Footprint.featureTableController.setIfChanged('selectAll', NO);
        // Execute the query. This will save the edited LayerSelection to the server
        this.invokeOnce('_doExecuteQuery');
    },

    _doExecuteQuery: function() {
        Footprint.statechart.sendAction('doExecuteQuery', this._content);
    },

    /***
     * Restore the LayerSelection to empty and reset approval to no query .
     * Returns to the Footprint.LayerSelectionEditState
     * @param context
     */
    exitState: function(context) {
        //reset the approval queries controller to have no query
        var content = Footprint.approvalQueriesController.get('content');
        Footprint.approvalQueriesController.selectObject(content.find(function(obj) {
            return obj.getPath('query_strings.filter_string')===undefined;})
        );
        //ensure that the active view is reset to approval rather than merge - edge case
        Footprint.approvalQueriesController.setIfChanged('activeView', 'Footprint.ApprovalView');
        //ensure that the map controls are activated on exit
        Footprint.toolController.set('selectorIsEnabled', YES);
        //set the context content to null to ensure that on exit, the layer selection state is re-entered
        context.set('content', null);
        //on exit first clear the active layer selection
        Footprint.statechart.sendAction('doClearSelection');
        //on exit re-enter the layer selection state and not the approval state
        Footprint.statechart.sendAction('layerSelectionDidChange', context);
        sc_super();
    }
});
