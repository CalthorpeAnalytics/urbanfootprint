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



// SC.Store (for nested records)
SC.Store.reopen({

    /***
     * I don't understand why this is a problem, but SC can't always
     * retrieveRecords into the main store when a nestedStore has changes.
     * Even worse, the nestedStore has no real changes. Everything in the
     * changelog is status READY_CLEAN. Thus, this hack resets the nestedStore
     * if it doesn't have any real changes. Look for ABL for the change
     *
     * @param storeKey
     * @param statusOnly
     * @param key
     * @returns {*}
     * @private
     */
  _notifyRecordPropertyChange: function(storeKey, statusOnly, key) {

    var records      = this.records,
        nestedStores = this.get('nestedStores'),
        K            = SC.Store,
        rec, editState, len, idx, store, status, keys;

    // pass along to nested stores
    len = nestedStores ? nestedStores.length : 0 ;
    for(idx=0;idx<len;idx++) {
      store = nestedStores[idx];
      status = store.peekStatus(storeKey); // important: peek avoids read-lock
      editState = store.storeKeyEditState(storeKey);

      // when store needs to propagate out changes in the parent store
      // to nested stores
      if (editState === K.INHERITED) {
        store._notifyRecordPropertyChange(storeKey, statusOnly, key);

      } else if (status & SC.Record.BUSY) {
          // ABL hack. There's no reason to throw an error if some records are dirty
          // Only warn if the store hasChanges for records that are clean
          // The default implementation throws an error if this method is called when
          // any record is dirty, which is absurd
           var fakeChanges = store.get('hasChanges') ?
               store.changelog && store.changelog.filter(
                   function(record) {
                       return store.peekStatus(record) === SC.Record.READY_CLEAN;
                   }
               ): [];

           if (fakeChanges && fakeChanges.get('length'))
             logWarning("Nested store has changes to clean records. This should not happen: %@".fmt(
               fakeChanges.join(', ')
             ));
      }
    }

    // store info in changes hash and schedule notification if needed.
    var changes = this.recordPropertyChanges;
    if (!changes) {
      changes = this.recordPropertyChanges =
        { storeKeys:      SC.CoreSet.create(),
          records:        SC.CoreSet.create(),
          hasDataChanges: SC.CoreSet.create(),
          propertyForStoreKeys: {} };
    }

    changes.storeKeys.add(storeKey);

    if (records && (rec=records[storeKey])) {
      changes.records.push(storeKey);

      // If there are changes other than just the status we need to record
      // that information so we do the right thing during the next flush.
      // Note that if we're called multiple times before flush and one call
      // has `statusOnly=true` and another has `statusOnly=false`, the flush
      // will (correctly) operate in `statusOnly=false` mode.
      if (!statusOnly) changes.hasDataChanges.push(storeKey);

      // If this is a key specific change, make sure that only those
      // properties/keys are notified.  However, if a previous invocation of
      // `_notifyRecordPropertyChange` specified that all keys have changed, we
      // need to respect that.
      if (key) {
        if (!(keys = changes.propertyForStoreKeys[storeKey])) {
          keys = changes.propertyForStoreKeys[storeKey] = SC.CoreSet.create();
        }

        // If it's '*' instead of a set, then that means there was a previous
        // invocation that said all keys have changed.
        if (keys !== '*') {
          keys.add(key);
        }
      }
      else {
        // Mark that all properties have changed.
        changes.propertyForStoreKeys[storeKey] = '*';
      }
    }

    this.invokeOnce(this.flush);
    return this;
  },

  /**
  * ABL: One change to check for existance of old children
  * register a Child Record to the parent
  **/
  registerChildToParent: function (parentStoreKey, childStoreKey, path) {
    var parentRecords, childRecords, oldPk, oldChildren, pkRef;

    // Check the child to see if it has a parent
    childRecords = this.childRecords || {};
    parentRecords = this.parentRecords || {};

    // first rid of the old parent
    oldPk = childRecords[childStoreKey];
    if (oldPk) {
      oldChildren = parentRecords[oldPk];
      if (oldChildren) // ABL Add existence check
        delete oldChildren[childStoreKey];
      // this.recordDidChange(null, null, oldPk, key); // ABL No change, was commented out in original
    }
    pkRef = parentRecords[parentStoreKey] || {};
    pkRef[childStoreKey] = path || YES;
    parentRecords[parentStoreKey] = pkRef;
    childRecords[childStoreKey] = parentStoreKey;

    // sync the status of the child
    this.writeStatus(childStoreKey, this.statuses[parentStoreKey]);
    this.childRecords = childRecords;
    this.parentRecords = parentRecords;
  },

    /***
     *
     * @param storeKey
     * @param hash
     * @param status
     * @returns {writeDataHash}
     */
  writeDataHash: function (storeKey, hash, status) {

    // update dataHashes and optionally status.
    if (hash) this.dataHashes[storeKey] = hash;
    if (status) this.statuses[storeKey] = status ;

    // also note that this hash is now editable
    var editables = this.editables;
    if (!editables) editables = this.editables = [];
    editables[storeKey] = 1 ; // use number for dense array support

    var processedPaths={};
    // Update the child record hashes in place.
    if (!SC.none(this.parentRecords) ) {
        var children = this.parentRecords[storeKey] || {},
            childHash;

        for (var key in children) {
            if (children.hasOwnProperty(key)) {
                if (hash) {
                    var childPath = children[key];
                    childPath = childPath.split('.');
                    if (childPath.length > 1) {
                        childHash = hash[childPath[0]][childPath[1]];
                    } else {
                        childHash = hash[childPath[0]];
                    }

                    if(!processedPaths[hash[childPath[0]]]){
                        // update data hash: required to push changes beyond the first nesting level
                        this.writeDataHash(key, childHash, status);
                    }
                    if(childPath.length > 1 && ! processedPaths[hash[childPath[0]]]) {
                        // save it so that we don't processed it over and over
                        processedPaths[hash[childPath[0]]]=true;

                        // force fetching of all children records by invoking the children_attribute wrapper code
                        // and then interating the list in an empty loop
                        // Ugly, but there's basically no other way to do it at the moment, other than
                        // leaving this broken as it was before
                        var that = this;
                        this.invokeLast(function(){
                            // TEMP fix, wrapping object
                            arrayOrItemToArray(that.records[storeKey].get(childPath[0])).forEach(function(it){});
                        });
                    }
                } else {
                    this.writeDataHash(key, null, status);
                }
            }
        }
    }

    return this;
  },

    hasBusyRecords: function() {
        return (this.changelog || []).some(function(storeKey) {
            return this.peekStatus(storeKey) & SC.Record.BUSY;
        }, this);
    },
    hasNoBusyRecords: function() {
        return !this.hasBusyRecords()
    },

    /***
     * Dump changes in the store, returning a list
     * @param recordType. Optional recordType to limit the changelog output
     * @returns {Array}
     */
    dumpChanges: function(recordType) {
        return (this.changelog || []).map(function(storeKey) {
            var record = this.materializeRecord(storeKey);
            if (!recordType || record.constructor==recordType)
                return [record.constructor, storeKey, getStatusString(record.get('status'))];
        }, this).compact();
    },
    dumpChainedChanges: function(recordType) {
        return (this.chainedChanges || []).map(function(storeKey) {
            var record = this.materializeRecord(storeKey);
            if (!recordType || record.constructor==recordType)
                return [record.constructor, storeKey, record.get('status')];
        }, this).compact();
    },

  /** @private

    See fixes marked with ABL below
    Called by writeDataHash to update the child record hashes starting from the new (parent) data hash.

    @returns {SC.Store} receiver
  */
  _updateChildRecordHashes: function(storeKey, hash, status) {
    // Update the child record hashes in place.
    if (!SC.none(this.parentRecords) ) {
      // All previously materialized nested objects.
      var materializedNestedObjects = this.parentRecords[storeKey] || {},
        processedPaths = {},
        childHash;

      for (var key in materializedNestedObjects) {
        if (materializedNestedObjects.hasOwnProperty(key)) {

          // If there is a value for the nested object.
          if (hash) {
            var childPath = materializedNestedObjects[key],
                nestedIndex,
                nestedProperty;

            // Note: toMany nested objects have a path indicating their index, ex. 'children.0'
            childPath = childPath.split('.');
            nestedProperty = childPath[0];
            nestedIndex = childPath[1];
            /*jshint eqnull:true*/
            if (nestedIndex != null) {
              // The hash value for this particular object in the array of the record.
              // ex. '{ children: [{ ... }, { ...] }'
              childHash = hash[nestedProperty][nestedIndex];
            } else {
              // The hash value for this object on the record.
              // ex. '{ child: { ... } }'
              childHash = hash[nestedProperty];
            }

            // Update the data hash for the materialized nested record.
            this.writeDataHash(key, childHash, status);

            // Problem: If the materialized nested object is in an array, how do we update only that
            // nested object when its position in the array may have changed?
            // Ex. children: [{ n: 'A' }] => children: [{ n: 'B' }, { n: 'A' }]
            // If { n: 'A' } was materialized, with child path 'children.0', if we updated the hash
            // to be the latest object at index 0, that materialized record would suddenly be backed
            // as { n: 'B' }. The only solution, short of an entire re-architect of nested objects,
            // seems to be to force materialize all items in the array.
            // NOTE: This is a problem because nested objects are masquerading as records. This will
            // be fixed by fixing the concept of nested records to be nested objects.
            // FURTHER NOTE: This also seems to be a usage/expectations problem. Is it not correct
            // for the first materialized child object to update itself?
            if (nestedIndex != null && processedPaths[nestedProperty] == null) {
              // save it so that we don't process it over and over
              processedPaths[nestedProperty] = true;

              // force fetching of all children records by invoking the children_attribute wrapper code
              // and then interating the list in an empty loop
              // Ugly, but there's basically no other way to do it at the moment, other than
              // leaving this broken as it was before
                // ABL fix. This was breaking for nested records
                // Nested records are not in the records array for nested stores?? This is a mess
              var record = this.records[storeKey];
              if (record) {
                var siblings = record.get(nestedProperty);
                for (var i = 0, len = siblings.get('length'); i < len; i++) {
                    if (i !== nestedIndex) { // Don't materialize this same one again.
                        siblings.objectAt(i); // Get the sibling to materialize it.
                    }
                }
              }
                // End ABL fix
            }
          } else {
            this.writeDataHash(key, null, status);
          }
        }
      }
    }
  }

});
