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


Footprint.SavingRecordsState = SC.State.extend({
    _active:YES,
    doCancel: function() {
        this.gotoState('noModalState');
    },

    initialSubstate: 'savingBeforeRecordsState',

    //Don't send event
    startingCrudState: function(context) {
    },
    /***
     *
     * @param context - contains the nestedStore to be used for the buffered save and the content, which is an
     * array of one or more records to save
     */
    enterState:function(context) {
        // If we enter this as a dynamic substate (for recursion), this_context will already be set, so we ignore the passed in parent context
        this._context = this._context || context;

        this.startingCrudState(this._context);

        if (!this._context.get('store'))
            throw Error('No nested store');
    },

    exitState: function() {
        this._context = null;
        this._active = NO;
    },

    /***
     * Saves all records of a properties that need to be saved before the main records are saved.
     * This is important in the create case where a dependent record needs to be created first.
     * For instance if a record type BuiltForm has a property Medium, the Medium should be created
     * before the BuiltForm so that the BuiltForm can reference it when it is created.
     *
     * All child records are saved concurrently. Thus if there are m main records that have p properties that
     * each have an array or c (child) records, then m*p*c records will be saved concurrently.
     */
    savingBeforeRecordsState:Footprint.SavingChildRecordsState.extend({

        enterState:function() {
            if (!this.getPath('parentState._active'))
                return;
            sc_super();
        },
        successEvent: 'didFinishBeforeRecords',
        failEvent: 'saveBeforeRecordsDidFail',
        getProperties: function(record) {
            return record._saveBeforeProperties();
        },
        didFinishBeforeRecords: function(context) {
            if (this.getPath('_context.content') === context.get('content')) {
                SC.Logger.debug('didFinishBeforeRecords handled %@'.fmt(context.getPath('content.firstObject.constructor')));
                this.gotoState('%@.savingMainRecordState'.fmt(this.getPath('parentState.fullPath')), context);
                return YES;
            }
            SC.Logger.debug('Not handled: savingBeforeRecordsState');
            return NO;
        }
    }),

    /***
     * Saves the main record(s). Sends the event saveRecordsDidFail if something goes wrong.
     */
    savingMainRecordState:SC.State.extend({

        didFinishMainRecords: function(context) {

            if (context.get('content') === this._context.get('content')) {
                SC.Logger.debug('Handled %@'.fmt(context.getPath('content.firstObject.constructor')));
                this.gotoState('%@.savingAfterRecordsState'.fmt(this.getPath('parentState.fullPath')), context);
                return YES;
            }
            SC.Logger.debug('Not handled: didFinishMainRecords');
            return NO;
        },

        /***
         * Handles errors in persisting records by calling saveRecordsDidFail.
         * This is in turn handled by savingBeforeRecordState, savingAfterRecordState if these records where
         * part of a child record save operation.
         * @param context
         * @returns {*}
         */
        mainRecordsDidError:function(context) {
            this.get('statechart').sendEvent('saveRecordsDidFail', context);
        },

        softCancelUpdate: function() {
            // Remove observers
            this._recordsQueue.forEach(function(record) {
                record.removeObserver('status', this, 'recordStatusDidChange');
            }, this);

            var nestedStore = this._context.get('store');
            nestedStore.changelog.forEach(function(storeKey) {
                var id = nestedStore.materializeRecord(storeKey).get('id');
                if (id >= 0)
                    nestedStore.writeStatus(storeKey, SC.Record.READY_DIRTY);
                else
                    nestedStore.writeStatus(storeKey, SC.Record.READY_NEW);
            });
            return NO;
        },

        /***
         * Cancel the in-process update
         * @param context
         */
        cancelUpdate: function() {
            // Remove observers
            this._recordsQueue.forEach(function(record) {
                record.removeObserver('status', this, 'recordStatusDidChange');
            }, this);

            var nestedStore = this.getPath('parentState._context.store');
            nestedStore.discardChanges();
            return NO;
        },

        /***
         * React to record save failures by canceling the entire update to avoid bad state problems
         * @param context
         * @returns {NO|*}
         */
        recordsDidFailToUpdate: function(context) {
            this.cancelUpdate();
            return NO;
        },

        enterState: function(context) {
            this._context = this.getPath('parentState._context');
            // commitRecords from changelog of nestedStore
            var nestedStore = this.getPath('parentState._context.store');
            var records = this.getPath('parentState._context.content');

            var templateRecord = records.get('firstObject');
            // Get references to unsaved records that should be removed from the instance for saving.
            // They will be added back on after and saved themselves.
            var deferredProperties = templateRecord._saveAfterProperties();
            if (deferredProperties.get('length') > 0) {
                records.forEach(function(record) {
                    // If any save after properties are new, tell the record to defer presentation
                    if ((typeof(record.get('no_post_save_publishing')) != 'undefined') &&
                        deferredProperties.find(function(property) {
                            return SC.Record.READY_NEW == record.get(property).get('status');
                        }, this)) {

                        record.set('no_post_save_publishing', YES);
                    }

                }, this);
            }
            // To prevent trying to save newly cloned records before the main record,
            // create a lookup of each record storeKey to a dict with a key and value for each cloneProperty
            // The key is the property and the value is the cloned property value
            // In the process the record property is temporary nulled out
            // These cloned properties will be reassigned to the record after for post main record saving
            this._deferredPropertyLookup = $.mapToDictionary(
                records,
                function(record) {
                    return [
                        // key by store key
                        record.get('storeKey'),
                        // value by a dict keyed by property and valued by instance
                        $.mapToDictionary(deferredProperties, function(propertyPath) {
                            var value = record.getPath(propertyPath);
                            if (value && value.isEnumerable) {
                                // If enumerable, extract the new items so we don't maintain the ManyArray which will be cleared
                                // during the save/reload
                                value = value.toArray().filter(function(rec) {
                                    return rec.get('id') < 0;
                                });
                                record.getPath(propertyPath).removeObjects(value);
                                return value.get('length') > 0 ? [propertyPath, value] : null;
                            }
                            else {
                                if (record.get('id') < 0)
                                    record.setPath(propertyPath, null);
                            }
                            return value ? [propertyPath, value] : null;
                        })
                    ];
                }
            );

            records.forEach(function(record) {
                record.addObserver('status', this, 'recordStatusDidChange');
            }, this);

            this._recordsQueue = SC.Set.create(records);
            // Prevent a race condition below
            this._finished = NO;
            this.recordStatusDidChange();

            nestedStore.commitRecords(
                records.map(function(record) {
                    return nestedStore.recordTypeFor(record.get('storeKey'));
                }, this),
                null,
                records.mapProperty('storeKey')
            );
        },
        recordStatusDidChange: function() {
            this.invokeOnce(this._recordStatusDidChange);
        },
        _recordStatusDidChange: function() {
            if (this._finished)
                return;

            if ($.any(this._recordsQueue, function (record) {
                    return record && record.get('status') === SC.Record.ERROR;
                })) {
                // Give up on any more processing of records in this scope.
                this._finished = YES;
                this.get('statechart').sendEvent('mainRecordsDidError', this.getPath('parentState._context'));
            }

            var recordsDequeue = this._recordsQueue.filter(function (record) {
                // Detect coding errors where instances are dirtied by observers right away
                if ((record.get('status') & SC.Record.READY) && record.get('status') != SC.Record.READY_CLEAN)
                    logWarning('Saved recordType %@ of id %@ was dirtied by an observer upon reload. Track this down and fix'.fmt(record.constructor, record.get('id')));
                return record && record.get('status') & SC.Record.READY;
            }, this);
            recordsDequeue.forEach(function (record) {
                record.removeObserver('status', this, 'recordStatusDidChange');
                this._recordsQueue.removeObject(record);
            }, this);

            if (this._recordsQueue.length == 0) {

                // If we have deferred properties we need to merge what came back from the server (if anything) with
                // the deferred property values, and attach them to the main record.
                // For new records it's possible that we deferred the property but that the server created it's own version.
                // Example: We defer feature_behavior from DbEntity saves, but the server creates a
                // default feature_behavior. In this case we have to merge the default that came back from the server
                // with what the user might have configured, such as the behavior property of the FeatureBehavior.
                // In the case that the server has created a new property, we have to give it time to load, so we
                // start with loading all properties that are deferred, followed by a merge, followed by setting
                // the merged property. When that is all done we save each deferred property
                if (Object.keys(this._deferredPropertyLookup).length == 0) {
                    // No deferred properties, skip processing and send finished event
                    this.get('statechart').sendEvent('didFinishMainRecords', this._context)
                }
                else {
                    this.gotoState('loadDeferredPropertiesState',
                        toArrayController({
                            content: this._context.get('content'),
                            store: this._context.get('store'),
                            deferredPropertyLookup: this._deferredPropertyLookup
                        })
                    );
                }
                // Mark the state as finished to avoid race conditions
                this._finished = YES;
            }
        },

        /***
         * If we have deferred properties that we removed prior to saving because those property values were
         * new records, then we need to load whatever the server might have produced, if anything, and
         * merge them with whatever might have been created locally. Then we reattach the merged properties
         * the main record.
         */
        loadDeferredPropertiesState: Footprint.LoadingState.extend({

            didLoadEvent: 'deferredPropertiesDidLoad',
            // Check the status of each deferred record loading from the server
            checkRecordStatuses: YES,

            recordArray: function() {
                var deferredRecords = [];
                var nestedStore = this.getPath('_context.store');
                // Restore the deferred properties for each record
                $.each(this._context.get('deferredPropertyLookup'), function (storeKey, propertyLookup) {
                    // Fetch the main record from the nested store.
                    var record = nestedStore.materializeRecord(storeKey);
                    // The record will not exist if it was removed from the store by a delete operation
                    if (record) {
                        // For each deferred property
                        $.each(propertyLookup, function (key, value) {
                            // Handle property paths. TODO why would we ever have chained properties?
                            var segments = key.split('.');
                            var propertyPath = segments.slice(0, -1).join('.');
                            var property = segments.slice(-1)[0];
                            var resolvedRecord = segments.get('length') > 1 ? record.getPath(propertyPath) : record;

                            // It's possible that we deferred the property but that the server created it's own version.
                            // Example. We defer feature_behavior from DbEntity saves, but the serer creates a
                            // default feature_behavior.
                            // In this case we need to wait for the associated record or records to load, then
                            // merge it/them with the new ones we created on the client and deferred.
                            // Important: Because retrieveRecords always uses the main store (it probably shouldn't)
                            // We have to observe the main store version for status changes.
                            // Once the records are clean we'll reset the nested store version to reflect them below
                            deferredRecords.pushObjects(arrayIfSingular(resolvedRecord.get(property)).map(function(propertyRecord) {
                                return nestedStore.get('parentStore').materializeRecord(propertyRecord.get('storeKey'));
                            }));
                        });
                    }
                });
                return deferredRecords;
            },

            deferredPropertiesDidLoad: function() {
                var nestedStore = this.getPath('_context.store');
                // If any records needed to load from the server, they are now loaded
                // Iterate again and this time merge values from the server with what was created on the client
                $.each(this._context.get('deferredPropertyLookup'), function (storeKey, propertyLookup) {
                    // Fetch the main record from the nested store.
                    var record = nestedStore.materializeRecord(storeKey);

                    // The record will not exist if it was removed from the store by a delete operation
                    if (record) {
                        // For each deferred property
                        $.each(propertyLookup, function (key, value) {
                            // Handle property paths. TODO why would we ever have chained properties?
                            var segments = key.split('.');
                            var propertyPath = segments.slice(0, -1).join('.');
                            var property = segments.slice(-1)[0];
                            var mainRecord = segments.get('length') > 1 ? record.getPath(propertyPath) : record;

                            // Use the normal inverse property or our special softInverse if we couldn't set the inverse property on the field, due to polymorphism problems
                            // Since we detached the property values, they don't pick up the new id of the saved
                            // records. So use the inverse property to assign the reference back to the reference
                            // if present.
                            var inverseProperty = mainRecord[property].inverse || mainRecord[property].softInverse;
                            if (value.isEnumerable) {
                                // TODO maintain order
                                // TODO handle default items created on the server
                                // The values should still be removed, but just in case
                                mainRecord.get(property).removeObjects(value);
                                value.forEach(function (item) {
                                    if (inverseProperty)
                                        item.set(inverseProperty, mainRecord);
                                });
                                mainRecord.get(property).pushObjects(value);
                            }
                            else if (inverseProperty) {
                                // If the property record is BUSY_LOADING we need to reset it, since the main store
                                // version will have fetched it from the server. This only happens for new records.
                                // We also need to merge it with whatever values the user might have configured
                                var propertyRecord = mainRecord.get(property);
                                if (propertyRecord && propertyRecord.get('status') === SC.Record.BUSY_LOADING) {
                                    // Get the version the user might have edited, minus the inverseProperty which will be out-of-date
                                    var localVersion = removeKeys(nestedStore.readDataHash(value.get('storeKey')), [inverseProperty]);
                                    // Reset the store key to get the value that was loaded via retrieveRecords on the main store
                                    nestedStore.resetSome([propertyRecord.get('storeKey')]);
                                    // Get the dataHash that came back from the server. TODO for some reason we can't use the
                                    // nestedStore even though resetSome should have synced it
                                    var serverVersion = nestedStore.get('parentStore').readDataHash(propertyRecord.get('storeKey'));
                                    // Merge the serverVersion with the localVersion, favoring the local
                                    var finalVersion = merge(serverVersion, localVersion);
                                    // Write the results to the nested store
                                    nestedStore.writeDataHash(propertyRecord.get('storeKey'), finalVersion);
                                    // Set the inverse relationship back to the main record
                                    propertyRecord.set(inverseProperty, mainRecord);
                                }
                                else {
                                    // Simply restore the value
                                    value.set(inverseProperty, mainRecord);
                                    mainRecord.setPath(property, value);
                                }
                            }
                        });
                    }
                });
                // Announce that the main records finished.
                // At this point the state is no longer active (I forget why), so we
                // send an event which the active version of the state processes.
                this.get('statechart').sendEvent('didFinishMainRecords', this._context);
            }
        })
    }),

    savingAfterRecordsState:Footprint.SavingChildRecordsState.extend({
        successEvent: 'didFinishRecords',
        failEvent: 'saveAfterRecordsDidFail',
        getProperties: function(record) {
            return record._saveAfterProperties();
        }
    })
});
