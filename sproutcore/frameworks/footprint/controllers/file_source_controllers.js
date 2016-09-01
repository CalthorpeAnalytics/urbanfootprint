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

// ==========================================================================
// Project:   Footprint.fileSourcesController
// ==========================================================================
sc_require('models/file_source_model');

/** @class
 A list of Footprint.FileDataset records.
 A FileDataset is created or updated by socket_io messages when progress on an item comes in
 @extends SC.ObjectController
 */
Footprint.fileSourcesController = SC.ArrayController.create({
    allowsEmptySelection: NO,

    /***
     * Select the FileSource with the lastest UUid by default.
     * The uuid is the Sproutcore-generated unique id for each file upload.
     * The user can then select older uploading/uploaded FileSources
     * If the latest uuid isn't in the list yest we won't select anything
     */
    firstSelectableObject: function () {
        return this.find(function (fileSource) {
            return fileSource.get('id') == this.get('latestUuid');
        }, this);
    }.property(),

    /***
     * The most recent upload id. Used to find the firstSelectableObject
     */
    latestUuid: null,

    orderBy: ['id DESC']
});

/***
 * This is used by the UploadProgressListView to track the upload of the
 * Footprint.FileSource or the processing of each of a FileSource's Footprint.Dataset.
 * A FileSource is only included until one of its DataSets becomes available. The
 * Dataset always begins with the progress of the FileSource. This give the user the
 * visual of the FileSource progress being replaced by one or more Dataset progress bars.
 * FileSource and FileDataset never load or save, so their statuses do not matter
 */
Footprint.fileSourcesAndDatasetsController = SC.ArrayController.create({
    fileSources: null,
    fileSourcesBinding: SC.Binding.oneWay('Footprint.fileSourcesController.content'),
    fileDatasets: null,
    fileDatasetsBinding: SC.Binding.oneWay('Footprint.fileDatasetsController.content'),

    /***
     * Since SC doesn't track membership, use this observer
     */
    collectionLengthObserver: function() {
        this.invokeOnce(this._collectionLengthObserver);
    }.observes('Footprint.fileSourcesController.[]', 'Footprint.fileDatasetsController.[]'),

    _collectionLengthObserver: function() {
        this.propertyDidChange('content');
    },

    content: function() {
        // Return each FileSource or the Datasets of each FileSource if the latter exist
        return (this.get('fileSources') || []).map(function(fileSource) {
            var fileDatasets = (this.get('fileDatasets') || []).filterProperty('file_source', fileSource);
            if (fileDatasets.get('length'))
                return fileDatasets;
            // If no datasets have been created for the FileSource, return it, otherwise ignore it.
            else if (!fileSource.get('datasetsCreated'))
                return [fileSource];
            else
                return []
        }, this).flatten();
    }.property('fileSources', 'fileDatasets').cacheable(),
    // orderId is the FileSource id for both record types. If they match we sort by name
    orderBy: ['orderId DESC', 'file_name ASC']
});
