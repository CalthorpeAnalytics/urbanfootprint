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


/*
 * Observes each item and sets the status or alternative status property
 */
SC.EnumerableStatus = {
    statusProperty: 'recordsStatus',
    // This can be observed publicly to detect changes in list membership
    observedRecords: null,
    // Set up observers.
    arrayContentDidChangeObserver: function() {
        var observedRecords = this.observedRecords;
        if (!observedRecords) observedRecords = this.observedRecords = [];
        var record, i, len;
        // If any items in observedRecords are not in content, stop observing them.
        len = observedRecords.length;
        for (i = len - 1; i >= 0; i--) {
            record = observedRecords.objectAt(i);
            if (!this.contains(record)) {
                record.removeObserver('status', this, this.calculateStatus);
                observedRecords.removeObject(record);
            }
        }
        // If any item in content is not in observedRecords, observe them.
        len = this.get('length');
        for (i = 0; i < len; i++) {
            record = this.objectAt(i);
            if (record && !observedRecords.contains(record)) {
                record.addObserver('status', this, this.calculateStatus);
                this.invokeOnce(this.calculateStatus);
                observedRecords.pushObject(record);
            }
        }
        // Call immediately to calculate status after an array membership change
        this.calculateStatus();
    }.observes('[]'),

    calculateStatus: function() {
        this.invokeOnce(this._calculateStatus);
    },
    /***
     * Fires whenever the array content changes or if content changes overall
     */
    _calculateStatus: function() {
        var length = this.get('length');
        var maxStatus = 0;
        for (i = 0; i < length; i++) {
            var record = this.objectAt(i);
            if (record) {
                var status = record.get('status');
                maxStatus = status > maxStatus ? status : maxStatus;
            }
        }
        this.setIfChanged(this.get('statusProperty'), maxStatus || SC.Record.EMPTY);
    }
};
/***
 * Use this when we can override the status
 */
SC.ArrayStatus = SC.mixin({}, SC.EnumerableStatus, {
    status: null,
    // By default set the status. Override this to set something else
    statusProperty: 'status'
});
/***
 * Use this to take the max status between status and the individual records
 */
SC.RecordsStatus = SC.mixin({}, SC.EnumerableStatus, {
    recordsStatus: null,
    statusProperty: 'recordsStatus',
    // Rework the status property of SC.RecordArrayController
    status: function() {
        var content = this.get('content');
        ret = content ? content.get('status') : null;
        var status = ret ? ret : SC.Record.EMPTY;
        return [this.get('recordsStatus') || 0, status, SC.Record.EMPTY].filter(function(x) {return x;}).max();
    }.property('content', 'recordsStatus').cacheable(),

    statusObserver: function() {
        // force recalculate recordsStatus when status changes
        this.calculateStatus();
    }.observes('.status')
});
