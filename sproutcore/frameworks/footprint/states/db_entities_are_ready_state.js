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

Footprint.DbEntitiesAreReadyState = Footprint.RecordsAreReadyState.extend({
    recordsAreReadyEvent: 'dbEntitiesAreReady',
    baseRecordType: Footprint.DbEntity,
    recordsDidUpdateEvent: 'dbEntitiesDidUpdate',
    recordsDidFailToUpdateEvent: 'dbEntitiesDidFailToUpdate',
    updateAction: 'doDbEntityUpdate',
    undoAction: 'doDbEntityUndo',
    undoAttributes: ['name', 'year', 'description'],
    recordsEditController: Footprint.dbEntitiesEditController,
    crudParams: function() {
        // We need an existing DbEntity to use as a template (for now)
        var template = Footprint.dbEntitiesEditController.getPath('selection.firstObject');
        if (!template || template.get('id') < 0)
            template = Footprint.dbEntitiesEditController.filter(function(dbEntity) { return dbEntity.get('id') > 0; })[0];
        return {
            infoPane: 'DataManagerUI.views.panel',
            recordType: Footprint.DbEntity,
            // We use the Footprint.dbEntitiesEditController as are primary edit controller
            // TODO we might have to refactor CrudState to support an alternative controller so that
            // we can also edit layers
            recordsEditController: this.get('recordsEditController'),
            content:template
        };
    }.property().cacheable(),

    /***
     * When the modal closes return from child states to this state
     */
    modalDidCancel: function(context) {
        if (context.get('recordsEditController') == Footprint.dbEntitiesEditController) {
            this.gotoState(this, this.getPath('parentState.loadingDbEntitiesState.loadingController'));
            return YES;
        }
        return NO;
    },



    doViewDbEntity: function() {
        this.get('statechart').sendAction('doViewRecord', this.get('crudParams'));
    },

    /***
     * After a file is uploaded and the DbEntity and Layer are saved, this allows the user
     * to configure the values of the DbEntity
     * @param context
     */
    doConfigureDbEntities: function() {
        this.get('statechart').sendAction('doViewRecord', this.get('crudParams'));
    },

    /***
     * Removes the given Footprint.FileSource of Footprint.FileDataset.
     * If a Footprint.FileSource is removed, all of its Datasets are too
     * @param context: expects only a 'content' property that is a single FileSource
     */
    removeFileSource: function(context) {
        var fileSource = context.get('content');

        fileSource.get('store').find(SC.Query.local(Footprint.FileDataset, {
            conditions: 'file_source = {file_source}',
            file_source: fileSource
        })).forEach(function (fileDataset) {
            this.removeFileDataset(SC.Object.create({content: fileDataset}));
        }, this);

        // Remove the FileSource from both the nestedStore if a version exists therein and main store
        if (fileSource.getPath('nestedStoreVersion.store'))
            fileSource.getPath('nestedStoreVersion.store').unloadRecord(Footprint.FileSource, fileSource.get('id'));
        fileSource.get('store').unloadRecord(Footprint.FileSource, fileSource.get('id'));
        return YES;
    },

    /***
     * Removes the FileDataset in the context after success or failure making a new Footprint.DbEntity
     * from a Footprint.FileDataset
     * @param context
     */
    removeFileDataset: function(context) {
        var fileDataset = context.get('content');

        // If there is an unsaved DbEntity in the nested store we need to remove it
        var dbEntity = fileDataset.getPath('nestedStoreVersion.db_entity');

        // Remove the FileDataset from both the nestedStore if a version exists therein and main store
        if (fileDataset.getPath('nestedStoreVersion.store'))
            fileDataset.getPath('nestedStoreVersion.store').unloadRecord(Footprint.FileDataset, fileDataset.get('id'));
        fileDataset.get('store').unloadRecord(Footprint.FileDataset, fileDataset.get('id'));

        // Only delete unsaved DbEntities (new or errored)
        if (!dbEntity || !((dbEntity.get('status') == SC.Record.READY_NEW) || (dbEntity.get('status') & SC.Record.ERROR)))
            return;

        // Remove the DbEntity from the ConfigEntities
        dbEntity.getPath('config_entity').forSelfAndChildren(function (configEntity) {
            configEntity.getPath('db_entities').removeObject(dbEntity)
        }, YES);

        if (dbEntity) {
            // Remove the DbEntity if created
            dbEntity.get('store').unloadRecord(Footprint.DbEntity, dbEntity.get('id'));
        }
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

    /***
     * Handles picking a tag from the tag selector.
     * @param context
     * @returns {window.NO|*}
     */
    doPickTag: function(context) {
        return this.addOrSelectAssociatedItem(SC.Object.create({
            content: context.getPath('selection.firstObject'),
            recordType: Footprint.DbEntityTag,
            list: Footprint.dbEntityEditController.getPath('content.tags'),
            comparisonKey: 'tag'
        }));
    },

    /***
     * Add a new tag to the current feature_behavior.tags list. Validation to prevent duplicates should already
     * @param context
     */
    doAddTag: function(context) {
        var value = context.get('value');
        return this.addOrSelectAssociatedItem(SC.Object.create({
            content: Footprint.dbEntityAllTagsEditController.get('content').find(function(tag) {
                return tag.get('tag') == value;
            }) || Footprint.dbEntityTagsEditController.getPath('content.store').createRecord(
                Footprint.DbEntityTag,
                {tag:value}
            ),
            recordType: Footprint.DbEntityTag,
            list: Footprint.dbEntityTagsEditController.get('content'),
            comparisonKey: 'tag'
        }));
    },

    /***
     * Removes a Tag instance from the DbEntity
     * @param context
     */
    doRemoveTag: function(context) {
        // Our context is the SourceListView from which the user selected an item
        var tagToRemove = context.get('content');
        var dbEntityTags = Footprint.dbEntityEditController.getPath('content.tags');
        dbEntityTags.removeObject(tagToRemove);
    },

    /***
     * Lets the user create a new Category for a DbEntity
     * @param context
     * @returns {*|boolean}
     */
    doAddCategory: function(context) {
        var value = context.get('value');
        return this.addOrSelectAssociatedItem(SC.Object.create({
            content: Footprint.dbEntityAllCategoriesEditController.get('content').find(function(category) {
                return category.get('value') == value;
            }) || Footprint.dbEntityTagsEditController.getPath('content.store').createRecord(
                Footprint.DbEntityCategory,
                {key:'DbEntityClassification', value:value}
            ),
            recordType: Footprint.DbEntityCategory,
            list: Footprint.dbEntityCategoriesEditController.get('content'),
            clearListFirst: YES,
            comparisonKey: 'value'
        }));
    },

   // --------------------------
   // Post-processing
   //
   // Note that crudDidStart and crudDidFinish are called directly from Footprint.TrackNewDbEntityState
   // so that they only handle the DbEntity specific to them.
   //

    /***
     * This override adds the DbEntity to the ConfigEntity and all child ConfigEntities.
     * This needs to happen locally even though its already done on the server
     * @param context
    */
    crudDidFinish: function(context) {
        var handled = sc_super();
        if (!handled)
            return;

        var store = Footprint.store;
        // For each dbEntity update its ConfigEntity and all children as needed
        context.get('content').forEach(function(dbEntity) {
            // This is already done on the serer. We do it here to save reloading the ConfigEntities
            dbEntity.getPath('config_entity').forSelfAndChildren(function (configEntity) {
                if (!configEntity.get('db_entities').contains(dbEntity))
                    configEntity.get('db_entities').pushObject(dbEntity);
                // Keep the configEntity clean
                store.writeStatus(configEntity.get('storeKey'), SC.Record.READY_CLEAN);
            }, YES);
        });

    },

    /***
     * Removes the give Layer from the LayerLibrary if it is there
     * @param dbEntity
     * @param configEntity
     * @private
     */
    _removeFromLayerLibrary: function(dbEntity, configEntity) {
        if (dbEntity.get('status') & SC.Record.DESTROYED || dbEntity.get('deleted')) {
            configEntity.get('db_entities').removeObject(dbEntity);
        }
        else {
            if (!configEntity.get('db_entities').contains(dbEntity)) {
                configEntity.get('db_entities').pushObject(dbEntity);
            }
        }
    },

    /***
     * Override to make sure we have the correct DbEntity in context before proceeding.
     * Each DbEntity has its own DbEntitiesAreReadyState. We only want to matching one to run here.
     * @param context
     */
    postSavePublisherStarted: function(context) {
        if (this._context.getPath('content.firstObject.id') != context.getPath('ids.firstObject')) {
            SC.Logger.debug('Not handled: postSavePublisherStarted');
            return;
        }
        sc_super()
    },

    /***
     * Override to make sure we have the correct DbEntity in context before proceeding.
     * Each DbEntity has its own DbEntitiesAreReadyState. We only want to matching one to run here.
     * @param context
     */
    postSavePublisherProportionCompleted: function(context) {
        if (this._context.getPath('content.firstObject.id') != context.getPath('ids.firstObject')) {
            SC.Logger.debug('Not handled: postSavePublisherProportionCompleted');
            return;
        }
        sc_super()
    },

    /***
     * Override for same reason as postSavePublisherProportionCompleted
     * @param context
     */
    postSavePublisherFailed: function(context) {
        if (this._context.getPath('content.firstObject.id') != context.getPath('ids.firstObject'))
            return;
        sc_super()
    },

    /***
     * If we finished saving new DbEntities, we need to save their new Layers
     * We also send dbEntityDidUpdate so concerned states can listen
     * @param context
     */
    postSavePublishingFinished: function(context) {

        context.get('records').forEach(function(db_entity) {

            // Handle anything DbEntity-related here
            // Send this event for analysis tools
            this.get('statechart').sendEvent('dbEntityDidUpdate', context);

            // Add the DbEntity to the ConfigEntity of its scope and all those below.
            // This is already done on the server so just prevents us from reloading ConfigEntities
            context.get('records').forEach(function(dbEntity) {
                dbEntity.get('config_entity').forSelfAndChildren(function (configEntity) {
                    if (!configEntity.getPath('db_entities').contains(dbEntity))
                        configEntity.getPath('db_entities').pushObject(dbEntity);
                }, YES);
            });

            // Load the new Layer and refresh the Footprint.LayerTreeController afterward
            // TODO don't do for existing layers
            Footprint.statechart.sendEvent(
                'doLoadNewLayer',
                SC.Object.create({dbEntity:context.getPath('records.firstObject')})
            );

            // Remove the FileDataset for the underlying DbEntity if the former exists
            var fileDataset = Footprint.store.find(SC.Query.local(
                Footprint.FileDataset, {
                    conditions: 'db_entity_key = {db_entity_key}',
                    db_entity_key: db_entity.getPath('key')
                }
            )).get('firstObject');

            // There were previously some cases where the FileDataset could not be resolved.
            // If this error occurs it probably means there's a sync problem between the nested store and main store
            if (!fileDataset) {
                logWarning('No FileDataset found for DbEntity. This should not happen');
            }
            else {
                Footprint.statechart.sendAction(
                    'removeFileDataset',
                    SC.Object.create({content: fileDataset})
                );
            }
        }, this);

        return YES;
    },

    /***
     * If something goes during post-save, treat it like an save error
     * @param context
     */
    postSavePublishingDidFail: function(context) {
        var ret = sc_super();
        // If the parent method didn't handle the event, don't handle it here either
        if (!ret)
            return ret;
        this.dbEntitiesDidFailToUpdate(context);
    },

    /***
     * If DbEntity save fails, remove the FileDataset.
     * We could delete new DbEntities here too, but they aren't attached to anything so harmless
     */
    dbEntitiesDidFailToUpdate: function(context) {
        context.get('records').forEach(function(db_entity) {
             // Remove the FileDataset for the underlying DbEntity if the former exists
            var fileDataset = Footprint.store.find(SC.Query.local(
                Footprint.FileDataset, {
                    conditions: 'db_entity_key = {db_entity_key}',
                    db_entity_key: db_entity.getPath('key')
                }
            )).get('firstObject');

            // There were previously some cases where the FileDataset could not be resolved.
            // If this error occurs it probably means there's a sync problem between the nested store and main store
            if (!fileDataset) {
                Footprint.logError('No FileDataset found for DbEntity. This should not happen');
            }
            else {
                Footprint.statechart.sendAction(
                    'removeFileDataset',
                    SC.Object.create({content: fileDataset})
                );
            }
        }, this)
    },

    /***
     * Don't show a message since we have progress bars
     * and possibly multiple items finishing at different times
     * @param fullContext
     */
    successMessage: function(fullContext) {
        return null;
    },

    // Internal support
    enterState: function(context) {
        this._store = Footprint.store.get('autonomousStore');
        // This needs to be set immediately so that TemplateFeatures will load
        // TODO TemplateFeatures should load based on the DbEntityActiveController as well
        if (!Footprint.dbEntitiesEditController.get('store')) {
            this._store.reset();
            Footprint.dbEntitiesEditController.set('store', this._store);
        }
        this._content = this._store.find(SC.Query.local(
            Footprint.DbEntity, {
                conditions: '{storeKeys} CONTAINS storeKey',
                storeKeys: context.mapProperty('storeKey')
            })).toArray();
        this._context = SC.ArrayController.create({content: this._content, recordType:context.get('recordType')});
        sc_super();
        // Alert the FeatureMetadataState that it can load metadata
        Footprint.statechart.sendEvent('dbEntitiesDidBecomeReady')
    },

    exitState: function() {
        this._store = null;
        sc_super();
        // Alert the FeatureMetadataState that it cannot load metadata
        Footprint.statechart.sendEvent('dbEntitiesDidBecomeNotReady')
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

});
