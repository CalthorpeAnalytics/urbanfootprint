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


sc_require('views/list_views/upload_progress_list_view');
sc_require('views/remove_button_view');
sc_require('views/info_button_view');
sc_require('views/label_view');

/***
 * Shows an UploadProgressView based on the value of progress property
 * This view extends ProgressOverlayView to offer a way to remove the view
 * when the user is not longer interested in the upload.
 * The content of this view is either a Footprint.FileSource or Footprint.FileDataset.
 */
Footprint.UploadProgressOverlayView = Footprint.ProgressOverlayView.extend({
    childViews: ['titleView', 'loadingProgressOverlayView', 'uploadedView', 'removeView', 'errorLabelView'],
    classNames: ['upload-progress-overlay-view'],

    isOverlayVisible: YES,

    /***
     * The content whose status is being observed. This must be non-null to show the overlay.
     * This is always a Footprint.FileSource or Footprint.FileDataset
     */
    content:null,

    /***
     * The current progress between 0 and 100.
     */
    progress: null,

    // The DbEntity key of the FileDataset. FileSources don't have a DbEntity key, since
    // they represent an uploading file that could resolve to multiple DbEntities
    fileDatasetDbEntityKey: null,
    fileDatasetDbEntityKeyBinding: SC.Binding.oneWay('*content.db_entity_key'),

    /***
     * The DbEntity to which the FileDataset associates, if any
     */
    dbEntity: function() {
        if (!this.get('fileDatasetDbEntityKey'))
            return null;
        // Once we get the new DbEntity from the server, we track it here.
        // We identify it by searching for a FileDataset with thte matching key
        return Footprint.store.find(
            SC.Query.local(Footprint.DbEntity,
            {
                conditions: 'key = {key}',
                key: this.get('fileDatasetDbEntityKey')
            })
        ).get('firstObject') || null;
    }.property('fileDatasetDbEntityKey').cacheable(),

    /***
     * Displays the name of the uploading file, or the name of the DbEntity if available
     * The DbEntity name might have an index added to distinguish it from existing ones of the same name
     */
    titleView: Footprint.LabelView.extend({
        layout: {left: 0, top: 2, height: 16},
        classNames: ['upload-progress-overlay-title-view'],

        fileSourceOrDataset: null,
        fileSourceOrDatasetBinding: SC.Binding.oneWay('.parentView.content'),
        dbEntity: null,
        dbEntityBinding: SC.Binding.oneWay('.parentView.dbEntity').defaultValue(null),
        dbEntityStatus: null,
        dbEntityStatusBinding: SC.Binding.oneWay('*dbEntity.status'),
        value: function() {
            if (!this.get('fileSourceOrDataset'))
                return null;

            // As long as the DbEntity exists we can use its name, otherwise use the FileSource
            // or FileDataset
            if (this.get('dbEntity')) {
                return 'Configuring new layer: %@'.fmt(this.getPath('dbEntity.name'));
            }
            else if (this.get('fileSourceOrDataset').instanceOf(Footprint.FileSource)) {
                return 'Uploading file: %@'.fmt(this.getPath('fileSourceOrDataset.file_name'));
            }
            else if (this.get('fileSourceOrDataset').instanceOf(Footprint.FileDataset)) {
                return 'Processing dataset: %@'.fmt(this.getPath('fileSourceOrDataset.file_name'));
            }
            return null;
        }.property('fileSourceOrDataset', 'dbEntity', 'dbEntityStatus').cacheable(),
    }),

    /***
     * Tracks progress of the uploading item (FileSource and then a FileDataset) and post save of the DbEntity
     * This view displays as long as the FileSource/FileDataset or DbEntity have progress < 1
     */
    loadingProgressOverlayView: Footprint.ProgressOverlayForMultipleRecordsView.extend({
        layout: {left: 10, right: 20, bottom: 4, height: 16},
        classNames: ['loading-progress-overlay-view'],

        fileSourceOrDataset: null,
        fileSourceOrDatasetBinding: SC.Binding.oneWay('.parentView.content').defaultValue(null),
        dbEntity: null,
        dbEntityBinding: SC.Binding.oneWay('.parentView.dbEntity').defaultValue(null),
        dbEntityStatus: null,
        dbEntityStatusBinding: SC.Binding.oneWay('*dbEntity.status'),

        storeKeyWeight: function() {
            var weightLookup = SC.Object.create({});
            // Give the UploadProgress 50% weighting
            if (this.getPath('fileSourceOrDataset'))
                weightLookup.set(this.getPath('fileSourceOrDataset.storeKey'), .5);
            // Give the DbEntity 50% weighting
            if (this.getPath('dbEntity'))
                weightLookup.set(this.getPath('dbEntity.storeKey'), .5);
            return weightLookup;
        }.property('fileSourceOrDataset', 'dbEntity', 'dbEntityStatus').cacheable(),

        /***
         * The tree items we are tracking. If not defined simply set to null. They will be filtered
         * out, but we'll need to count the total number of items in the array.
         */
        content: function() {
            return [this.get('fileSourceOrDataset'), this.get('dbEntity')].compact();
        }.property('fileSourceOrDataset', 'dbEntity', 'dbEntityStatus').cacheable(),

        notError: YES,
        notErrorBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR).not(),
        isRunningBinding: SC.Binding.oneWay('.value').valueEquals(100).not(),
        isVisibleBinding: SC.Binding.and('.parentView.isVisible', '.notError', '.isRunning'),
        minimum: 0,
        maximum: 100
    }),

    uploadedView: Footprint.UpdatedInfoView.extend({
        layout: {left: 10, right: 20, bottom: 2, height: 27},
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        value: null,
        valueBinding: SC.Binding.oneWay('*content.progress'),
        title: 'UF.Uploaded',
        isVisibleBinding: SC.Binding.oneWay('.value').valueEquals(100)
    }),

    /***
     * Removes the Footprint.FileSource or Footprint.FileDataset
     * This removes the FileSource so that when the upload finishes no DbEntities are created and saved
     * For FileDatsets this just hides the progress view. We can't stop the processing.
     */
    removeView: Footprint.RemoveButtonView.extend({
        layout: {right: 4, top: 4, height: 11, width: 10},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        action: function() {
            if (!this.get('content'))
                return null;
            if (this.get('content').instanceOf(Footprint.FileSource))
                return 'removeFileSource';
            else if (this.get('content').instanceOf(Footprint.FileDataset))
                return 'removeFileDataset';
            else
                return null;
        }.property('content').cacheable()
    }),

    errorLabelView: Footprint.LabelView.extend({
        layout: {left: 10, right: 20, bottom: 4, height: 16},
        classNames: ['upload-progress-overlay-error-view'],
        isVisible:NO,
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR),
        title: 'UF.UploadError'
    })
});
