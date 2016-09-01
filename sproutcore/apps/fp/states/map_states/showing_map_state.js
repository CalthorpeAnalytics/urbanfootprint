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

/***
 * The state that manages the map panel portion of the application
 * @type {Class}
 */
Footprint.ShowingMapState = SC.State.design({

    /***
     * Fired when a Scenario becomes active and the layers and all of their dependencies are ready
     */
    dbEntitiesDidLoad: function() {
        this.gotoState('layersAreReadyForMapState');
        return NO;
    },
    /***
     * When the project changes instruct the map to move to the project extent
     */
    projectDidChange: function() {
        this.invokeLast(function() {
            // Wait until everyone has the new project
            Footprint.mapController.resetExtentToProject();
        });
    },

    /***
     * Fired when a Layer becomes active
     * @param context
     */
    layerDidChange: function(context) {
        // Re-enter the selectionHandlerState whenever the active layer changes
        // This will make sure our layerSelection/features loading happens
        // Clear the previous layer's selections
        Footprint.layerSelectionsController.set('content', null);
        // Make sure layerSelectionActiveController is cleared
        this.invokeLast(function() {
            this.gotoState('layerSelectionEditState', context);
        });
        return NO;
    },

    cancelSelection: function(layerContext) {
        this._closeFeatureTable();
        // Start over the selectionHandlerState
        this.gotoState('layerSelectionEditState', layerContext);
    },

    /***
     * Fired when the user changes the selection or order of visible map layers.
     */
    visibleLayersDidChange: function() {
        this.invokeOnce('doScheduleMapUpdate');
    },

    // If we're ready, and there isn't already a timer ticking, schedule a map update.
    doScheduleMapUpdate: function() {
        if (!Footprint.mapController.get('isReady'))
            // If map or layers are not ready
            return;
        if (!this._updateTimer) {
            this._updateTimer = SC.Timer.schedule({target: this, action: 'doProcessLayers', interval: 500});
        }
    },

    doProcessLayers: function() {
        this._updateTimer = null;
        Footprint.mapLayerGroupsController.updateMapLayerGroups();
        this.invokeNext(function() {
            // Once everything is ready, set layer visibility
            Footprint.mapController.set('mapLayersNeedZoomUpdate', YES);
        });
    },

    /**
     * Close the feature table popup.
     */
    _closeFeatureTable: function() {
        Footprint.featurePopupTableController.get('featureTablePopupPane').doClose();
    },



    /***
     * Activates the pencil (select individual features) tool
     * @param view
     */
    pointbrush: function(view) {
        this._closeFeatureTable();
        // Prevent selection from beginning before the layerSelectionActiveController is ready
        // TODO this should be done instead by disabling the selection buttons
        if (Footprint.layerSelectionActiveController.get('status') & SC.Record.READY) {
            Footprint.mapToolsController.selectToolByKey('pointbrush');
        }
    },

    /***
     * Activate the select (draw a shape to select) tool
     * @param view
     */
    rectanglebrush: function(view) {
        this._closeFeatureTable();
        // Prevent selection from beginning before the layerSelectionActiveController is ready
        // TODO this should be done instead by disabling the selection buttons
        if (Footprint.layerSelectionActiveController.get('status') & SC.Record.READY) {
            Footprint.mapToolsController.selectToolByKey('rectanglebrush');
        }
    },

    /***
     * Activate the select (draw a shape to select) tool
     * @param view
     */
    polybrush: function(view) {
        this._closeFeatureTable();
        // Prevent selection from beginning before the layerSelectionActiveController is ready
        // TODO this should be done instead by disabling the selection buttons
        if (Footprint.layerSelectionActiveController.get('status') & SC.Record.READY) {
            Footprint.mapToolsController.selectToolByKey('polybrush');
        }
    },

    /**
     * Fired to let the user move around the map. Disable
     * any selection tools.
     */
    navigate: function(view) {
        Footprint.mapToolsController.selectToolByKey('navigate');
    },

    /**
     * Fired to let the user start using the identify tool. Disable
     * any selection tools.
     */
    identify: function(view) {
        Footprint.mapToolsController.selectToolByKey('identify');
    },

    /***
     * Undo last paint operation
     * @param view
     */
    doPaintUndo: function(view) {
        Footprint.statechart.sendAction('doFeaturesUndo');
    },

    /***
     * Redo last undid operation
     * @param view
     */
    doPaintRedo: function(view) {
        Footprint.statechart.sendAction('doFeaturesRedo');
    },

    /***
     * TODO unimplemented. Revert to the first state in the undo buffer.
     * @param view
     */
    doPaintRevert: function(view) {

    },

    /***
     * Responds to zoomToProjectExtent by calling resetExtentToProject on the mapController
     * @param view
     */
    zoomToProjectExtent: function(view) {
        this._closeFeatureTable();
        Footprint.mapController.resetExtentToProject();
    },

    zoomToSelectionExtent: function(view) {
        this._closeFeatureTable();
        Footprint.mapController.resetExtentToSelection();
    },

    zoomToTableSelectionExtent: function(view) {
        Footprint.mapController.resetExtentToTableSelection();
    },

    doExportMap: function(view) {
        this._closeFeatureTable();
        Footprint.mapController.exportMapToImage();
    },

    substatesAreConcurrent: YES,
    mapState: SC.State.extend({

        scenariosDidChange: function(context) {
            // Changing projects and scenario is the same to the map for now
            this.scenarioDidChange(context);

            return NO;
        },
        layersDidChange: function(context) {
            return NO;
        },
        scenarioDidChange: function(context) {
            // The map controller is not ready until the layers are ready
            Footprint.mapController.set('readyToCreateMapLayers', NO);
            // Catch a scenario change by leaving going to readyState
            this.gotoState('%@.readyState'.fmt(this.get('fullPath')), context);
            return NO;
        },

        initialSubstate: 'readyState',
        readyState: SC.State,

        enterState: function() {
            Footprint.mapController.setIfChanged('readyToCreateMap', YES);
        },
        exitState: function() {
            // Exit only happens with application unload
            Footprint.mapController.setIfChanged('readyToCreateMap', NO);
        },

        layersAreReadyForMapState: SC.State.extend({
            enterState: function() {
                // If it's our first time loading layers, allow initial map creation to happen
                Footprint.mapController.setIfChanged('readyToCreateMapLayers', YES);
                Footprint.mapLayerGroupsController.clearMapLayers();
                Footprint.statechart.sendAction('doScheduleMapUpdate');

            }
        })
    }),

    // All the substates for handling feature selection and updating the selection on the server. This state
    // is always active and ready to accept a new selection drawn or queried by the user (unless the active layerSelection is loading).
    layerSelectionEditState: SC.State.plugin('Footprint.LayerSelectionEditState')
});
