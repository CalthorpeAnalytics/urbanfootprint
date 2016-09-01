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
 * Tracks file uploads and the DbEntity saves that result.
 * This has concurrent substates so that we can track any number of DbEntity that come in
 */
Footprint.FileUploadState = SC.State.extend({

    /***
     * This message tracks the uploading of the zip file or similar source.
     * In response to an upload progress message, update or create a fileSource
     * @param message
     */
    uploadTaskDatasourceProgressUpdated: function (message) {
        var fileSource = Footprint.fileSourcesController.findProperty('id', message.id);
        if (!fileSource) {
            Footprint.statechart.sendAction('doCreateUploadFileSource', message);
        }
        else {
            Footprint.statechart.sendAction('doUpdateUploadFileSource', merge({fileSource: fileSource}, message));
        }
    },

    /***
     * If we receive an error and can match the FileSource, try to cancel tracking of related records
     * @param message
     */
    uploadTaskDatasourceError: function(message) {
        var fileSource = Footprint.fileSourcesController.findProperty('id', message.id);
        if (!fileSource) {
            logWarning("Received an uploadTaskDatasourceError but could find a matching FileSource")
        }
        else {
            var fileDatsets = Footprint.fileDatasetsController.filterProperty('file_source', fileSource);
            if (fileDatsets.get('length')) {
                var dbEntities = fileDatsets.map(function(fileDataset) {
                    return Footprint.dbEntitiesController.findProperty(key=fileDataset.get('db_entity_key'));
                }, this);
                if (dbEntities.get('length')) {
                    Footprint.statechart.sendAction(
                        'dbEntitiesDidFailToUpdate',
                        SC.Object.create(merge({records: dbEntities}, message))
                    );
                }
            }
        }
    },

    /***
     * This message tracks the processing of a dataset within an uploaded zip file.
     * There are one or more datasets per uploaded zip file
     * In response to an upload dataset progress message, update or create a fileSource
     * @param message
     */
    uploadTaskDatasetProgressUpdated: function (message) {
        var fileDataset = Footprint.fileDatasetsController.findProperty('id', message.id);
        if (!fileDataset) {
            Footprint.statechart.sendAction('doCreateFileDataset', message);
        }
        else {
            Footprint.statechart.sendAction('doUpdateFileDataset', merge({fileDataset: fileDataset}, message));
        }
    },

    uploadTaskDatasetError: function(message) {
        var fileSource = Footprint.fileSourcesController.findProperty('id', message.id);
        if (!fileSource) {
            logWarning("Received an uploadTaskDatasetError but could find a matching FileSource")
        }
        else {
            Footprint.statechart.sendAction(
                'dbEntitiesDidFailToUpdate',
                SC.Object.create(merge({records: [fileSource]}, message))
            );
        }
    },

    /***
     * Responds to a new Footprint.SocketIO state receiving upload progress about a file that
     * does not yet have a Footprint.FileSource to monitor the upload
     * @param context: The message from socketIO, containing:
     *  progress: 0 to 100 progress of the upload
     *  config_entity_id: The scope of the upload
     *  file_name: The name of the uploaded file
     *  x_progress_id: A unique id used by the upload manager that we used for the uuid property
     *  id: The unique id that we use for the FileSource
     */
    doCreateUploadFileSource: function(context) {
        // Reset the nested store so that the Footprint.FileSource goes into it
        Footprint.store.get('autonomousStore').reset();
        // TODO can't set this in the controller directly due to load order
        if (!Footprint.fileSourcesController.get('content'))
            Footprint.fileSourcesController.set(
                'content',
                Footprint.store.find(Footprint.FileSource));

        // Create the record. This will add it to controllers that monitor them
        Footprint.store.createRecord(
            Footprint.FileSource, {
                progress: context.get('progress'),
                config_entity: context.get('config_entity_id') &&
                    Footprint.store.find(Footprint.ConfigEntity, context.get('config_entity_id')),
                file_name: context.get('file_name'),
                name: context.get('file_name').split('.')[0].titleize(),
            },
            context.get('id'));
    },

    /***
     * Modifies the matching FileSource when a progress update comes in
     * @param context: The message from socketIO, plus the existing fileSource
     *  fileSource: The existing Footprint.FileSource that matched the context.id
     *  progress: The progress between 0 and 100
     */
    doUpdateUploadFileSource: function(context) {
        var fileSource = context.get('fileSource');
        // Update the progress, normalizing to 0 to 1
        fileSource.set('progress', context.get('progress') / 100);
        // This should already be set
        if (!this.getPath('fileSource.config_entity'))
            fileSource.set('config_entity', context.get('config_entity_id') ?
                Footprint.store.find(Footprint.ConfigEntity, context.get('config_entity_id')) :
                null);
        // TODO do we need to do anything else here?
    },


    /***
     * Responds to a new Footprint.SocketIO state receiving progress about the dataset of an upload file that
     * does not yet have a Footprint.FileDataset to monitor the progress
     * @param context: The message from socketIO, containing:
     *  progress: 0 to 100 progress of the upload
     *  config_entity_id: The scope of the upload
     *  file_name: The name of the uploaded file
     *  x_progress_id: A unique id used by the upload manager that we used for the uuid property
     *  id: The unique id that we use for the FileDataset
     */
    doCreateFileDataset: function(context) {
        // If for some reason the Footprint.FileSource doesn't exist in the store, ignore
        // the Footprint.FileDataset. It might be that the user reloaded during the upload
        var fileSource = Footprint.fileSourcesController.findProperty('id', context.get('datasource_id'));
        if (!fileSource) {
            logWarning("Could not process new Footprint.FileDataset %@ because the Footprint.FileSource with id %@ does not exist".fmt(
                context.get('name'), context.get('datasource_id')
            ));
            return;
        }
        else {
            // Flag the FileSource as having FileDatasets, which means we no longer show it to the user
            fileSource.setIfChanged('datasetsCreated', YES);
        }

        // TODO can't set this in the controller directly due to load order
        if (!Footprint.fileDatasetsController.get('content'))
            Footprint.fileDatasetsController.set(
                'content',
                Footprint.store.find(Footprint.FileDataset));

        // Create the record. This will add it to controllers that monitor them
        Footprint.store.createRecord(
            Footprint.FileDataset, {
                // Link the FileDataset to the Footprint.FileSource
                file_source: context.get('datasource_id'),
                progress: context.get('progress') / 100,
                file_name: context.get('file_name'),
                name: context.get('file_name').split('.')[0].titleize(),
                dataset_id: context.get('dataset_id')
            },
            context.get('id'));
    },

    /***
     * Modifies the matching FileDataset when a progress update comes in
     * @param context: The message from socketIO, plus the existing fileSource
     *  fileSource: The existing Footprint.FileDattaset that matched the context.id
     *  progress: The progress between 0 and 100
     */
    doUpdateFileDataset: function(context) {
        var fileDataset = context.get('fileDataset');
        // Update the progress, normalizing to 0 to 1
        fileDataset.set('progress', context.get('progress') / 100);
        fileDataset.set('config_entity', context.get('config_entity_id') ?
            Footprint.store.find(Footprint.ConfigEntity, context.get('config_entity_id')) :
            null);
    },

    /***
     *  React to async signal that upload has created a new DbEntity
     *  This happens right after the Footprint.FileDataset progress hits 100
     *  context: An SC.Object with properties of the new DbEntity, including the id
     *  The context also contains file_dataset which is the id of the FileDataset
     */
    doCreateDbEntity: function(context) {
        // Create the DbEntity from the context. This is already on the server
        // so we are just tracking it. We put it in the main store since
        // we aren't actually saving it.
        // It's very likely that we will receive a post-save message from the server before we
        // get this message, in which case the record will get loaded by the Footprint.RecordsAreReadyState
        // So check for existence before creating the record

        var fileDataset = Footprint.fileDatasetsController.findProperty('id', context.get('file_dataset'));
        if (!fileDataset) {
            logWarning("Could not track new DbEntity %@ because the Footprint.FileDataset with id %@ does not exist".fmt(
                context.get('key'), context.get('file_data_set')
            ));
            return;
        }
        var dbEntity = Footprint.dbEntitiesController.findProperty('id', context.get('id'));
        // If for some reason the DbEntity has already been loaded, don't do any tracking
        // This could happen if the user loads the browser while the server is processing new DbEntities
        if (dbEntity)
            return;

        var dbEntity = Footprint.store.createRecord(
            Footprint.DbEntity, {
                key: context.get('key'),
                name: context.get('name'),
                config_entity: context.get('config_entity') // this is the ConfigEntity id
            },
            context.get('id')
        );

        // Tell the FileDataset what it's DbEntity is. We don't save this but use it for removing an unsaved
        // DbEntity if the user removes the FileDataset. We use the key because using the instance
        // causes nested store problems
        fileDataset.set('db_entity_key', dbEntity.get('key'));

        // Create and save the DbEntity and Layer immediately after the dataset is finished
        this.trackNewDbEntityFromServer(dbEntity);
    },

    /***
    * Track the post save progress of a DbEntity that was created on the server
    * We must create a concurrent substate to track each DbEntity
    */
    trackNewDbEntityFromServer: function(dbEntity) {
        var trackNewDbEntitiesState = this.trackNewDbEntitiesState;
        var substateName = 'trackDbEntity%@State'.fmt(dbEntity.get('id'));
        trackNewDbEntitiesState.addSubstate(
            substateName,
            Footprint.TrackNewDbEntityState,
            // Pass the context as an argument. I don't know a way to pass it to enterState
            // Treat the content as an array since the substate expects an array
            {_context: toArrayController({content:dbEntity})}
        );
        // If we are already in the container state reenter it to activate new states
        if (trackNewDbEntitiesState.get('isEnteredState')) {
            trackNewDbEntitiesState.reenter();
        }
        // Otherwise go to the container state
        else {
            this.gotoState(trackNewDbEntitiesState);
        }
    },

    initialSubstate: 'readyState',
    readyState: SC.State,

    trackNewDbEntitiesState: SC.State.extend({
        substatesAreConcurrent: YES
    })
});
