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
sc_require('states/crud_state');
sc_require('states/crud_modal_state');
sc_require('states/crud_modal_ready_state');
sc_require('controllers/layers/style_controllers');

/***
 * The state that manages the projects pane at the top of the application
 * @type {Class}
 */
Footprint.ShowingLayersState = SC.State.design({

    scenarioDidChange: function(context) {
        // Start over and wait for layers to load
        this.gotoState(this.readyState, context);
        return NO;
    },

    layersDidChange: function(context) {
        Footprint.layerTreeController.deselectObjects(
            Footprint.layerTreeController.get('selection')
        );
        Footprint.layerTreeController.updateSelectionAfterContentChange();
        this.gotoState('layersAreReadyState', context);
        return NO;
    },

    initialSubstate: 'readyState',
    readyState: SC.State,

    layersAreReadyState: Footprint.RecordsAreReadyState.extend({
        recordsAreReadyEvent: 'layersAreReady',
        baseRecordType: Footprint.Layer,
        recordsDidUpdateEvent: 'layersDidUpdate',
        recordsDidFailToUpdateEvent: 'layersDidFailToUpdate',
        updateAction: 'doLayerUpdate',
        undoAction: 'doLayerUndo',
        undoAttributes: ['name', 'year', 'description'],
        recordsEditController: Footprint.layersEditController,
        crudParams: function() {
            // We need an existing layer to use as a template (for now)
            var template = Footprint.layersEditController.get('content');
            if (!template || template.get('id') < 0)
                template = Footprint.layersEditController.filter(function(layer) { return layer.get('id') > 0; })[0];
            return {
                infoPane: 'Footprint.LayerInfoPane',
                recordType: Footprint.Layer,
                // We use the Footprint.layersEditController as are primary edit controller
                recordsEditController: this.get('recordsEditController'),
                content:template
            };
        }.property().cacheable(),

        /***
         * Reload the new DbEntity to get the layer id then
         * load the newly created layer by checking the DbEntity
         * @param context
         */
        doLoadNewLayer: function(context) {
            this.gotoState(this.reloadNewDbEntity, context);
        },


        /***
         * When the scenario-scope button is clicked for a DbEntity or new Layer is created,
         * this adds/removes the Layer to/from the APPLICATION LayerLibrary specified.
         *
         * In the case of adding a new Layer (or deleting) where no * LayerLibrary is specified,
         * the add/remove is performed at the ConfigEntity scope and all those below it. For instance,
         * a Project Layer would add/remove from the Project Application LayerLibrary and all Scenario
         * Application LayerLibraries.
         *
         * @param context:
         *  value: YES to add, NO, to remove
         *  theLayer: the layer to add or remove
         *  layerLibrary: Optional. The layerLibrary to update. Otherwise all Application LayerLibraries
         *  at and below the DbEntity's ConfigEntity are modified
         *  doSave: Optional, if YES, save the LayerLibrary to the server immediately. Note that currently
         *  new Layers are added to the APPLICATION LayerLibrary upon creation (based on the import layer
         *  configuration in default_layer.py, so there's no need to save changes to the server after a
         *  Layer is created)
         */
        doAddOrRemoveLayerFromApplicationLayerLibrary: function(context) {
            // Add the layer to the Application LayerLibraries at an below the DbEntity's ConfigEntity scope
            // We set the context to NO to simulate going from off to on in the UI
            // doSave: YES means call the updatingSTate immediately to save the LayerLibrary
            var layerLibraries = context.get('layerLibrary') ?
                // Just the explicitly specified one
                [context.get('layerLibrary')] :
                // All at or below the ConfigEntity
                context.get('theLayer').getPath('db_entity.config_entity').forSelfAndChildren(function(configEntity) {
                    return configEntity.getPath('presentations.layers').findProperty(
                        'key',
                        Footprint.scenarioLayerLibraryApplicationEditController.get('key')
                    );
                }, YES).compact();

            // Iterate through to update or remove
            layerLibraries.forEach(function(layerLibrary) {
                if (context.get('value')) {
                    // Add the Layer to the LayerLibrary
                    this._updateLayerLibrary(context.get('theLayer'), layerLibrary)
                }
                else {
                    // Remove the Layer from the LayerLibrary
                    this._removeFromLayerLibrary(context.get('theLayer'), layerLibrary)
                }
            }, this);
            // If desired save the LayerLibrary update immediately
            // We only ever need to save the highest-level LayerLibrary since the subordinate ones
            // will adopt.
            var layerLibrariesToClean;
            if (context.get('doSave')) {
                this.gotoState(
                    'updatingLayerLibraryState',
                    SC.Object.create({
                        content: [layerLibraries.get('firstObject')],
                        // Pass theLayer and value so we can set the main store LayerLibraries after save
                        // We do this since we only save one LayerLibrary to the server (the others update
                        // on the server so we have to update them manually)
                        theLayer: context.get('theLayer'),
                        value: context.get('value')
                    })
                );
                // Mark the other LayerLibraries as READY_CLEAN since they are reflected
                layerLibrariesToClean = layerLibraries.slice(1);
            }
            else {
                layerLibrariesToClean = layerLibraries;
            }
            // Set all unsaved LayerLibraries to READY_CLEAN
            layerLibrariesToClean.forEach(function(layerLibrary) {
                layerLibrary.get('store').writeStatus(layerLibrary.get('storeKey'), SC.Record.READY_CLEAN);
            });

            // Tell the Footprint.layerTreeController about the change
            Footprint.layerTreeController.contentDidChange();
        },

        modalDidCancel: function(context) {
            if (context.get('recordsEditController') == Footprint.layersEditController) {
                this.gotoState(this, this._context);
                return YES;
            }
            return NO;
        },

        modalDidExit: function() {
            //deselect the selection on the style attributes controller
            var styleAttributeSelection = Footprint.styleableAttributesEditController.get('selection');
            Footprint.styleableAttributesEditController.deselectObjects(styleAttributeSelection);
        },

        doExportRecord: function(context) {
            var records = Footprint.layersEditController.getPath('selection');
            if (!records)
                return NO;

            if (records.get('length') == 0) {
                SC.AlertPane.info('Cannot export: No layer selected.');
                return NO;
            }

            if (records.get('length') > 1) {
                SC.AlertPane.info('Cannot export: Too many layers selected.');
                return NO;

            }

            var record = records.get('firstObject');

            // This is an internal error, don't bug the user about it.
            if (!record.kindOf(Footprint.PresentationMedium)) {
                SC.Logger.debug('Cannot export: selection isn\'t a layer.');
                return NO;
            }

            Footprint.DataSource.export('export_layer', record);
            SC.AlertPane.info('Exporting the currently selected layer - it will start downloading as soon as it is ready.\n\n' +
                              'Please do not close your UrbanFootprint session.');
            return YES;
        },

        doViewLayer: function() {
            this.get('statechart').sendAction('doViewRecord',  this.get('crudParams'));
        },

        doSaveLayer: function(context) {
            Footprint.layerEditController.set('layerIsSaving', YES);
            this.get('statechart').sendAction('doSave', context);
        },

        doCreateLayer: function() {
            this.get('statechart').sendAction('doCreateRecord', this.get('crudParams'));
        },
        doCloneLayer: function() {
            this.get('statechart').sendAction('doCloneRecord', this.get('crudParams'));
        },
        doCreateLayerFromSelection: function() {
            this.get('statechart').sendAction('doCloneRecord', this.get('crudParams'));
        },
        doUpdateLayer: function() {
            this.get('statechart').sendAction('doUpdateRecord', this.get('crudParams'));
        },
        /***
         * Called from the Footprint.DbEntitiesAreReadyState when new Layers need to
         * be saved for new DbEntities
         */
        doSaveNewLayers: function(context) {
            Footprint.statechart.gotoState('layerCrudState',
                SC.ArrayController.create({
                    content: context.get('content'),
                    recordType: this.get('baseRecordType'),
                    recordsEditController: this.get('recordsEditController')
                })
            )
        },


        /***
         * Handles picking a behavior from selector. Results in updating the FeatureBehavior behavior
         * @param context
         * @returns {window.NO|*}
         */
        doPickBehavior: function(context) {
            // Our context is the SourceListView from which the user selected an item
            var behavior = context.getPath('selection.firstObject');
            if (!behavior)
                return;
            var containerLayer = Footprint.layersEditController.getPath('selection.firstObject');
            var featureBehavior = containerLayer.getPath('db_entity.feature_behavior');

            // This should never happen, but does
            if (!featureBehavior.get('parentRecord')) {
                logWarning('featureBehavior had no parent! Can\'t write to it');
                return;
            }

            featureBehavior.setIfChanged('behavior', behavior);
            featureBehavior.setIfChanged('intersection', behavior.get('intersection'));

            if (!containerLayer.getPath('db_entity.feature_behavior')) {
                logWarning('featureBehavior had no parent! Can\'t write to it');
                return;
            }

            containerLayer.setPath('db_entity.feature_behavior.behavior', behavior);
        },

        /**
         * Generate a temporary key for this object, until it is written to the database.
         */
        _generateActiveStyleKey: function(activeLayerKey) {
            var date = new Date();
            return '%@__%@_%@_%@_%@'.fmt(activeLayerKey, date.getDay(), date.getHours(), date.getMinutes(), date.getSeconds());
        },
        /**
         * This is the first name
         */
        _generateActiveStyleName: function(activeLayerName) {
            var date = new Date();
            return '%@ %@-%@-%@'.fmt(activeLayerName, date.getMonth(), date.getDay(), date.getFullYear());
        },
        /***
         * Responds to changing the selection of the Footprint.stylableAttributesController
         * by adding a new Footprint.StyleAttribute to the Footprint.styleableAttributesEditController
         * if it is needed.
         */
        addStyleAttribute: function(context) {
            var stylableAttribute = context.get('content'),
                activeLayerKey = Footprint.layerActiveController.getPath('db_entity.key'),
                activeLayerName = Footprint.layerActiveController.getPath('db_entity.name'),
                activeStyleKey= this._generateActiveStyleKey(activeLayerKey);

            if (!stylableAttribute) {
                // No selection, clear the controller selection and quit
                Footprint.styleableAttributesEditController.deselectObjects(
                    Footprint.styleableAttributesEditController.get('selection')
                );
                return;
            }

            //create a new styled attribute defaulted to a SINGLE style type with opacity of 1 User will be able to
            //updated the style type and attribute from the UI
            var styleAttribute = Footprint.styleableAttributesEditController.get('content').createNestedRecord(
                Footprint.StyleAttribute, {
                    name: this._generateActiveStyleName(activeLayerName),
                    key: activeStyleKey,
                    attribute: null,
                    opacity: 1,
                    style_type: 'single',
                    style_value_contexts: []
                });
            // Add and new style value context with empty attributes
            var styleValueContext = styleAttribute.get('style_value_contexts').createNestedRecord(
                Footprint.StyleValueContext, {
                    value: null,
                    style: null,
                    symbol: null
                });
            //create default style for the single value for the style value context
            var style = styleValueContext.createNestedRecord(
                Footprint.Style, {
                    'polygon-fill': '#ADD8E6',
                    'polygon-opacity': 1,
                    'line-color': '#587272',
                    'line-width': 1,
                    'line-opacity': 1
                });
            //set the style value context to the default style
            styleValueContext.set('style', style);
            //set the selection to the new styled attribute on the layer
            Footprint.styleableAttributesEditController.selectObject(styleAttribute);
            //update the active style to reflect the newly added style - this will also be the selection
            F.layerEditController.set('active_style_key', activeStyleKey);
        },

        removeStyleAttribute: function(context) {
            var objectToRemove = context.get('content');
            if (!objectToRemove) {
                return;
            }
            objectToRemove.destroy();
            Footprint.styleableAttributesEditController.getPath('content').removeObject(objectToRemove);

            if (!Footprint.styleableAttributesEditController.getPath('selection.firstObject')) {
                var firstObject = Footprint.styleableAttributesEditController.getPath('content.firstObject');
                Footprint.styleableAttributesEditController.selectObject(firstObject);
            }
        },

        addStyleValueContext: function(context) {
            var styleValueContexts = Footprint.styleValueContextsEditController.getPath('content');
            if (!styleValueContexts) {
                return;
            }
            // Add and new style value context with empty attributes
            var styleValueContext = Footprint.styleValueContextsEditController.getPath('content').createNestedRecord(
                Footprint.StyleValueContext, {
                    value: 0,
                    style: null,
                    symbol: '>='
                });
            //create default style for the single value for the style value context
            var style = styleValueContext.createNestedRecord(
                Footprint.Style, {
                    'polygon-fill': '#ADD8E6',
                    'polygon-opacity': 1,
                    'line-color': '#587272',
                    'line-width': 1,
                    'line-opacity': 1
                });
            //set the style value context to the default style
            styleValueContext.set('style', style);
        },

        removeStyleValueContext: function(context) {
            var objectToRemove = context.get('content');
            if (!objectToRemove) {
                return;
            }
            objectToRemove.destroy();
            Footprint.styleValueContextsEditController.getPath('content').removeObject(objectToRemove);

            if (!Footprint.styleValueContextsEditController.getPath('selection.firstObject')) {
                var firstObject = Footprint.styleValueContextsEditController.getPath('content.firstObject');
                Footprint.styleValueContextsEditController.selectObject(firstObject);
            }
        },

        setDefaultSingleStyleType: function() {
            var selection = Footprint.styleValueContextsEditController.getPath('selection'),
                styleValueContexts = Footprint.styleValueContextsEditController.getPath('content');

            if (!styleValueContexts) {
                return;
            }
            Footprint.styleValueContextsEditController.deselectObjects(selection);
            styleValueContexts.forEach(function(styleValueContext) {
                if (styleValueContext)
                    styleValueContext.destroy();
                Footprint.styleValueContextsEditController.getPath('content').removeObject(styleValueContext);
            });
            // Add and new style value context with empty attributes
            var styleValueContext = Footprint.styleValueContextsEditController.getPath('content').createNestedRecord(
                Footprint.StyleValueContext, {
                    value: null,
                    style: null,
                    symbol: null
                });
            //create default style for the single value for the style value context
            var style = styleValueContext.createNestedRecord(
                Footprint.Style, {
                    'polygon-fill': '#ADD8E6',
                    'polygon-opacity': 1,
                    'line-color': '#587272',
                    'line-width': 1,
                    'line-opacity': 1
                });
            //set the style value context to the default style
            styleValueContext.set('style', style);
        },

        setDefaultNonSingleStyleType: function() {
            //removes all style value contexts
            var selection = Footprint.styleValueContextsEditController.getPath('selection'),
                styleValueContexts = Footprint.styleValueContextsEditController.getPath('content');

            if (!styleValueContexts) {
                return;
            }
            Footprint.styleValueContextsEditController.deselectObjects(selection);
            styleValueContexts.forEach(function(styleValueContext) {
                if (styleValueContext) {
                    styleValueContext.destroy();
                    Footprint.styleValueContextsEditController.getPath('content').removeObject(styleValueContext);
                }
            });
        },

        loadFeatureAttributes: function(context) {
            context.get('loadingController').set('isProcessing', YES);
            this.get('statechart').sendAction('setDefaultNonSingleStyleType');
            this.loadingFeatureAttributeState.set('symbologyType', context.get('symbologyType'));
            this.gotoState('loadingFeatureAttributeState', context);
        },

        configureCategoricalStyleAttributes: function() {
            var unique_values = Footprint.FeatureCategoryController.getPath('content.firstObject.unique_values').sort();

            unique_values.forEach(function(field) {
                var styleValueContexts = F.styleValueContextsEditController.get('content');
                var styleValueContext = styleValueContexts.createNestedRecord(Footprint.StyleValueContext, {
                    value: field,
                    style: null,
                    symbol: '='
                });
                    //create default style for the single value for the style value context
                var style = styleValueContext.createNestedRecord(
                    Footprint.Style, {
                        'polygon-fill': '#ADD8E6',
                        'polygon-opacity': 1,
                        'line-color': '#587272',
                        'line-width': 1,
                        'line-opacity': 1
                    });
                //set the style value context to the default style
                styleValueContext.set('style', style);
            });
            Footprint.FeatureCategoryController.set('isProcessing', NO);
        },

        configureQuantitativeStyleAttributes: function() {
            var content = Footprint.FeatureQuantitativeController.getPath('content.firstObject'),
                min = parseFloat(content.get('min')),
                max = parseFloat(content.get('max')),
                range = max - min > 0 ? max - min: 0,
                quantiles = range > 0 ? 5: 1,
                quantileRange = range > 0 ? Math.floor(range / quantiles): 0,
                currentValue = min,
                i=0;

            while (i <= quantiles -1)  {
                currentValue = i == quantiles - 1 ? max: currentValue;
                var styleValueContexts = F.styleValueContextsEditController.get('content');
                var styleValueContext = styleValueContexts.createNestedRecord(Footprint.StyleValueContext, {
                    value: currentValue,
                    style: null,
                    symbol: '>='
                });
                    //create default style for the single value for the style value context
                var style = styleValueContext.createNestedRecord(
                    Footprint.Style, {
                        'polygon-fill': '#ADD8E6',
                        'polygon-opacity': 1,
                        'line-color': '#587272',
                        'line-width': 1,
                        'line-opacity': 1
                    });
                //set the style value context to the default style
                styleValueContext.set('style', style);
                currentValue = currentValue + quantileRange;
                i+=1;
            }
            Footprint.FeatureQuantitativeController.set('isProcessing', NO);
        },

        loadingFeatureAttributeState: SC.State.plugin('Footprint.LoadingFeatureAttributeState'),

        // --------------------------
        // Post-processing
        //
       /***
        * Update the layerLibrary of the layer to insert or remove the layer if needed
        * This checks for membership by id for the case that the layerLibrary is the main store version and
        * the layer is the nested store version.
        * @param layer
        * @param layerLibrary
        */
        _updateLayerLibrary: function(layer, layerLibrary) {
            if (layer.get('status') & SC.Record.DESTROYED || layer.get('deleted')) {
                layerLibrary.get('layers').removeObject(layer);
            }
            else {
                var layers = layerLibrary.get('layers').filter(function(lay) { return lay.get('id') == layer.get('id');});
                if (!layers.length){
                    layerLibrary.get('layers').pushObject(layer);
                }
            }
        },

        /***
         * Removes the give Layer from the LayerLibrary if it is there
         * We assume that the layer and layerLibrary are both part of the same nestedStore
         * @param layer
         * @param layerLibrary
         * @private
         */
        _removeFromLayerLibrary: function(layer, layerLibrary) {
            if (layer.get('status') & SC.Record.DESTROYED ||
                layer.get('deleted') ||
                layerLibrary.get('layers').contains(layer)) {
                layerLibrary.get('layers').removeObject(layer);
            }
        },

        /***
         * Refreshes the layer since it will pick up new attributes during post save
         * @param context
         */
        postSavePublishingFinished: function(context) {
            // Handle anything DbEntity-related here
            // Send this event for analysis tools
            this.get('statechart').sendEvent('dbEntityDidUpdate', context);
        },

        // Override
        postSavePublisherProportionCompleted: function(context) {

            var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
            if (!recordType.kindOf(Footprint.Layer)) {
                SC.Logger.debug('Not handled: postSavePublisherProportionCompleted');
                return NO;
            }

            function eventHandler() {
                // Post save layer presentation only has one signal, indicating completion.
                var layer = Footprint.store.find(SC.Query.local(Footprint.Layer, {
                    // Use $ to compare ids since the layer's version is nested and
                    // the incoming is not, so they won't share storeKeys
                    conditions: 'id = %@',
                    parameters: [context.get('ids')[0]]
                })).firstObject();

                if (layer) {
                    // This is the layer that was just created/updated
                    this.commitConflictingNestedStores([layer]);
                    layer.refresh();
                    Footprint.mapLayerGroupsController.refreshLayers([layer.get('dbEntityKey')]);
                }
                else {
                    // This layer was just created/updated for another scenario because the main
                    // layer was created at project scope. Load the layer remotely to get it in the store.
                    var layerQuery = Footprint.store.find(SC.Query.create({
                        recordType:Footprint.Layer,
                        location:SC.Query.REMOTE,
                        parameters:{
                            // We use the layer_selection instead of listing all the feature ids, to prevent
                            // overly long URLs
                            id:context.getPath('ids.firstObject')
                        }
                    }));
                    layerQuery.addObserver('status', this, 'layerQueryStatusDidChange');
                }
                Footprint.layerEditController.set('layerIsSaving', NO);
            }
            if (this._crudFinished) {
                // Run the handler immediately if CRUD is already finished
                eventHandler.apply(this);
            }
            else {
                // Queue it up
                this._eventHandlerQueue.pushObject(eventHandler);
            }

            return YES;
        },

        /***
        * If something goes during post-save, treat it like an save error
        * @param context
        */
        postSavePublishingDidFail: function(context) {
            var ret = sc_super();
            if (!ret)
                return ret;
            context.getPath('records').map(function(layer) {
                layer.set('layerIsSaving', NO);
            });
        },

        layerQueryStatusDidChange: function(layerQuery) {
            if (layerQuery.get('status') === SC.Record.READY_CLEAN) {
                var layer = layerQuery.get('firstObject');
                this.updateLayerLibrary(layer);
            }
        },

        /***
         * Updates the layer library of the layer that was just CRUDed
         * @param layer
         */
        updateLayerLibrary: function(layer) {
            var layerLibrary = F.store.materializeRecord(layer.getPath('presentation.storeKey'));
            if (layerLibrary.get('status') & SC.Record.READY) {
                // If the LayerLibrary already in the store, update it. Otherwise do nothing.
                this._updateLayerLibrary(
                    // Use the main store Layer. The incoming Layer is from a nested Store
                    Footprint.store.materializeRecord(layer.get('storeKey')),
                    layerLibrary);
            }
        },

        postSavePublishingFailed: function(context) {
            // Override the parent class
            // The context (nee the socket event) gives us enough information to
            // get the DbEntity. From there, we can query the corresponding
            // failed layer.
            if (context.get('class_name') !== 'DbEntity') return NO;
            var failedRecord = F.store.find(Footprint.DbEntity, context.get('id')),
                failedLayer = F.store.find(SC.Query.local(F.Layer, {
                    conditions: 'db_entity = %@',
                    parameters: [failedRecord]
                })).firstObject();
            if (!failedLayer) return NO;
            var failedLayerName = failedLayer.get('name'),
                layerLibrary = failedLayer.get('presentation'),
                layerLibraryStatus = layerLibrary.get('status');
            // Delete the failed layer, and remove it from its LayerLibrary.
            var nestedStore = Footprint.statechart.getState('showingAppState.crudState.modalState')._store;
            if (nestedStore && nestedStore.locks[layer.get('storeKey')])
                nestedStore.commitChanges();
            failedRecord.destroy();
            failedLayer.destroy();
            layerLibrary.get('layers').removeObject(failedLayer);
            F.store.writeStatus(layerLibrary.get('storeKey'), layerLibraryStatus);
            // Show an alert.
            SC.AlertPane.warn({
                message: 'Layer Creation Failed',
                description: 'There was an error processing "%@". Please try again, and if this continues, please report to your system administrator.'.loc(failedLayerName)
            });
            this._postSavePublisherFailed(context);
            return YES;
        },

        // Internal support
        enterState: function(context) {
            this._store = Footprint.store.get('autonomousStore');
            this._content = this._store.find(SC.Query.local(
                Footprint.Layer, {
                    conditions: '{storeKeys} CONTAINS storeKey',
                    storeKeys:context.mapProperty('storeKey')
                })).toArray();
            this._context = SC.ArrayController.create({content: this._content, recordType:context.get('recordType')});

            this.setPath('recordsEditController.store', this._store);
            sc_super();
        },

        exitState: function() {
            this._store = null;
            sc_super();
        },

        /***
         *
         * The undoManager property on each layer
         */
        undoManagerProperty: 'undoManager',

        updateContext: function(context) {
            var recordContext = SC.ObjectController.create();
            return this.createModifyContext(recordContext, context);
        },

        /**
         * Reload the new DbEntity to get the Layer reference
         */
        reloadNewDbEntity: Footprint.LoadingState.extend({
            didLoadEvent:'newDbEntityDidReload',
            didFailEvent:'newDbEntityDidFail',
            recordType: Footprint.DbEntity,
            checkRecordStatuses: YES,

            /***
             * Simply load the new Layer of the DbEntity
             * @returns {*}
             */
            recordArray: function(context) {
                // Start the load. This should make the record busy
                context.get('dbEntity').refresh();
                // Wait for it
                return [context.get('dbEntity')];
            },

            /***
             * Once reloaded load the layer
             * @param context
             */
            newDbEntityDidReload: function(context) {
                this.gotoState(this.parentState.loadingNewLayer, SC.Object.create({dbEntity: context.get('content')[0]}));
            }
        }),

        loadingNewLayer: Footprint.LoadingState.extend({
            didLoadEvent:'newLayerDidLoad',
            didFailEvent:'newLayerDidFail',
            recordType: Footprint.Layer,
            checkRecordStatuses: YES,

            /***
             * Simply load the new Layer of the DbEntity
             * @returns {*}
             */
            recordArray: function(context) {
                return [context.getPath('dbEntity.layer')];
            },

            /***
             * Add the layer to the Application LayerLibrary
             * Also make the Layer application visible so it appears immediately
             * @param context
             */
            newLayerDidLoad: function(context) {
                var theLayer = this.getPath('loadingController.firstObject');
                // Make the layer visible in the application. This does not make it checked
                // by default when the app reloads
                theLayer.set('applicationVisible', YES);
                this.parentState.doAddOrRemoveLayerFromApplicationLayerLibrary(
                    SC.Object.create({theLayer: this.getPath('loadingController.firstObject'), value: YES})
                );
                // Tell the map to refresh the new layer so we see it immediately
                // invokeNext so the layer has time to get in the Footprint.layersForegroundController
                this.invokeNext(function() {
                    Footprint.mapLayerGroupsController.refreshLayers([theLayer.getPath('db_entity.key')]);
                })
            }
        }),


        /***
        * Does a simple LayerLibrary update to add or remove a Layer from the library
        */
        updatingLayerLibraryState: Footprint.RecordsAreReadyState.extend({
            recordsDidUpdateEvent: 'layerLibraryDidUpdate',
            recordsDidFailToUpdateEvent: 'layerLibraryDidFail',

            doUpdateRecordsImmediately: function(context) {
                this.updateRecords(context);
            },

            /***
             * The content of the context are the LayerLibraries to udpate.
             * We also pass in the layer as theLayer so that we can make
             * @param context
             */
            enterState: function(context) {
                this._store = Footprint.store.get('autonomousStore');
                this._content = context.get('content');
                this._context = SC.ArrayController.create({content: this._content, recordType: Footprint.LayerLibrary});

                sc_super();

                this.invokeNext(function() {
                    Footprint.statechart.sendAction('doUpdateRecordsImmediately', context);
                })
            },

            layerLibraryDidUpdate: function(context) {
                // Redo the add or update without save to the main store version
                this.parentState.doAddOrRemoveLayerFromApplicationLayerLibrary(SC.Object.create({
                    content: context.get('content'),
                    theLayer: context.getPath('theLayer.mainStoreVersion'),
                    value: context.get('value')
                }))
            }
        }),

    }),

});
