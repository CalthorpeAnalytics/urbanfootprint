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



SC.Record.reopen({

    /***
     * Patch to fix status of nestedRecords
     */
    status: function() {
        var parent = this.get('parentRecord');
        if (parent) {
            if (this._sc_nestedrec_isDestroyed)
                return SC.Record.DESTROYED;
            else
                return parent.get('store').peekStatus(parent.get('storeKey'));
        }
        else
            return this.get('store').peekStatus(this.get('storeKey'));
    }.property('storeKey'),


});
SC.mixin(SC.Record, {
    // Special status to indicate a sparseArray is loading additional indexes
    // We use this so that tables don't show a spinning overlay when new records are loading,
    // which would happen if we went to a BUSY state
    // This matches all the adding statuses below
    READY_SPARSE_ARRAY_LOADING: 0x0208, // 520
    // Non-continuous (one-time) add
    READY_SPARSE_ARRAY_ADDING: 0x0209, // 521
    READY_SPARSE_ARRAY_CONTINUOUS: 0x020C, // 524
    // Special status to indicate a sparseArray is incrementally loading all of its indexes
    // This tells the data_source that once one load is finished to move on to the next range of indexes
    READY_SPARSE_ARRAY_CONTINUOUS_WILL_ADD: 0x020D, // 525
    // Temporary status between incremental adds, just so there's a status change to observe
    READY_SPARSE_ARRAY_CONTINUOUS_DID_ADD: 0x020E // 526
});
