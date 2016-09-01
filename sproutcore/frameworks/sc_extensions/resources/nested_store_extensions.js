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


SC.NestedStore.reopen({
    /**
     * Adding in storage of what attributes actually changed. SC doesn't
     * keep track of this by default, but it's very important to send to the backend
     * what attributes changed so that we know what publishers to run. We store
     * the changes on the attributes in an _updatedAttributes array. Since the record
     * will already be dirty or new, this won't change the status and will allow us
     * to easily send the array to the server without worrying about retrieving the array
     * from the nested store beforehand.
     *
     * We can also detect when primitives are updated back to their original value by
     * comparing to the main store (assuming a NestedStore here). If all values match
     * then we revert the record to clean
     */
    recordDidChange: function (recordType, id, storeKey, key, statusOnly) {
        sc_super();
        // We can't keep track of change if the record is new and has no parentStore version
        if (this.peekStatus(storeKey) === SC.Record.READY_NEW)
            return;
        // Never react to writing our meta attribute or to writing nested records
        if (!key || key=='_updatedAttributes' ||
            (recordType || this.recordTypeFor(storeKey)).prototype[key].nested ||
            this.materializeRecord(storeKey).get('parentRecord'))
            return;
        var dataHash = this.readDataHash(storeKey);

        var parentStore = this.get('parentStore');
        var parentDataHash = parentStore.readDataHash(storeKey);
        // If the record was just created on the server we won't have a parentStore version yet.
        if (!parentDataHash)
            return;
        // Update the _updatedAttributes by comparing previous updates to the parent store, as well
        // as the attribute value of key, which might be reverting a previous change
        dataHash['_updatedAttributes'] = SC.Set.create(
            [key].concat(dataHash['_updatedAttributes'] || [])
        ).filter(function (attribute) {
            return JSON.stringify(dataHash[attribute]) !== JSON.stringify(parentDataHash[attribute]);
        }, this);

        // Often no primitive or nested values are dirty, but a nonNested child attribute is dirty.
        // Child attributes mark their parent as dirty using propagateToAggregates if a reverse relationship
        // is defined from the child to the parent with aggregate=YES. We override propagateToAggregates
        // in footprint_record.js to add dirty toOne or toMany attributes to _updatedAttributes.
        // dirty toOne or toMany attributes means that the one value is dirty or any of the toMany values are dirty

        // If we now can't detect any primitive or toOne/toMany dirty records discard the change for the record,
        // resetting it to its original store state
        if (!dataHash['_updatedAttributes'].get('length')) {
            this.discardSomeChanges([storeKey]);
        }
        else {
            // write _updatedAttributes
            this.writeDataHash(dataHash);
        }
        return this;
    },

    _discardStoreKeys: [],
    /**
     Uses code from discardChange to just discard to reset records are specified

     @returns {SC.Store} receiver
     */
    discardSomeChanges: function (storeKeys) {
        // any locked records whose rev or lock rev differs from parent need to
        // be notified.
        var locks;
        if ((this.records) && (locks = this.locks)) {
            var pstore = this.get('parentStore'), psRevisions = pstore.revisions;
            var revisions = this.revisions, storeKey, lock, rev;
            storeKeys.forEach(function (storeKey) {
                if (!(lock = locks[storeKey])) return; // not locked.

                rev = psRevisions[storeKey];
                if ((rev !== lock) || (revisions[storeKey] > rev)) {
                    this._notifyRecordPropertyChange(parseInt(storeKey, 10));
                }
            }, this);
        }
        this.resetSome(storeKeys);
        this.flush();
        return this;
    },
    resetSome: function(storeKeys) {

        // If all records are being reset, call reset
        if (this.changelog.get('length') == storeKeys.get('length')) {
            this.reset();
            return;
        }

        // Delete storeKey entries
        storeKeys.forEach(function (storeKey) {
            // create a new empty data store
            //delete this.revisions[storeKey];
            this.statuses[storeKey] = SC.Record.READY_CLEAN;
            if (this.childRecords) {
                // Recursively discardChanges to childRecords
                var childStoreKeys = this.chainedChanges.filter(function(chainedStoreKey) {
                    return this.childRecords[chainedStoreKey] == storeKey;
                }, this);
                if (childStoreKeys.get('length'))
                    this.discardSomeChanges(childStoreKeys);
            }

            // also reset temporary objects and errors
            if (this.chainedChanges)
                this.chainedChanges.removeObject(storeKey);
            if (this.locks)
                this.locks.removeObject(storeKey);
            if (this.editables)
                this.editables.removeObject(storeKey);
            if (this.changelog)
                this.changelog.removeObject(storeKey);
        }, this);

        var dataSource = this.get('dataSource');
        storeKeys.forEach(function (storeKey) {
            this._notifyRecordPropertyChange(parseInt(storeKey, 10), NO);
        }, this);
    }
});
