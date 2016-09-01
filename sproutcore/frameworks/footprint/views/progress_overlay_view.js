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
 * Shows a ProgressView based on the value of progress property
 */
Footprint.ProgressOverlayView = SC.View.extend({
    childViews: ['loadingProgressOverlayView', 'errorProgressOverlayView'],
    classNames: ['progress-overlay-view'],

    /***
     * The content whose status is being observed. This must be non-null to show the overlay
     */
    content:null,

    /***
     * The current progress between 0 and 1.
     */
    progress: null,

    /***
     * The content status
     */
    status:null,
    statusBinding:SC.Binding.oneWay('*content.status'),
    /**
     * Indicates that whether or not the overlay is visible
     */
    isOverlayVisible:null,

    // Show the progress bar if the record is not ready or the isOverlayVisible is true
    isVisible: function() {
        return this.get('content') && this.get('isOverlayVisible');
    }.property('content', 'isOverlayVisible').cacheable(),

    loadingProgressOverlayView: SC.ProgressView.extend({
        classNames: ['loading-progress-overlay-view'],
        isRunning: YES,
        notError: YES,
        notErrorBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR).not(),
        isVisibleBinding: SC.Binding.and('.notErrorBinding', '.parentView.isVisible'),
        valueBinding: SC.Binding.oneWay('.parentView*progress'),
        minimum: 0,
        maximum: 1
    }),

    errorProgressOverlayView: SC.ProgressView.extend({
        classNames: ['error-progress-overlay-view'],
        isVisible:NO,
        isVisibleBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.ERROR),
        value: 0,
        minimum: 0,
        maximum: 1
    })
});

/***
 * This progress overlay is used when you need to display progress (managed on parent store
 * records) of a nested store record.
 */
Footprint.ProgressOverlayForNestedStoreView = Footprint.ProgressOverlayView.extend({
    nestedStoreContent: null,
    /***
     * Set by progressDidChange. The progress of each record of content makes up this total,
     * multiplied by the weight in the storeKeyWeight property
     */
    progress: null,
    /***
     * Optional. Apply a weight to each record based on its storeKey. This is useful when
     * the content consists of more than one recordType, and the weight should be applied unevenly
     * This should return an SC.Object that maps the storeKey to the percent of total progress
     */
    storeKeyWeight: null,

    /***
     * Calculates the visibility of the view based on the overall progress being 0 or greater until 1
     * or no progress but at least one record with saveInProgress flag on or status BUSY_COMMITTING or BUSY_CREATING
     */
    isOverlayVisible: function() {
        return (typeof(this.get('progress'))=='number' && this.get('progress') >= 0 && this.get('progress') < 1) ||
            this.get('content').find(function(record) {
                return record.get('saveInProgress') ||
                    [SC.Record.BUSY_CREATING, SC.Record.BUSY_COMMITTING].contains(record.get('status'));
            });
    }.property('progress').cacheable(),

    /***
     * Whenever a saveInProgress flag changes, trigger isOverlayVisible
     */
    saveInProgressObserver: function() {
        this.propertyDidChange('isOverlayVisible');
    },

    nestedStoreContentObserver: function() {
        var nestedStoreRecords = arrayOrItemToArray(this.get('nestedStoreContent') || []).compact();
        if (!nestedStoreRecords.get('length'))
            return;
        SC.ObservableExtensions.observablesPropertyAndStatusObservation('statusObservers', nestedStoreRecords, 'status', this, 'nestedStoreContentDidChange');
    }.observes('.nestedStoreContent'),

    /***
     * Update the content whenever the status of any nested content changes
     */
    nestedStoreContentDidChange: function() {
        this.propertyDidChange('content')
    },

    content: function() {
        // GATEKEEP: No nested content or no items are READY status
        var nestedStoreRecords = arrayOrItemToArray(this.get('nestedStoreContent') || []).compact().filter(function(record) {
            return record.get('status') & SC.Record.READY;
        });
        if (!nestedStoreRecords.get('length'))
            return null;

        // GATEKEEP: Doesn't exist in the master store yet.
        var storeKeys = nestedStoreRecords.mapProperty('storeKey');
        var store = nestedStoreRecords.getPath('firstObject.store.parentStore');
        // Make sure that at least one record is in the main store
        // The check of < 0 is a bug work around for materializeRecord of nested records
        var records = storeKeys.map(function(storeKey) {
            var id = store.idFor(storeKey);
            return id && id > 0 ? store.materializeRecord(storeKey) : null;
        }).compact();
        if (!records.get('length'))
            return null;

        // Change progress property whenever any record's progress or status updates
        SC.ObservableExtensions.observablesPropertyAndStatusObservation('progressObservers', records, 'progress', this, 'progressDidChange');
        // Observer saveInProgress on each record so we know whether or not to show this view
        SC.ObservableExtensions.observablesPropertyAndStatusObservation('saveInProgressObservers', records, 'saveInProgress', this, 'saveInProgressObserver');
        return records;
    }.property('nestedStoreContent').cacheable(),

    /***
     * Called when the progress property changes on any of the content,
     * or when content membership or status changes
     */
    progressDidChange: function() {
        var contentLength = this.getPath('content.length') || 0;
        if (!contentLength)
            return;
        var storeKeyWeight = this.get('storeKeyWeight');
        var self = this;
        this.set(
            'progress',
            this.get('content').reduce(function(percentTotal, record) {
                return percentTotal + (record.get('progress') || 0) *
                    // Weight by the lookup dict
                    ((self.get('storeKeyWeight') && self.getPath('storeKeyWeight.%@'.fmt(record.get('storeKey')))) ||
                    // If no lookup or no storeKey match weight by simple proportion
                     1 / contentLength)
            }, 0)
        );
    }
});

/***
 * This progress overlay is used when you need to display progress
 * of multiple records. Note that this only inherits from ProgressOverlayForNestedStoreView because
 * the latter was setup to handle multiple records. It should be refactored so ProgressOverlayView
 * handles multiple records
 */
Footprint.ProgressOverlayForMultipleRecordsView = Footprint.ProgressOverlayForNestedStoreView.extend({
    _uploadDoneAlertPane: function() {
        SC.AlertPane.plain({
            message: 'Upload Complete',
            description: 'UrbanFootprint will now reload to incorporate the new layer.',
            buttons: [{
                title: 'Reload',
                target: this,
                action: function() {
                    window.location.reload();
                },
            }],
        })
    },

    progressObserver: function() {
        var progress = this.get('progress');

        // Render the alert pane once the upload is complete.
        // Upload progress is a percentage, 1 means 100%.
        if (progress == 1) {
            this._uploadDoneAlertPane();
        }
    }.observes('progress'),

    contentDidChange: function() {
        var records = this.get('content');
        // Change progress property whenever any record's progress or status updates
        SC.ObservableExtensions.observablesPropertyAndStatusObservation('progressObservers', records, 'progress', this, 'progressDidChange');
        // Call immediately once
        this.progressDidChange();
        // Observer saveInProgress on each record so we know whether or not to show this view
        SC.ObservableExtensions.observablesPropertyAndStatusObservation('saveInProgressObservers', records, 'saveInProgress', this, 'saveInProgressObserver');
        // Call immediately once
        this.saveInProgressObserver();
    }.observes('.content'),
});
