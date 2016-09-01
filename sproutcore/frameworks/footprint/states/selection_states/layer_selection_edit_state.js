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


Footprint.LayerSelectionEditState = SC.State.extend({
    initialSubstate: 'choicepointState',

    /***
     * Responds to the Footprint.topSectionVisibleViewController.topSectionIsVisible changing
     * @param context
     */
    layerSelectionDidChange: function(context) {
        // If the value is 'approval' go to the approvalQueryState
        if (context.get('content') == 'approval') {
            //make the edit section close and disable the button
            Footprint.mainPaneButtonController.set('editSectionIsVisible', NO);
            var layerSelection = Footprint.approvalQueriesController.getPath('selection.firstObject');
            // Goto the approvalQueryingState with the selected predefined LayerSelection
            this.gotoState(
                this.choicepointState,
                SC.ObjectController.create({content:layerSelection, layerSelectionIsReadyState:this.approvalQueryingState}));
        }
        // If the value is 'query' go to the choicepointState so that we can react to the current Layer
        else {
            // Simply restart the state to exit any substates
            this.gotoState(
                this.choicepointState,
                SC.ObjectController.create({content: Footprint.layerSelectionActiveController.get('content')})
            );
        }
        // Otherwise do nothing since the value has nothing to do with the LayerSelection
    },

    /***
     * Listen to when a Scenario's Layers become fully loaded and then load the LayerSelection
     */
    layerDidBecomeReady: function() {
        this.gotoState(
            this.choicepointState,
            SC.ObjectController.create({content: Footprint.layerSelectionActiveController.get('content')})
        );
    },

    doCloseTopSection: function(context) {
        var activeView = Footprint.topSectionVisibleViewController.get('view');

        if (activeView == 'Footprint.ApprovalTopSectionView') {
            //explicity exit the approval state when the top panel is closed
            Footprint.statechart.sendAction('exitApprovalState', context);
        }
        Footprint.topSectionVisibleViewController.setIfChanged('topSectionIsVisible', NO);
        return YES;
    },

    /***
     * On entry, decides which peer substate we should end up in.
     */
    choicepointState: SC.State.extend({
        // TODO layerContext is sometimes content=Layer and sometimes LayerSelection
        // correct this.
        enterState: function(layerContext) {
            if (!layerContext) {
                // We're in tight spot. It seems the Layer lacks a LayerSelection in the database
                // This should never happen
                Footprint.statechart.gotoState('layerNotReadyState', layerContext);
            }
            else if (!(Footprint.layersAndDependenciesController.getPath('status') & SC.Record.READY) ||
                layerContext.getPath('content.isBaseMap')
            ) {
                // If the layers are not ready or it is a base map, we're not ready
                Footprint.statechart.gotoState('layerNotReadyState', layerContext);
            }
            else if (!(Footprint.layerSelectionActiveController.get('status') & SC.Record.READY)) {
                // The LayerSelection is not READY and thus needs to load
                Footprint.statechart.gotoState(
                    'loadingLayerSelectionsState',
                    layerContext.get('content') && layerContext.get('content').kindOf(Footprint.Layer) ?
                        layerContext:
                        Footprint.layerActiveController);
            }
            else if (!(Footprint.layerSelectionActiveController.getPath('layer.db_entity.status') & SC.Record.READY)) {
                // It's possible for the DbEntity of the Layer to not be loaded, so wait for it to load if needed
                Footprint.statechart.gotoState(
                    'loadingDbEntityState',
                    layerContext.get('content') && layerContext.get('content').kindOf(Footprint.Layer) ?
                        layerContext:
                        Footprint.layerActiveController);
            }
            else {
                Footprint.statechart.gotoState(
                    layerContext.get('layerSelectionIsReadyState') || 'layerSelectionIsReadyState',
                    SC.ObjectController.create({
                        content:layerContext.get('content') || Footprint.layerSelectionActiveController.get('content')}));
            }
        }
    }),

    /***
     * No layer selection because no layer! Once it loads, we will reenter choicepointState.
     */
    layerNotReadyState: SC.State.extend({
        enterState: function() {
            // Clear any features from the previously selected layers
            Footprint.featuresActiveController.set('content', null);
            Footprint.featuresEditController.set('content', null);
            Footprint.toolController.set('featurerIsEnabled', NO);
            Footprint.toolController.set('selectorIsEnabled', NO);
        }
    }),

    /***
     * Layer selection is loading.
     */
    loadingLayerSelectionsState: Footprint.LoadingState.extend({

        recordType:Footprint.LayerSelection,
        loadingController: Footprint.layerSelectionsController,
        didLoadEvent:'layerSelectionsControllerIsReady',
        didFailEvent:'layerSelectionsControllerDidFail',
        // Set the loading controller to the recordArray query, so that it becomes status loading immediately
        // This helps us show loading messages quicker
        setLoadingControllerDirectly: YES,

        /***
         * This submits a LayerSelection clear request for the current layer
         * This will respond to the clear button if we are stuck in a long loading state
         */
        doClearSelection: function() {
            this.gotoState(this, SC.Object.create({content:Footprint.layerActiveController.get('content'), clear:YES}));
            return YES;
        },

        enterState: function(context) {
            Footprint.toolController.set('featurerIsEnabled', NO);
            Footprint.toolController.set('selectorIsEnabled', NO);
            return sc_super();
        },

        recordArray: function(context) {
            // TODO there's no need to load the LayerSections every time we enter the state
            // They should be cached once loaded--it's unlikely they will be updated outside this app in the meantime
            //var configEntity = Footprint.scenarioActiveController.get('content');
            var layer = context.get('content');
            if (layer && !layer.get('deleted')) {
                return Footprint.store.find(SC.Query.create({
                    recordType: this.get('recordType'),
                    location: SC.Query.REMOTE,
                    parameters: {
                        layer: layer,
                        config_entity: Footprint.scenarioActiveController.get('content')
                    },
                }));
            }
        },

        layerSelectionsControllerIsReady: function() {
            // Start over now that we have a layerSelection
            // invokeLast to allow the active controller to bind
            this.invokeNext(function() {
                this.gotoState(
                    this.getPath('parentState.fullPath'),
                    SC.ObjectController.create({content:Footprint.layerSelectionsController.getPath('selection.firstObject')}));
            });
        },
        layerSelectionsControllerDidFail: function() {
            SC.AlertPane.warn({
                message: 'Failed to load the layer selection',
                description: 'Please select another layer, and if this continues, please report to your system administrator.'
            });
        }
    }),

    loadingDbEntityState: Footprint.LoadingState.extend({
        enterState: function(context) {
            Footprint.toolController.set('featurerIsEnabled', NO);
            Footprint.toolController.set('selectorIsEnabled', NO);
            return sc_super();
        },
        recordType:Footprint.DbEntity,
        didLoadEvent:'dbEntityIsReady',
        didFailEvent:'dbEntityDidFail',

        /***
         * We just return a single record here, since we are simply waiting for a READY status
         * @param context: The Footprint.Layer whose DbEntity we need to await
         * @returns {*}
         */
        recordArray: function(context) {
            // Most likely this load is already in progress
            return context.getPath('db_entity');
        },

        dbEntityIsReady: function() {
            // Start over now that we have the DbEntity
            this.gotoState(
                this.getPath('parentState.fullPath'),
                SC.ObjectController.create({
                    content:Footprint.layerSelectionsController.getPath('selection.firstObject')
                })
            );
        },

        dbEntityDidFail: function() {
            SC.AlertPane.warn({
                message: 'Failed to load the DbEntity',
                description: 'Please report to your system administrator.'
            });
        }
    }),

    /***
     * Layer selection is ready!
     */
    layerSelectionIsReadyState: SC.State.plugin('Footprint.LayerSelectionIsReadyState', {

        /***
         * Handle the event if the topSection is 'query' and we are already in the right state
         * @param context
         * @returns {boolean}
         */
        layerSelectionDidChange: function(context) {
            if (context.get('content') == 'query') {
                return YES;
            }
            return NO;
        }
    }),

    /***
     * A subclass of LayerSelectionIsReadyState used to do approval querying with a predefined LayerSelection
    */
    approvalQueryingState: SC.State.plugin('Footprint.ApprovalQueryingState', {

        /***
         * Handle the event if the topSection is 'approval' and we are already in the right state
         * @param context
         * @returns {boolean}
         */
        layerSelectionDidChange: function(context) {
            if (context.get('content') == 'approval') {
                return YES;
            }
            return NO;
        }
    })
});
