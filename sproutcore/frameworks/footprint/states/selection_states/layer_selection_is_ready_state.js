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

sc_require('controllers/features/feature_controllers');
sc_require('states/selection_states/querying_state');
sc_require('states/records_are_ready_state');
sc_require('states/record_updating_state');

/***
 * Handles updating a layerSelection instance by drawing bounds or querying
 * The context is always a controller whose content is a layerSelection instance
 * @type {*|RangeObserver|Class|void}
 */
Footprint.LayerSelectionIsReadyState = Footprint.RecordsAreReadyState.extend({

    recordsDidUpdateEvent: 'layerSelectionDidUpdate',
    recordsDidFailToUpdateEvent: 'layerSelectionDidFailToUpdate',
    updateAction: 'doLayerSelectionUpdate',
    undoAction: 'doLayerSelectionUndo',
    undoAttributes: ['query_strings', 'joins', 'bounds'],

    /***
     * Each layerSelection has an undoManager
     */
    undoManagerProperty: 'undoManager',

    doLayerSelectionUndo: function(context) {
        this.doRecordUndo(context);
    },
    doLayerSelectionRedo: function(context) {
        this.doRecordRedo(context);
    },

    /***
     * Update the layerSelection
     * @param context
     */
    doUpdateLayerSelection: function(context) {
        // Clear the features
        Footprint.featuresActiveController.set('content', null);
        this.updateRecords(context);
    },

    /***
     * Creates an update context for layer_selections. Since layer_selections are updated by query form and selecting
     * bounds, this doesn't set any attributes to update.
     */
    updateContext: function(context) {
        var recordContext = SC.ObjectController.create({selectionWantsToEnd:context.get('selectionWantsToEnd')});
        return this.createModifyContext(recordContext, context);
    },

    /***
     * Creates a clear painting context for clearing the selected features
     */
    clearContext: function(context) {
        var recordContext = SC.ObjectController.create({
            bounds: null,
            query_strings: SC.Object.create({filter_string:null, aggregates_string:null, group_by_string:null}),
            joins: null
        });
        return this.createModifyContext(recordContext, context)
    },


    /***
     * Responds to a PaintTool ending its selection shape.
     * The closed geometry of the final shape is assigned to the activeLayerSelection.bounds
     * @param view
     */
    doEndShape: function(event) {
        // Set the bounds to a new SC.Object so that we can observe changes in the UI
        //var eventType = L.DomEvent._getEvent().ctrlKey ? 'add' : 'replace';
        // this.setBounds();
        this.setBoundsFromDrawnPoly();
        // Pass the desire to end on the context
        Footprint.statechart.sendAction('doTestSelectionChange', SC.ObjectController.create(
            {content:this._context.get('content'), selectionWantsToEnd:YES})
        );
    },
    /***
     * After ending the selection we hide the extent of the brush immediately, if the
     * Footprint.mapController.showToolShape is False, so that the extent rect does not
     * linger on the map
     * @param event
     */
    doTogglePaintTool:function(event) {
        if (Footprint.mapToolsController.getPath('activeSelectorTool'))
            Footprint.mapToolsController.setPath('activeSelectorTool.isVisible',
                                                 Footprint.toolController.get('showToolShape'));
    },
    /***
     * Clears the selection and saves the clear layerSelection to the server
     * This clears the bounds, filter, join, aggregates...everything
     */
    doClearSelection: function() {

        Footprint.toolController.set('featurerIsEnabled', NO);

        this._context.set('bounds', null);
        this._context.set('description', null);
        // Clear the filter
        Footprint.statechart.sendAction('doClearAll');
        // Pass the desire to end on the context
        Footprint.statechart.sendAction('doTestSelectionChange', SC.ObjectController.create(
            {content:this._context.get('content'), selectionWantsToEnd:YES})
        );
        return YES;
    },

    // Stores the most recently selected bounds so that when a new doTestSelectionChange happens we
    // can check to see if the bounds actually changed
    _bounds:null,
    _time:null,

    // Triggered by a timer (box) or points (polygon) or whatever. Is
    // also run when entering the state in case the layer selection is already set to something
    doTestSelectionChange: function(context) {
        var time = new Date().getTime();
        // Just do at end for now
        //(NO && time-this._time > 3000) ||
        if (context.get('selectionWantsToEnd')) {
            // If a change occurred since last save (geoms, query doesn't match, etc),
            // and a decent amount of time has passed or the selection wants to end,
            // goto the savingSelectionState substate in order to update the server
            // The context might include a selectionWantsToEnd, which savingSelectionState will handle
            this._time = time;
            this._bounds = context.get('bounds');
            // Save the bounds query
            if (context.get('selectionWantsToEnd')) {
                // If the user drags a new selection, always assumed constrain_to_bounds
                // is desired. Otherwise the user's selection is 'ignored'
                context.setPath('content.selection_options.constrain_to_bounds', YES);
                this._invokeContext = this._invokeContext || context;
                this.invokeOnce('onceUpdateLayerSelection');
            }
        }
    },

    onceUpdateLayerSelection: function() {
        // Go to doExecuteQuery to make sure the query is kosher
        // and then continue on to doUpdateLayerSelection
        Footprint.statechart.sendAction('doExecuteQuery', this._invokeContext);
        this._invokeContext = null;
    },

    /***
     * Set the bounds to the painted geometry
     * @param eventType: 'add' or 'replace'. 'replace' is the default.
     */
    setBounds: function() {
        if (!Footprint.mapToolsController.get('activeSelectorTool')) {
            logWarning('No active paint tool. This should not happen');
            return;
        }
        var tool = Footprint.mapToolsController.get('activeSelectorTool');

        var bounds = SC.Object.create(
            tool.get('geometry')
            // eventType == 'add' && Footprint.layerSelectionActiveController.get('bounds') ?
            //     tool.appendGeometry(Footprint.layerSelectionActiveController.get('bounds')) :
            //     tool.get('geometry')
        );
        this._context.set('bounds', bounds);
    },

    setBoundsFromDrawnPoly: function() {
        if (!Footprint.mapToolsController.get('activeSelectorTool')) {
            logWarning('No active paint tool. This should not happen');
            return;
        }
        var tool = Footprint.mapToolsController.get('activeSelectorTool');

        var newBounds;
        if (tool.get('addToSelectionKeyPressed')){
            newBounds = Footprint.layerSelectionActiveController.getPath('bounds.coordinates');
            newBounds.push(tool.get('drawnPolygonCoordinates'));
        } else {
            newBounds = [];
            newBounds.push(tool.get('drawnPolygonCoordinates'));
        }

        var bounds = Footprint.BoundsDictionary.create({
            type: "MultiPolygon",
            coordinates: newBounds
        });
        this._context.set('bounds', bounds);
    },

    /***
     * Execute the query defined in the layerSelection
     * @param context
     */
    doExecuteQuery: function(context) {
        this.gotoState('queryingState', SC.ObjectController.create({content:context.get('content')}));
    },

    /***
     * Open the query window
     * @param view
     */
    doFeatureQuery: function() {
        if (!((this._context.get('status') & SC.Record.READY) &&
            (Footprint.featuresActiveController.getPath('layerStatus') & SC.Record.READY))) {
            logWarning("doFeatureQuery called when dependant controllers were not ready. This should not be possible.");
            return;
        }
        // Trigger the modal state to open the query dialog
        this.statechart.sendAction('doQueryRecords',
            SC.ObjectController.create({
                recordType:Footprint.featuresActiveController.get('recordType'),
                infoPane: 'Footprint.FeatureInfoPane',
                nowShowing:'Footprint.ModalFeatureQueryInfoView',
                recordsEditController:Footprint.featuresEditController
            })
        );
    },

    /**
     * Clears all query fields
     */
    doClearAll: function() {
        this.doClearBounds();
        this.doClearFilter();
        this.doClearJoins();
        this.doClearAggregates();
        this.doClearGroupBy();
    },


    /***
     * Just clears the bounds without saving
     */
    doClearBounds: function() {
        this.clear(['bounds']);
    },
    /***
     * Just clears the filter without saving
     */
    doClearFilter: function() {
        this.clear(['query_strings.filter_string', 'filter']);
    },

    doClearJoins: function() {
        this.clear(['joins']);
    },

    /***
     * Just clears the aggregate fields without saving
     */
    doClearAggregates: function() {
        this.clear(['query_strings.aggregates_string', 'aggregates']);
    },

    /***
     * Just clears the aggregate fields without saving
     */
    doClearGroupBy: function() {
        this.clear(['query_strings.group_by_string', 'group_bys']);
    },

    /***
     * Clears given layer selection properties
     * @param properties - simple or chained property string
     * @returns {*}
     */
    clear: function(properties) {
        //var context = this._context;
        /// TODO  Assuming we always want the edit controller here. The _context has the active controller
        var context = Footprint.layerSelectionEditController.get('content')
        if (context.getPath('store').readStatus(context.get('storeKey')) & SC.Record.BUSY) {
            logWarning("Attempt to clear layerSelection while it is busy");
            return;
        }
        properties.forEach(function(property) {
            context.setPath(property, null);
        });
    },

    // Tell the map controller whenever a new selection layer is ready
    layerSelectionDidUpdate:function(context) {
        if (context.get('selectionWantsToEnd')) {
            // Send the layerSelection as the context
            Footprint.statechart.sendEvent('selectionDidEnd', context);
        }
        else {
            this.gotoState('%@.readyState'.fmt(this.get('fullPath')), context);
        }
    },

    // Event thrown by substates when they've decided that we're ready to end selecting.
    selectionDidEnd: function(context) {
        // Start over
        this.gotoState(this.get('fullPath'), context);
    },

    layerSelectionDidFailToUpdate: function(context) {
        // If selection wants to end, throw an error message to the user.
        if (context && context.get('selectionWantsToEnd')) {
            SC.AlertPane.error({
                message: 'A selection error occurred',
                description: 'There was an error processing your selection. You can try selecting fewer features.'
            });
        }
        // Make sure all the bindings are correct

        // Either way, run selectionDidUpdate.
        // slight hack... an errored selection behaves the same as an updated selection + error message... so
        // we keep it internal here rather than routing it through an action call.
        this.layerSelectionDidUpdate(context);
    },

    /***
     * If the LayerSelection is already ready , do nothing
     * @returns YES
     */
    doQuery: function() {
        return YES
    },

    /***
     * if the LayerSelection is already ready, do nothing
     * @returns YES
     */
    doSummarize: function() {
        return YES
    },
    /***
     * Enter the state. The context.content is the LayerSelection that is ready to use
     * @param context
     */
    enterState: function(context) {
        this._store = Footprint.store.get('autonomousStore');
        this._content = this._store.materializeRecord(context.getPath('content.storeKey'));
        this._context = SC.ObjectController.create({content: this._content, selectionWantsToEnd: context.get('selectionWantsToEnd') || NO});
        sc_super();

        Footprint.statechart.sendAction('doTogglePaintTool');
        Footprint.toolController.set('selectionToolNeedsReset', YES);

        // Use the controller for ease of reference.
        Footprint.layerSelectionEditController.set('content', this._content);

        // No Feature Footprint.featuresActiveController.get('content'))inspection or updating is allowed until we have downloaded the features
        Footprint.toolController.set('featurerIsEnabled', NO);
        // Enable selector tools
        Footprint.toolController.set('selectorIsEnabled', YES);

        /*** QUI support code ***/
        /*
        var store = Footprint.layerSelectionEditController.getPath('content.store');
        QueryUI.set('store', store);
        // For now we only have one active query, that of the LayerSelectionEditController.
        // In the future we'll have saved queries as well
        var storedQueriesQuery = SC.Query.local(
            Footprint.LayerSelection,
            { conditions: "unique_id = '%@'".fmt(Footprint.layerSelectionEditController.get('unique_id')) });
        QueryUI.allQueriesController.set('content', store.find(storedQueriesQuery));
        */
        /*** End QUI support code ***/
    },

    exitState: function() {
        this._store = null;
        Footprint.layerSelectionEditController.set('content', null);

        /*** QUI support code ***/
        QueryUI.set('store', null);
        QueryUI.allQueriesController.set('content', null);
        /*** End QUI support code ***/
    },

    /***
     * Override the parent state's readyState to advance us to the selectedFeaturesState whenever there are features
     * in the layerSelection
     */
    readyState: SC.State.extend({

        enterState: function(context) {
            // Allow deselecting if there are any records selected
            Footprint.toolController.set('deselectorIsEnabled', !!context.get('features_count'));

            if (context.getPath('features_count')) {
                // Features selected.
                Footprint.statechart.gotoState(this.parentState.selectedFeaturesState, this._context);
            }
            else {
                // Set it to empty so the query info window shows no results
                Footprint.featuresActiveController.set('content', null);
                // Still go to the featuresAreReadyState so that we can support undo/redo
                this.gotoState('featuresAreReadyState', Footprint.featuresActiveController);
            }
        }
    }),

    // TODO Overrriding parent version to force action handling
    updatingState: Footprint.RecordUpdatingState.extend({
        doEndShape: function() {
            this.cancelUpdate();
            return NO;
        },
        doExecuteQuery: function() {
            this.cancelUpdate();
            return NO;
        },
        doClearSelection: function() {
            this.cancelUpdate();
            return NO;
        },
        doQueryRecords: function() {
            this.cancelUpdate();
            return NO;
        },

        undoActionBinding: SC.Binding.oneWay('.parentState.undoAction'),
        updateActionBinding: SC.Binding.oneWay('.parentState.updateAction'),
        recordsDidUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidUpdateEvent'),
        recordsDidFailToUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidFailToUpdateEvent'),
        recordsDidUpdate:function(context) {
            // Do the default stuff
            sc_super();
        }
    }),

    // The state for querying for selections
    queryingState: Footprint.QueryingState,

    // When a selection is ready, we load the features and then allow the user to edit them (multiple
    // times).
    selectedFeaturesState:SC.State.extend({

        initialSubstate:'loadingFeaturesState',

        refreshFeatures: function() {
          this.gotoState(this, this._context)
        },

        enterState: function(context) {
            this._context = context;
        },
        exitState: function() {
            this._context = null;
        },

        /***
         * Load the features stored in the layerSelection
         */
        loadingFeaturesState: Footprint.LoadingState.extend({

            didLoadEvent:'featuresDidLoad',
            didFailEvent:'featuresDidFailToLoad',
            loadingController:Footprint.featuresActiveController,
            // This is important so that the loadingController status changes to loading when we change layers
            // or incrementally load features
            setLoadingControllerDirectly: YES,

            enterState: function(context) {
                // Turn off the feature controllers
                Footprint.toolController.set('featurerIsEnabled', NO);
                sc_super();
            },

            /***
             * Fetches the features in the Footprint.layerSelectionActive controller via a remote query
             * @returns {*}
             */
            recordArray: function() {
                return Footprint.store.find(SC.Query.create({
                    recordType:Footprint.layerSelectionEditController.getPath('layer.featureRecordType'),
                    location:SC.Query.REMOTE,
                    parameters:{
                        layer: Footprint.layerSelectionEditController.get('layer'),
                        config_entity: Footprint.scenarioActiveController.get('content')
                    }
                }));
            },
            featuresDidLoad: function() {
                this.gotoState('featuresAreReadyState', Footprint.featuresActiveController);
            },
            featuresDidFailToLoad: function() {
                this.gotoState('errorState', Footprint.featuresActiveController);
            },
            errorState: SC.State.extend({
                enterState: function() {
                    SC.AlertPane.error({
                        message: 'Error loading features',
                        description: 'Try different bounds or query filters. Contact the system admin if the problem persists',
                        buttons: [{
                            title: 'OK'
                        }]
                    })
                }
            })
        }),

        featuresAreReadyState: SC.State.plugin('Footprint.FeaturesAreReadyState')
    })
});
