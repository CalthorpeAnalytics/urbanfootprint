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

sc_require('states/record_updating_state');

Footprint.RecordsAreReadyState = SC.State.extend({

    /***
     * Optional. The name of the event to send when this state is entered.
     * No event is sent if this is null
     */
    recordsAreReadyEvent: null,

    /***
     * Optional, the controller with read-only content.
     * No code in this class expects this controller, but it is useful
     * for subclasses and might come to be expected in this class as well.
     */
    recordsController: null,

    /***
     * Optional, the controller used to edit records for this state.
     * This controller is normally created by assigning a nestedStore to it.
     * No code in this class expects the recordsEditController, but it is useful
     * for subclasses and might come to be expected in this class as well.
     */
    recordsEditController: null,

    /***
     * Required. The event to invoke when the record(s) successfully update
     */
    recordsDidUpdateEvent: null,

    /***
     * Required. The event to invoke when the records(s) fail to update
     */
    recordsDidFailToUpdateEvent: null,

    /***
     * Required. The action to invoke upon undo to distinguish this state from others
     */
    undoAction: null,
    /***
     * Required. The attributes of the records that should be updated or undone upon invoking undo
     * TODO This could default to all attributes for simple record types
     */
    updateAttributes: null,

    /**
     * Optional. The recordContext when updating one or more records to the same value
     * This is an SC.Object with an update and revert property. The value of each is the
     * an SC.Object that has the properties of the records that need to be updated/reverted.
     *
     * This is used as an alternative to updating records immediate when editing them, and
     * to apply updates based on other view controls that are global to the records being
     * updated (e.g. for features the dev percent)
    */
    recordContext: null,

    /***
    * The undoManager for the instance(s) being updated. Use the Container and Property
    * or the undo
    */
    undoManagerProperty: null,
    /***
     * Use the controller with undoManagerProperty for collection undo (like for Features)
     */
    undoManagerController: null,
    /***
     * Get the initialized undoManager for the current item or collection
     * @returns {*}
     */
    undoManager: function() {
        var property = this.get('undoManagerProperty');
        var controller = this.get('undoManagerController');
        if (controller && property) {
            return controller.getPath(property);
        }
        else if (property) {
            // TODO stupidly assuming single _content for now
            return this._content.getPath(property);
        }
    }.property(),

    /***
     *
     * Initialize the undoManager for Scenario collection and individuals
     */
    initializeUndoManager: function() {
        var property = this.get('undoManagerProperty');
        var controller = this.get('undoManagerController');

        // For collection-scoped undo use the (e.g. a controller) and the undoManagerProperty (e.g. 'undoManager')
        if (controller && property) {
            if (!controller.getPath(property)) {
                controller.setPath(this.get('undoManagerProperty'), SC.UndoManager.create());
                //controller.get('content')[this.get('undoManagerProperty')] = SC.UndoManager.create();
            }
        }
        // For item scoped undo iterate through the items
        else if (property) {
            arrayOrItemToArray(this._content).forEach(function(content) {
                if (!content.getPath(property)) {
                    content.setPath(property, SC.UndoManager.create());
                    //content[property] = SC.UndoManager.create();
                }
            });
        }
    },

    /***
     * Returns the context to update the records(s). This is a list of SC.ObjectController that points
     * to the record along with a key/values of attributes and their target update value. The context
     * is the incoming context of the state, which can be used to create the updateContext
    */
    updateContext: function(context) {
        // recordContext is ONLY used if a certain DbEntity has default values to apply when editing
        // Otherwise it is just an empty object that does nothing
        var recordContext = this.getPath('recordContext.update') || SC.ObjectController.create();
        return this.createModifyContext(recordContext, context);
    },

    /***
     * The attributes to undo during and undo action. This determines what current attributes to store when
     * building and undoContext
     */
    undoAttributes: [],

    /***
     * The attribute to cancel any update in progress, used when new updates come in during saving
     */
    cancelAction: null,

    /***
     * Called when undoing so that we don't register a new undo
     * @param context
     */
    undoRecords: function(context) {
        this.gotoState('%@.undoingState'.fmt(this.get('fullPath')), context);
    },

    /***
     * Method to submit the record(s) with updated values.
     * We use this method for normal updates and redos. WE use undoRecords for undos
     */
    updateRecords: function(context) {
        this.gotoState('%@.updatingState'.fmt(this.get('fullPath')), this.updateContext(context));
    },

    doRecordUndo: function(context) {
        this.get('undoManager').undo();
    },
    doRecordRedo: function(context) {
        this.get('undoManager').redo();
    },

    /***
     * If a record update fails this handles the event.
     * @param context. This could be used to report what records failed
     */
    updateDidFail: function(context) {
        // Simply return to the start of this state
        this.gotoState(this.get('fullPath'), this._context);
    },

    /***
     * Adds an existing or new record to an associated list
     * TODO this currently assumes nested records only.
     * @param context:
     *  list: The list to which to add the item. It must be a ChildArray or similar
     *  clearListFirst: Default NO, set to YES to clear the list prior to adding the item to the list
     *  content: The item to add. Either an existing record or an new unsaved record
     *  recordType: The required record type of the item. If the content is not
     *  a of the recordType the function returns NO
     *  comparisonKey: Optional property of the item to compare to the list items. By default
     *  the list just uses contains to see if the item is in it.
     * @returns {boolean} YES if the add was made or object was already in the list
     * NO if the record didn't match
     */
    addOrSelectAssociatedItem: function(context) {
        var itemToAdd = context.getPath('content');
        if (!itemToAdd)
            return YES;
        if (!context.getPath('content').kindOf(context.get('recordType')))
            return NO;
        var list = context.get('list');
        // Item is already part of the list. Return YES to indicate handled
        // TODO there is a bug somewhere that causes a double click to add a tag twice
        // For some reason in that case the tags aren't treated as identical instances,
        // so compare the string value
        if (context.get('comparisonKey') ?
            list.mapProperty(
                context.get('comparisonKey')).contains(itemToAdd.get(context.get('comparisonKey'))) :
            list.contains(itemToAdd))
            return YES;

        // If desired clear the list before adding the item
        if (context.get('clearListFirst'))
            list.removeObjects(list);
        // Existing item
        if (itemToAdd.get('id'))
            list.pushObject(itemToAdd);
        // Nested record
        else if (list.instanceOf(SC.ChildArray)) {
            // Create a nested record
            list.createNestedRecord(
                context.get('recordType'),
                itemToAdd.get('attributes')
            );
            // Now that we have a nested record, remove the temporary record from the store
            list.get('store').unloadRecord(itemToAdd.constructor, itemToAdd.get('id'), itemToAdd.get('storeKey'));
        }
        // Non-nested record
        else if (list.instanceOf(SC.ManyArray)) {
            list.pushObject(itemToAdd);
        }
        else {
            throw 'Don\'t know how to handle list of type %@'.fmt(list.constructor.toString());
        }
        return YES;
    },

    /***
     * Add a toMany item to the "parent" object's toMany array
     * @param context. Contains:
     *  record: The record to add the toMany array
     *  parentRecord: The owner of the toMany array
     *  toManyAttribute: The attribute of the parentRecord to hold the record
     */
    doUpdateToManyAssociation: function(context) {
        var parentRecord = context.get('parentRecord');
        var record = context.get('record');
        var toManyAttribute = context.get('toManyAttribute');
        var manyArray = parentRecord.get(toManyAttribute);
        if (record.get('status') & SC.Record.DESTROYED || record.get('deleted')) {
            /// If the record was destroyed due to error or abandonment, remove it
            manyArray.removeObject(record);
        }
        else {
            if (!manyArray.contains(record)) {
                manyArray.pushObject(record);
            }
        }
    },

    // Queue of postSave handlers that queue up before CRUD finishes
    _eventHandlerQueue: [],
    // Track when the CRUD saving starts and finishes. We'll queue postSave events
    // until the CRUD is finished saving
    _crudFinished:  YES,
    // The record type to match from context passed to crudDidStart and crudDidFinish
    // If not overridden in the subclass this will never match and crudDidStart, crudDidFinish
    // will not be used
    baseRecordType: null,
    // Instructs postSave methods to use the baseRecordType to find the record in the
    // store. If NO, it will used the subclass recordType passed in as context.class_name
    // We use NO for BuiltForm subclasses and other records that are saved as their subclass
    // whereas something like Scenario is treated Scenario, so we keep this value NO
    findByBaseRecordType: YES,
    // For more server-side dynamic subclasses like, Features subclasses, set this to true
    // to find by the subclassRecordType instead of the baseRecordType
    findBySubclassRecordType: NO,
    subclassRecordType: null,

    /**
     * The default success message. Override to customize
     * If customized to return null, the alert will be supressed
     * @param context. The postSave context plus record and recordType
     * @returns {*}
     */
    successMessage: function(context) {
        // Resolve the recordType from the recordType or class_name
        var recordType = context.get('recordType') ||
            SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        return 'Successfully saved %@ records'.fmt(recordType.friendlyName() || recordType.toString().split('.')[1].titleize());
    },
    /**
     * The default failure message. Override to customize
     * @param context. The postSave context plus record and recordType
     * @returns {*}
     */
    failureMessage: function(context) {
        var recordType = context.get('recordType');
        return  'Saving %@ Failed'.fmt(recordType.friendlyName() || recordType.toString().split('.')[1].titleize());
    },

    /***
     * Simply returns the content.firstObject. Override for custom behavior. For instance,
     * Layers resove to their DbEntity
     * @param context
     * @returns {*}
     * @private
     */
    _resolveContextRecord: function(context) {
        return context.getPath('content.firstObject');
    },
    crudDidStart: function(context) {
        if ((this._resolveContextRecord(context) || SC.Object).kindOf(this.get('baseRecordType'))) {
            this._eventHandlerQueue.clear();
            this._crudFinished = NO;
            this._crudFailed = NO;
            // Reset any records that implement the no_post_save_publishing flag
            context.get('content').forEach(function(record) {
                if (typeof(record.get('no_post_save_publishing')) != 'undefined')
                    record.setIfChanged('no_post_save_publishing', NO);
            });
            return YES;
        }
        return NO;
    },
    crudDidFinish: function(context) {
        if ((this._resolveContextRecord(context) || SC.Object).kindOf(this.get('baseRecordType'))) {
            this._crudFinished = YES;
            // Pop out handlers that queued up and run them
            while (this._eventHandlerQueue.length > 0)
                this._eventHandlerQueue.popObject().apply(this);
            return YES;
        }
        return NO;
    },

    _resolveRecords: function(context, allowNull) {
        // Either find the record by the baseRecordType, the subclassRecordType, or by the class_name in the context
        // baseRecordType is the default. subclassRecordType is used for classes like Feature, where we always
        // have subclass instances. class_name is used if neither of those are appropriate, like BuiltForms that
        // have well defined subclasses
        var records = context.get('ids').map(function(id) {
            return F.store.find(
                this.get('findByBaseRecordType') ?
                    this.get('baseRecordType') :
                    this.get('findBySubclassRecordType') ?
                        this.get('subclassRecordType') :
                        SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name'))),
                id);
        }, this);
        if (!records && !allowNull)
            throw Error('Could not find record(s) of class_name %@ and id %@ in the main store'.fmt(context.get('class_name'), context.get('ids').join(',')));
        return records;
    },

    /***
     * Responds to the start event of a postSave publisher. If the incoming class_name matches
     * this.baseRecordType, the handler will run or be queued up if _crudFinished=NO
     * @param context
     * @returns {*}
     */
    postSavePublisherStarted: function(context) {
        // Gate keep by recordType
        var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        if (!recordType.kindOf(this.get('baseRecordType'))) {
            SC.Logger.debug('Not handled: postSavePublisherStarted');
            return NO;
        }
        SC.Logger.debug('Handled');
        if (this._crudFailed)
            // Quit if we already failed
            return NO;

        var eventHandler = function() {
            var records = this._resolveRecords(context);

            this.resetProgress(records, 0);
            SC.Logger.debug('Starting progress for recordType %@ with id(s) %@'.fmt(recordType, records.mapProperty('id').join(',')));
        };
        if (this._crudFinished)
            // Run the handler immediately if CRUD is already finished
            eventHandler.apply(this);
        else
            // Queue it up
            this._eventHandlerQueue.unshiftObject(eventHandler);

        return YES;
    },

    // Reset the progress of all records to 0 or null
    // use 0 for value if starting a new run
    // use null for reset after failure
    resetProgress: function(records, value) {
        records.forEach(function(record) {
            record.set('progress', value);
        });
    },

    /***
     * Listens for postSavePublisherProportionCompleted updates from Socket IO
     * Each update sends a 'proportion' value. When this proportion hits 100% the save is
     * completed. We use proportion both to show status and because concurrent publishers
     * on the server make it impossible to know otherwise when everything is complete.
     * @param context
     * @returns {window.NO|*}
     */
    postSavePublisherProportionCompleted: function(context) {
        // Gate keep by recordType
        var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        if (!recordType.kindOf(this.get('baseRecordType'))) {
            SC.Logger.debug('Not handled: postSavePublisherProportionCompleted');
            return NO;
        }
        SC.Logger.debug('Handled portion %@ with proportion %@'.fmt(
            context.get('progress_description'), context.get('proportion')));
        if (this._crudFailed)
            // Quit if we already failed
            return YES;

        var eventHandler = function() {
            var records = this._resolveRecords(context);

            // Update the progress.
            records.forEach(function(record) {
                record.set('progress', Math.min(1, record.get('progress')+context.get('proportion')));
                SC.Logger.debug('Updating progress for recordType %@ with id %@, portion %@ with total progress %@'.fmt(
                    recordType, record.get('id'), context.get('progress_description'), record.get('progress')));
            });

            var fullContext = SC.ObjectController.create(context, {records:records, recordType:recordType});
            // Progress is complete
            if (records[0].get('progress') == 1) {
                var successMessage = this.successMessage(fullContext);
                if (successMessage)
                    SC.AlertPane.info({
                        message: successMessage
                    });
                this.postSavePublishingFinished(fullContext);
            }
        };
        if (this._crudFinished)
            // Run the handler immediately if CRUD is already finished
            eventHandler.apply(this);
        else
            // Queue it up
            this._eventHandlerQueue.unshiftObject(eventHandler);
        return YES;
    },


    /***
     * Handles postSave presentation failure events
     * @param context
     * @returns {window.NO|*}
     */
    postSavePublisherFailed: function(context) {
        // Gate keep by recordType
        var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        if (!recordType.kindOf(this.get('baseRecordType')))
            return NO;
        var records = this._resolveRecords(context, YES);
        this.resetProgress(records, null);

        var fullContext = SC.ObjectController.create(context, {records:records, recordType:recordType});
        SC.AlertPane.warn({
            message: this.failureMessage(fullContext),
            description: 'There was an error processing "%@". Please try again, and if this continues, please report to your system administrator.'.loc(
                context.get(context.get('keys') ? 'keys' : 'ids').join(',') || 'unknown'
            )
        });
        // Let subclasses handle. We pass the record if it is available
        this.get('statechart').sendEvent('postSavePublishingDidFail', fullContext);
        this._postSavePublisherFailed(context);
        return YES;
    },

    postSavePublishingDidFail: function(context) {
        var recordType = SC.objectForPropertyPath('Footprint.%@'.fmt(context.get('class_name')));
        if (!recordType.kindOf(this.get('baseRecordType'))) {
            return NO;
        }
    },

    _postSavePublisherFailed: function(context) {
        this._crudFailed = YES;
        this._crudFinished = YES;
        // If the crud state is still savingRecords, tell it to give up
        this.get('statechart').sendEvent('saveRecordsDidFail');
    },

    commitConflictingNestedStores: function(records) {
        // Other nestedStore locks cause SC to crash. They shouldn't but I don't know to prevent it right now
        Footprint.store.get('nestedStores').forEach(function(nestedStore) {
            if (nestedStore.locks) {
                var locks = (records.map(function(record) {
                    var lockStatus = nestedStore.locks[record.get('storeKey')];
                    return lockStatus ? [record.get('storeKey'), getStatusString(nestedStore.peekStatus(lockStatus))] : null;
                }).compact());
                if (locks.get('length') > 0) {
                    logWarning(
                        'Refreshing locked records!. A nested store has locks of the following storeKeys with the given statuses: %@'.fmt(
                        locks.map(function(keyAndStatus) {
                            return [keyAndStatus[0], getStatusString(keyAndStatus[1])].join(':');
                        }).join(', ')
                    ));
                    // Commit the changes to clear the locks
                    // TODO this is not a permanent solution
                    nestedStore.commitChanges();
                }
            }
        });
    },

    /***
     * Override to do something useful after postSavePublishing completes
     * context contains the context from postSaveCompleted plus the record that was resolved
     */
    postSavePublishingFinished: function(context) {

    },
    /***
     * Override to so something useful after a postSavePublisherFailed event
     * @param context
     */
    postSavePublishingFailed: function(context) {

    },

    initialSubstate: 'readyState',
    readyState: SC.State,

    /***
     * Typically overridden by the subclass which sets the _content and _context properties
     * @param context
     */
    enterState: function(context) {
        // Announce to parent states that records are ready for this state
        if (this.get('recordsAreReadyEvent'))
            this.get('statechart').sendEvent(this.get('recordsAreReadyEvent'));
        // Create the undoManager if it doesn't yet exist
        if (!this.get('undoManager'))
            this.initializeUndoManager();
    },

    exitState: function() {
        this._content = null;
        this._context = null;
    },

    /***
     * For simpler record type saves that don't need CrudState.SavingRecords state.
     * TODO The two ways of saving should be coallesced
     * Updates the records.
     */
    updatingState: Footprint.RecordUpdatingState.extend({
        undoActionBinding: SC.Binding.oneWay('.parentState.undoAction'),
        updateActionBinding: SC.Binding.oneWay('.parentState.updateAction'),
        recordsDidUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidUpdateEvent'),
        recordsDidFailToUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidFailToUpdateEvent')
    }),

    /***
    * For simpler record type saves that don't need CrudState.SavingRecords state.
    * TODO The two ways of saving should be coallesced
    * Undo has a different context but is otherwise the same as update but it doesn't register an undo
    */
    undoingState:Footprint.RecordUpdatingState.extend({
        undoActionBinding: SC.Binding.oneWay('.parentState.undoAction'),
        updateActionBinding: SC.Binding.oneWay('.parentState.updateAction'),
        recordsDidUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidUpdateEvent'),
        recordsDidFailToUpdateEventBinding: SC.Binding.oneWay('.parentState.recordsDidFailToUpdateEvent'),
        recordsDidUpdate:function() {
            // Skip sc_super() so we don't register an undo
        }
    }),

    /***
     * Creates the undoContext by storing the non-edited values (the main store version) of the records
     * The attributes that are recorded for undo are those in the record's attributes._updatedAttributes.
     */
    undoContext: function(otherContext) {
        // If we have an explicit updateContext (only painting features), we use the updateContext keys as our
        // undo context. Otherwise we look at what attributes have been edited below
        var updateContextKeys = this.getPath('recordContext.keys');
        return SC.ObjectController.create({
            // The undoManager needs to be specified for setting redo (I think)
            undoManager: this.get('undoManager'),
            // The Feature recordType
            recordType: this._context.get('recordType'),
            // Tell the statechart when we are undoing
            isUndoContext: YES,
            // An array of each record to be undone along with the values to undo to (context)
            // The resulting objects are {record:record, attributeToUpdate:value, attributeToUpdate:value, ...}
            recordContexts: arrayOrItemToArray(this._content).map(function(editedRecord) {
                var uneditedRecord = editedRecord.get('mainStoreVersion');
                return SC.ObjectController.create(
                    {record:editedRecord},
                    // extract the primitive attributes from the record to be target attribute values for undoing
                    $.mapToDictionary(updateContextKeys || editedRecord.getPath('attributes._updatedAttributes'), function(attr) {
                        return [attr, uneditedRecord.get(attr)];
                    })
                );
            }, this)
        },
        otherContext || {});
    },
    /***
     * This creates a context that restores values to the currently edited values, since we create the
     * redoContext when we create the undoContext
     * @param otherContext
     * @param the undoContext for the redoContext. We could generate this by comparing redo values
     * to the current values, but we know the current values have to match this undoContext
     * @returns {*}
     */
    redoContext: function(otherContext, undoContext) {
        // If we have an explicit updateContext (only painting features), we use this updateContext as our
        // redo context. Painting features apply the same values to every feature (e.g. BuiltForm), so
        // this context is used for all features. Otherwise we look at what attributes were edited to create
        // the context
        var updateContext = this.getPath('recordContext.update.asObject');
        return SC.ObjectController.create({
            // The undoManager needs to be specified for setting redo (I think)
            undoManager: this.get('undoManager'),
            // The Feature recordType
            recordType: this._context.get('recordType'),
            undoContext: undoContext,
            // Tell the statechart when we are redoing
            isRedoContext: YES,
            // An array of each record to be undone along with the values to undo to (context)
            // The resulting objects are {record:record, attributeToUpdate:value, attributeToUpdate:value, ...}
            recordContexts: arrayOrItemToArray(this._content).map(function(editedRecord) {
                return SC.ObjectController.create(
                    {record:editedRecord},
                    // If we have an update context use it
                    updateContext ?
                        updateContext :
                        // extract the primitive attributes from the updated record to be target attribute values for redoing
                        $.mapToDictionary(updateContext || editedRecord.getPath('attributes._updatedAttributes'), function(attr) {
                            return [attr, editedRecord.get(attr)];
                        })
                );
            }, this)
        },
        otherContext || {});
    },

    /***
     * Creates forward modification contexts (not undoing contexts)
     * @param recordsContext - context dict to apply to all records for blanket updates
     * @param statechartContext - context dict to apply to the outer context to pass non-record info. if this
     * contains 'content' that is assume to be the records or records that are modified. Otherwise
     * this._content is used
     */
    createModifyContext: function(recordsContext, statechartContext) {
        var content = (statechartContext && statechartContext.content) ? arrayOrItemToArray(statechartContext.content) : this._content;
        var undoContext =  this.undoContext(statechartContext);
        return SC.ObjectController.create({
            // The undoManager for records of the active layer selection
            undoManager: this.get('undoManager'),
            // The same structure as this object but used to undo the records back to their previous state
            undoContext: undoContext,
            // The same structure as this object but used to redo the records to the current edits
            // The redo operation is saved when we save the undo operation (via closure)
            redoContext: this.redoContext(statechartContext, undoContext),
            // The Feature recordType
            recordType: this._context.get('recordType'),
            // An array of each records to be updated along with the values to update (context)
            // The resulting object is {record:record, attributeToUpdate:value, attributeToUpdate:value, ...}
            // If we already have recordContexts, it means we are a redo operation, so use it instead of our
            // possibly edited records. For the corner case where the user edits records and hits redo,
            // we must abandon their edits and use what's stored in the redo context. Alternatively
            // we could change the UI to destroy all redos whenever they edit--redos are destroyed when they save
            recordContexts: statechartContext.get('recordContexts') || arrayOrItemToArray(content).map(function(record) {
                return SC.ObjectController.create({
                    record:record
                },
                    recordsContext
                );
            })
        },
        statechartContext || {});
    }
});
