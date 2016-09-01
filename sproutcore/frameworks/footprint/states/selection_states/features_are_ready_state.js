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
 * Updates features
 * @type {*|RangeObserver|Class|void}
 */
Footprint.FeaturesAreReadyState = Footprint.RecordsAreReadyState.extend({

    recordsController: Footprint.featuresActiveController,
    recordsEditController: Footprint.featuresEditController,
    /**
     * Use controller that is specific to the DbEntity of the Features.
     * It establishes default values for certain attributes
     * TODO binding this to the *recordsEditController.defaultsController does not work
     * I have no idea why not
     */
    recordContext: function() {
        return Footprint.featuresActiveController.get('defaultsController');
    }.property(),

    baseRecordType: Footprint.Feature,
    findBySubclassRecordType: YES,
    subclassRecordTypeBinding: SC.Binding.oneWay('*recordsController.recordType'),
    // We need to find the features by their subclass type
    findByBaseRecordType: NO,
    recordsDidUpdateEvent: 'featuresDidUpdate',
    recordsDidFailToUpdateEvent: 'featuresDidFailToUpdate',
    updateAction: 'doFeaturesUpdate',
    undoAction: 'doFeaturesUndo',
    undoAttributesBinding: SC.Binding.oneWay('*recordContext.update.keys').transform(function(value) {
        return value || [];
    }),

    /***
     *
     * The undoManager for the features of the current layerSelection
     */
    undoManagerController: Footprint.layerSelectionActiveController,

    undoManagerProperty: 'featureUndoManager',

    /***
     * if features are already ready, do nothing
     * @returns {Window.YES|*}
     */
    doQuery: function() {
        return YES;
    },

    /***
     * if features are already ready, do nothing
     * @returns {Window.YES|*}
     */
    doSummarize: function() {
        return YES;
    },

    /***
     * Updates the features in the context.content
     * @param context. content is and array of features or an Object controller.
     * Optional maintainApprovalStatus is a flag that when YES maintains to the approvalStatus of the features
     * as they are. If not set it automatically sets the approvalStatus to pending
     * If the context
     */
    doFeaturesUpdate: function(context) {
        var content = context.get('content') || this._content;
        if (!context.getPath('additionalContext.maintainApprovalStatus')) {
            content.forEach(function(feature) {
                feature.setPath('approval_status', 'pending');
            });
        }
        this.setPath('recordsEditController.recordsAreUpdating', YES);
        // Don't pass the full context in case if it's not a controller because it might be a view
        // If it is a controller we want the whole thing because it might be an undo operation that
        // has recordContexts
        if (context.kindOf(SC.Controller)) {
            if (context.get('isUndoContext')) {
                // Undo case
                this.undoRecords(context);
            } else {
                // Redo case
                this.updateRecords(context);
            }
        }
        else
            this.updateRecords(SC.Object.create({content: content}));
    },

    doFeaturesUndo: function(context) {
        this.doRecordUndo(context);
    },
    doFeaturesRedo: function(context) {
        this.doRecordRedo(context);
    },
    doFeaturesRevert: function() {
        this.revertRecords();
    },

    /**
     * When a feature is needed for the identify tool that has not been lazily loaded, load it explicitly
     */
    doLoadPopupFeature: function() {
        this.gotoState(this.loadingPopupFeaturesState);
    },

    /***
     * Any functionality needed after the save completes
     * @param context
     */
    featuresDidUpdate: function(context) {
        // Since we don't user the crud_state we need to call these manually
        this.crudDidStart(context);
        this.crudDidFinish(context);
    },
    /***
     * Override the parent postSavePublisherStarted - features have no proportional progress
     * @param context
     */
    postSavePublisherStarted: function(context) {
        return YES;
    },
    /***
     * Override the parent - simple case, only need to error handle and execute the postSavePublishing logic for
     * feature refresh
     * @param context
     */
    postSavePublisherProportionCompleted: function(context) {
        // Gate keep by recordType
        var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        if (!recordType.kindOf(this.get('baseRecordType'))) {
            SC.Logger.debug('Not handled: postSavePublisherProportionCompleted');
            return NO;
        }
        SC.Logger.debug('Handled portion %@ with proportion %@'.fmt(
            context.get('progress_description'), context.get('proportion')));
        if (this._crudFailed)
            // Quit if we already failed
            return YES;

        var eventHandler = function() {
            this.postSavePublishingFinished(context);
        };
        if (this._crudFinished)
            // Run the handler immediately if CRUD is already finished
            eventHandler.apply(this);
        else
            // Queue it up
            this._eventHandlerQueue.unshiftObject(eventHandler);
        return YES;
    },
    /***
     * Post-save publishing - refresh specific db_entites that population data on backend post save processes
     * ie. the core processes or the agriculture module
     * @param context
     */
    postSavePublishingFinished: function(context) {
        this.setPath('recordsEditController.recordsAreUpdating', NO);
        var dbEntityKey = context.get('class_key');
        var dbEntity = Footprint.dbEntitiesController.findProperty('key', dbEntityKey);
        if (!dbEntity) {
            return
        }

        // If we have a layer associated with a scenario or agriculture builder,
        // reload the Feature instances since the post-processing will update other attributes
        // of the features that were not edited in the client
        if (['behavior__scenario_end_state',
             'behavior__agriculture_scenario',
             'behavior__base_agriculture'].contains(dbEntity.getPath('feature_behavior.behavior.key'))
        ) {
            Footprint.statechart.sendAction('refreshFeatures');
        }

        // Always refresh teh map layers in case the styled attribute was updated
        Footprint.mapLayerGroupsController.refreshLayers([dbEntityKey]);
    },

    // TODO this should be wired up automatically by the base class
    featuresDidFailToUpdate: function(context) {
        this.updateDidFail(context);
    },

    /***
     * Suppress the success message
     * @param context
     * @returns {null}
     */
    successMessage: function(context) {
        return null;
    },

    /***
     * Pops open a window of the feature specified in the context.content
     */
    toggleFeatureRevisions: function(context) {
        this.gotoState('featureRevisionsLoadingState', context);
    },

    /***
     * Loads the remaining features for a SparseArray
     * @param context
     */
    doLoadRemaining: function(context) {
        var sparseArray = context.getPath('content.storeKeys');
        if ((sparseArray instanceof SC.SparseArray)) {
            // If not everything is loaded yet, set the status to load everything,
            // and then request the next
            if (sparseArray.get('length') != sparseArray.definedIndexes().get('length')) {
                sparseArray.set('status', SC.Record.READY_SPARSE_ARRAY_CONTINUOUS);
                // Load the next index to kick off all loading
                sparseArray.loadNext();
            }
        } else {
            Footprint.logError('Expected SC.SparseArray, but didn\'t get one');
        }
    },

    /***
     * If the edit section becomes visible and we have an editable feature whose spare array
     * hasn't fully loaded, we need to do it here
     */
    editSectionDidBecomeVisible: function() {
        var context = this._unnestedContext;
        var sparseArray = context.getPath('content.storeKeys');
        if (Footprint.layerActiveController.get('layerIsEditable') &&
          sparseArray && (sparseArray instanceof SC.SparseArray) &&
          sparseArray.get('length') != sparseArray.definedIndexes().get('length')) {

            // Go to the loadingRemainingState, after which we'll return to this state
            this.gotoState(this.loadingRemainingState, context);
        }
    },

    /***
     * Called on enterState and whenever the sparseArray loadedCount changes
     * @private
     */
    _updateContext: function(context) {
        // If there are features. This is the total count, whether the features
        // are loaded in the sparse array or not
        if (context.get('length') > 0) {
            if (this._content && this._content.isObject)
                this._content.destroy();
            // TODO this triggers a datasource fetch the first time it is called,
            // which is not needed because the remote query already loaded the features
            // We need a way to run this local query without a fetch to first time
            // It's probably happening because we are using a spare array, but I'm not certain
            this._content = this._store.find(SC.Query.local(
                context.get('recordType'), {
                    conditions: '{storeKeys} CONTAINS storeKey',
                    // Only load the storeKeys that are currently in the SC.SparseArray
                    // We'll keep redoing this query whenever the sparse array loads more records
                    storeKeys:context.get('content').mapLoadedRecords(function(record) {
                        return record.get('storeKey');
                    }),
                    // Order by the id ASC so the order matches the active controller
                    orderBy: 'id ASC',
                }
            ));
            // Enable the info, apply, clear, etc buttons
            Footprint.toolController.set('featurerIsEnabled', YES);
        } else {
            // If no features, we are just here to support undo/redo
            this._content = [];
        }
        if (this._context)
            this._context.destroy();
        this._context = SC.ArrayController.create({
            content: this._content,
            recordType: context.get('recordType'),
            layer: context.get('layer'),
        });
        this.setPath('recordsEditController.content', this._context.get('content'));
    },

    /***
     * Whenever the sparseArray loadedCount changes, this event is handled
     */
    featuresSparseArrayDidLoadMore: function() {
        logProperty(this.getPath('recordsController.content.loadedCount'), 'sparseArray loadedCount');
        if (this.getPath('recordsController.content.loadedCount')) {
            this._updateContext(this._unnestedContext);
        }
    },

    /***
     * Sets the store and updates the context to match what has loaded in the sparse array.
     * If we are editing features we need to force all features to load at this point
     * @param context
     */
    enterState: function(context) {
        this._unnestedContext = context;
        this._store = Footprint.store.get('autonomousStore');
        // If the Layer is editable and the editor is showing force the remaining features to load if needed
        // We'll also re-enter this this state if the user opens the editor to force all to load if they
        // haven't yet
        var sparseArray = context.getPath('content.storeKeys');
        if (Footprint.layerActiveController.get('layerIsEditable') &&
            Footprint.mainPaneButtonController.get('editSectionIsVisible') &&
          sparseArray && (sparseArray instanceof SC.SparseArray) &&
            sparseArray.get('length') != sparseArray.definedIndexes().get('length')) {

            // Invoke gotoState next runloop since we are in an enterState
            this.invokeNext(function() {
                // Go to the loadingRemainingState, after which we'll return to this state
                this.gotoState(this.loadingRemainingState, context);
            });
        } else {
            this._updateContext(context);
            sc_super();
        }
    },


    exitState: function() {
        this._store = null;
    },

    /***
     * State for forcing remaining Features to load when the user has selected more features
     * than the sparse array loads by default. Once the
     */
    loadingRemainingState: SC.State.extend({
        initialSubstate: 'readyState',
        readyState: SC.State,

        enterState: function(context) {
            // Force the features to all load
            this.parentState.doLoadRemaining(context);
        },

        /***
         * The DataSource will send this event to tell us all are loaded
         * @param sparseArray
         */
        sparseArrayDidComplete: function(sparseArray) {
            // Go back to the parent state now that we are ready to edit the features
            this.gotoState(this.parentState, this.parentState._unnestedContext);
        },
    }),

    featureRevisionsLoadingState: Footprint.LoadingState.extend({
        didLoadEvent: 'didLoadFeatureRevisions',
        didFailEvent: 'didFailToLoadFeatureRevisions',
        loadingController: Footprint.featureRevisionsController,

        recordArray: function() {
            return Footprint.store.find(SC.Query.create({
                recordType: Footprint.FeatureVersion,
                location: SC.Query.REMOTE,
                parameters: {
                    config_entity:Footprint.featureRevisionsController.get('configEntity'),
                    layer:Footprint.featureRevisionsController.get('layer'),
                    id:this._context.getPath('content.id'),
                },
            }));
        },

        didLoadFeatureRevisions: function(context) {
            // Dependency is loaded, move on.
            this.gotoState('featureRevisionsAreReadyState', this._context);
        },
        didFailToLoadFeatureRevisions: function() {
            // Failure sense us back to the top level
            this.gotoState(this.parentState, this.parentState._context);
        },
    }),

    featureRevisionsAreReadyState: Footprint.RecordsAreReadyState.extend({

        crudParams: function() {
            return {
                infoPane: 'Footprint.FeatureRevisionInfoPane',
                recordsEditController: Footprint.featureRevisionsEditController,
                recordType: Footprint.FeatureVersion,
            };
        }.property().cacheable(),

        doManageFeatureRevisions: function() {
            Footprint.statechart.sendAction('doViewRecord',  this.get('crudParams'));
        },

        enterState: function(context) {
            Footprint.statechart.sendAction('doManageFeatureRevisions');
        },
    }),

    /**
     * When the user inspects a Feature that isn't lazily loaded, we
     * need to load it explicitly The goal here is to get a Feature's
     * info into the popup as soon as possible.  We can't inject this
     * into the Footprint.featuresActiveController because it doesn't
     * know what feature ids it does not have
     *
     * Active when we're loading data for the feature popup. Exits
     * when the data is loaded.
     */
    loadingPopupFeaturesState: Footprint.LoadingState.extend({
        didLoadEvent: 'popupFeatureDidLoad',
        loadingController: Footprint.featurePopupTableController,

        // Set this to YES so that we can see a status in the view
        setLoadingControllerDirectly: YES,

        /***
         * Fetches the features in the Footprint.layerSelectionActive controller via a remote query
         * @returns {*}
         */
        recordArray: function() {
            return Footprint.store.find(SC.Query.create({
                recordType:Footprint.layerSelectionEditController.getPath('layer.featureRecordType'),
                location:SC.Query.REMOTE,
                parameters:{
                    db_entity: Footprint.layerSelectionEditController.getPath('layer.db_entity'),
                    ids: [Footprint.featurePopupTableController.get('featureTablePopupId')],
                },
            }));
        },

        popupFeatureDidLoad: function() {
            // Back to the parent's readyState
            this.gotoState(this.parentState.initialSubstate);
        },

    }),
});
