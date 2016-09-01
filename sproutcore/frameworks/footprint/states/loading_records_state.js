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
 * LoadingRecordsState takes an content and loads all childRecords in parallel.
 * Upon completion it sends didLoadRecords
 * @type {*}
 */
Footprint.LoadingRecordsState = SC.State.extend({
    enterState:function(context) {
        this._context = context;
        if (this._context.getPath('content.length')==0) {
            // I don't think should ever happen
            this.get('statechart').sendEvent('didLoadRecords', this._context);
            return;
        }

        // Due to a bug in calling retrieveRecords with nestedStores, we get
        // all the parent store records and access their properties. This
        // success in loading the records in the parent store and updating the nested store versions.
        var mainStore = context.getPath('content.firstObject.store.parentStore');
        var mainStoreContent = context.get('content').map(function(record) {
            return mainStore.materializeRecord(record.get('storeKey'));
        });

        // This returns a flattened list of pairs of child attributes in the form
        //{key:property_string, value:property value}
        var childRecordPairs = $.shallowFlatten(mainStoreContent.map(function(record) {
            return record.loadAttributes();
        }));
        this._childRecords = childRecordPairs.mapProperty('value');
        this._childRecordsQueue = SC.Set.create(this._childRecords);
        this._childRecords.forEach(function(childRecord) {
            // Make sure child attributes are loaded
            childRecord.addObserver('status', this, 'childRecordStatusDidChange');
        }, this);
        this.childRecordStatusDidChange();
    },
    childRecordStatusDidChange: function() {
        this.invokeOnce(this._childRecordStatusDidChange);
    },
    _childRecordStatusDidChange: function() {
        this._childRecords.forEach(function(childRecord) {
            if (childRecord.get('status') & SC.Record.READY) {
                this._childRecordsQueue.remove(childRecord);
                childRecord.removeObserver('status', this, 'childRecordStatusDidChange');
            }
        }, this);
        if (this._childRecordsQueue.length == 0) {
            this.get('statechart').sendEvent('didLoadRecords', this._context);
        }
    }
});
