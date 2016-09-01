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

sc_require('states/loading_state');
/**
*
* Loads an associated record from each parent record passed in. This currently assumes that each associated record
* must be loaded with a separate call. The code could easily be refactored to support a single call
*/
Footprint.LoadingLocalOrRemoteState = Footprint.LoadingState.extend({

    /***
     * Default YES, calls the remote query for all records. If NO, calls the remote query for each sought record
     */
    useSingleRemoteQuery: YES,

    /***
     * Records, ids, etc to load. These are passed to localQueryDict and remoteQueryDict
     * @param context. An SC.Observable whose content contains DbEntities
     * @returns {*}
     */
    records: function(context) {
        throw "Must override in subclass";
    },

    /***
     * Returns a dict of the conditions and parameters of the local query to see if the sought records are already
     * in the store
     * @param records: THe records from the records function
     * @returns {{conditions: string, records: *}}
     */
    localQueryDict: function(records) {
        throw "Must override in subclass";
    },

    /***
     * The parameters to fetch the sought records remotely
     * @param record
     * @returns
     */
    remoteQueryDict: function(record) {
        throw "Must override in subclass";
    },

    /***
     * Use the already loaded records to determine which aren't yet loaded
     * @param records
     * @param localRecords
     * @returns {*}
     */
    nonLocalRecords: function(records, localRecords) {
        throw "Must implement in subclass";
    },

    /***
     * Fetches the records
     */
    recordArray: function(context) {
        var store = Footprint.store;

        // Get the main store version of each associating (parent) record
        var records = this.records(context);

        // Look in the store first.
        var localRecords = store.find(SC.Query.create(
            merge({
                recordType: this.get('recordType'),
                location: SC.Query.LOCAL
            }, this.localQueryDict(records)))
        );

        if (localRecords.get('length') == records.get('length')) {
            return context.get('content').isEnumerable ?
                [localRecords] : // array of queries to match the remote case
                localRecords;
        }
        else {
            // If we haven't fetched any of the assoiated records yet, get them now
            var nonLocalRecords = this.nonLocalRecords(records, localRecords)
            if (this.get('useSingleRemoteQuery')) {
                var ret = Footprint.store.find(SC.Query.create({
                    recordType: this.get('recordType'),
                    location: SC.Query.REMOTE,
                    parameters: this.remoteQueryDict(records)
                }));
            }
            else {
                 var ret = nonLocalRecords.map(function (record) {
                    return Footprint.store.find(SC.Query.create({
                        recordType: this.get('recordType'),
                        location: SC.Query.REMOTE,
                        parameters: this.remoteQueryDict(record)
                    }));
                }, this);
            }
            // If we have multiple results return them all and we'll check individual query statuses
            // using checkRecordStatuses==YES, otherwise just return the single query result
            return context.get('content').isEnumerable || this.get('useSingleRemoteQuery') ?
                ret:
                ret.get('firstObject')
        }
    },

});
