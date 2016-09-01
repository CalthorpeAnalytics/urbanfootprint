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

sc_require('states/loading_local_or_remote_state');

/**
*
* Loads an associated record from each parent record passed in.
*/
Footprint.LoadingAssociatedRecordsState = Footprint.LoadingLocalOrRemoteState.extend({

    /***
     * Optional, but required if toAttribute is used
     */
    parentRecordType: null,

    /***
     * Optional. The association property from the associated recordType back to the parent record type
     * This may or not be available depending on the direction of the relationshiFootprint.TemplateFeature,
     */
    toAttribute: null,


    /***
     * records that have an associated to load.
     * @param context. An SC.Observable whose content contains DbEntities
     * @returns {*}
     */
    records: function(context) {
        if (!this.get('toAttribute'))
            throw "Must override in subclass";
        var store = Footprint.store;
        return arrayIfSingular(context.get('content')).map(function(record) {
            return store.find(this.get('parentRecordType'), record.get('id'));
        }, this);
    },

    /***
     * Returns a dict of the conditions and parameters of the local query to see if the sought records are already
     * in the store
     * @param records: THe records from the records function
     * @returns {{conditions: string, records: *}}
     */
    localQueryDict: function(records) {
        if (!this.get('toAttribute'))
            throw "Must override in subclass";
        return {
            conditions: '{records} CONTAINS %@'.fmt(this.get('toAttribute')),
            records: records
        }
    },

    /***
     * The parameters to fetch one associated record given a record from records()
     * @param record
     * @returns
     */
    remoteQueryDict: function(record) {
        if (!this.get('toAttribute'))
            throw "Must override in subclass";

        var ret = {};
        ret['%@__id'.fmt(this.get('toAttribute'))] = record.get('id');
        return ret;
    },

    /***
     * Use the already loaded records to determine which aren't yet loaded
     * @param records
     * @param localRecords
     * @returns {*}
     */
    nonLocalRecords: function(records, localRecords) {
        if (!this.get('toAttribute'))
            throw "Must implement in subclass";
        return records.filter(function(record) {
            return !localRecords.mapProperty(this.get('toAttribute')).contains(record);
        }, this);
    },

});
