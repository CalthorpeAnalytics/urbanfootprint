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
 *  Base class for simple updating all types of records.
 *  This class allows multiple records to update any attributes.
 *  It does not support nested updates--see record_crud_states for that.
 *
 */
Footprint.RecordUpdatingState = SC.State.extend({

    /***
     * The event to call when the record(s) sucessfully update
     */
    recordsDidUpdateEvent: null,

    /***
     * The event to call when the record(s) failed to update
     */
    recordsDidFailToUpdateEvent: null,

    /***
     * The action to call to handle undoing the record(s) with their undoManager
     */
    undoAction: null,
    /***
     * The action to call to handle updating within a redo operation
     */
    updateAction: null,

    initialSubstate:'readyState',
    readyState:SC.State,

    /***
     * Event called after the records update to register an undo in the context's undoManager, using the context's
     * undoContext as the target for the undo operation
     * @param context
     */
    recordsDidUpdate:function(context) {
        var undoManager = context.get('undoManager');
        var undoContext = context.get('undoContext');
        var redoContext = context.get('redoContext');
        var self = this;
        if (undoManager) {
            if (context.get('isRedoContext')) {
                // There seems to be a bug in the UndoManager that creates an emtpy undo group
                // when you call execute redo. We want this undo group but we need to fill it up
                // This code is just copied from UndoManager.registerGroupedUndoAction by
                // assuming that the current undoStack group is created but empty, which is what
                // hitting redo just did for us. We fill in the properties to complete the group
                var undoStack = undoManager.get('undoStack');
                undoStack.targets.push(null);
                undoStack.contexts.push(undefined);
                undoStack.timeStamp = SC.DateTime.create();
                undoStack.actions.push(function() {
                    // This registers a redo by doing a normal update within the undo. Amazing.
                    undoManager.registerUndoAction(null, function () {
                        // This the redo function
                        self.get('statechart').sendAction(self.get('updateAction'), redoContext);
                    });
                    // Sends an action that can be handled by the parent state if the context recordType matches
                    self.get('statechart').sendAction(self.get('updateAction'), undoContext);
                });
            }
            else {
                undoManager.registerUndoAction(null, function () {
                    // This registers a redo by doing a normal update within the undo. Amazing.
                    undoManager.registerUndoAction(null, function () {
                        // This the redo function
                        self.get('statechart').sendAction(self.get('updateAction'), redoContext);
                    });
                    // Sends an action that can be handled by the parent state if the context recordType matches
                    self.get('statechart').sendAction(self.get('updateAction'), undoContext);
                });
            }
        }
        // Send the didUpdateEvent
        this.get('statechart').sendEvent(this.get('recordsDidUpdateEvent'), this._context);
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

        if (this._records)
            this._records.getPath('firstObject.store').discardChanges();
        // Use the undoContext to reset each records values
        var undoContext = this._context.get('undoContext');
        // Just like when we prepare for the update, except instead update the records
        // according to the undoContext.
        this.updateRecordsToContexts(undoContext.get('recordContexts'));
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

    /***
     * Enters the updating state
     * @param context. An object with the following properties:
     *  recordType: The recordType of all the records in recordContexts
     *  recordContexts: An array of SC.Objects with the following structure:
     *      record: The record instance
     *      attribute1...attributeN: any number of attributes and their target values.
     *       -- Each record is thus paired with attributes and values with which to update the record.
     *          This structure is naturally used for updating, undoing, and redoing.
     *  undoManager: The SC.UndoManager used to manage this record, recordType, logical group of records, etc.
     *      The granularity of the undoManager depends on what the user reasonably expects undo/redo to do in a
     *      certain UI context.
     *  undoContext: Identical in structure to the entire context param, minus an undoContext.
     *  Used to undo the update that is configured. No undoContext is needed because the undoManager already knows
     *  how to undo to the previous context by the entire context.
     */
    enterState: function(context) {
        this._context = context;

        var recordContexts = context.get('recordContexts');
        this._records = recordContexts.map(function(recordContext) {
            return recordContext.get('record');
        });
        this._recordsQueue = SC.Set.create(this._records);
        // Prevent a race condition below
        this._finished = NO;

        // Perform our actual record updates
        this._records.forEach(function(record) {
            // Add observer on each record
            record.addObserver('status', this, 'recordStatusDidChange');
        }, this);
        // Applies the attributes in the recordContexts to the records
        this.updateRecordsToContexts(recordContexts);

        // Commit the records to the datasource
        this._store = this._records.getPath('firstObject.store');
        this._store.commitRecords(
            this._records.mapProperty('storeKey').map(function(storeKey) {
                return this._store.recordTypeFor(storeKey);
            }, this),
            this._records.mapProperty('id'),
            this._records.mapProperty('storeKey')
        );
        // Manually invoke observer in case everything is already done
        this.recordStatusDidChange();
    },

    /***
     * Takes the record in each recordContext and updates it to the key/value pairs in the context
     * @param recordContexts
     */
    updateRecordsToContexts: function(recordContexts) {
        return recordContexts.forEach(function(recordContext) {
            // Set attributes of record based on the key/value pairs stored with it
            // If the records were already modified then the context won't contain any attributes
            var record = recordContext.get('record');
            var updateHash = filterKeys(recordContext, record.constructor.allRecordAttributeProperties(), 'object');
            record.setIfChanged(updateHash);
            // SC doesn't call recordDidChange when you go from A to B and then back to B on a set attribute
            // Seems to be a bug. Call manually instead
            record.recordDidChange();
        }, this);
    },

    recordStatusDidChange: function(sender) {
        this.invokeOnce(this._recordStatusDidChange);
    },
    _recordStatusDidChange: function() {
        if (!this._recordsQueue)
            // Late binding
            return;

        var recordsDequeue = [];
        if ($.any(this._recordsQueue, function(record) {
            return record && record.get('status') === SC.Record.ERROR;
        })) {
            this._finished = YES;
            SC.AlertPane.warn({
                message: "Records failed to update. Report this error if it recurs."
            });
            this.get('statechart').sendEvent(this.get('recordsDidFailToUpdateEvent'), this._context);
            return;
        }

        this._recordsQueue.forEach(function(record) {
            if (record && record.get('status') & SC.Record.READY) { // === SC.Record.READY_CLEAN) { until we fix the LayerSelecdtion problem
                recordsDequeue.pushObject(record);
            }
        }, this);
        recordsDequeue.forEach(function(record) {
            record.removeObserver('status', this, 'recordStatusDidChange');
            this._recordsQueue.removeObject(record);
        }, this);

        if (this._recordsQueue.length == 0) {
            if (this._finished) // Avoid a race condition that results in two calls
                return;
            this._finished = YES;

            // All good, send the updated records to the main store
            this._store.commitChanges(YES);
            // Register an undo (if this isn't an undo) and send the recordsDidUpdateEvent
            this.recordsDidUpdate(this._context);
        }
    },

    exitState: function() {
        // Cancel any pending update in case we are about to reenter this state;
        if (this._recordsQueue.length > 0)
            this.cancelUpdate();

        this._context = null;
        // Remove observers
        this._records.forEach(function(record) {
            // Remove orphaned observers
            record.removeObserver('status', this, 'recordStatusDidChange');
        }, this);

        this._recordsQueue = null;
        this._finished = null;
    }
});
