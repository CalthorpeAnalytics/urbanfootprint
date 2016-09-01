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

/***
 * This state CRUDs all child records of record in parallel
 * @type {*}
 */
Footprint.SavingChildRecordsState = SC.State.extend({

    /***
     * The event to call upon success.
     */
    successEvent: null,
    /***
     * The name of the event to send in the event of failure
     */
    failEvent: null,

    /***
     * Handles the failure of saving child records by sending an event saveBeforeRecordsDidFail
     * @param context
     */
    saveRecordsDidFail: function(context) {
        if (this.getPath('parentState._context.content') === context.get('content')) {
            SC.Logger.debug('Handled %@'.fmt(context.getPath('content.firstObject.constructor')));
            this.get('statechart').sendEvent(this.get('failEvent'), context);
            return YES;
        }
        SC.Logger.debug('Not handled: saveRecordsDidFail');
        return NO;
    },

    didFinishChildRecords: function(context) {

        if (this.getPath('parentState._context.content') === context.get('content')) {
            SC.Logger.debug('Handled %@'.fmt(context.getPath('content.firstObject.constructor')));
            // Resassign the updated records to the content to trick the content instances into
            // updating their attributes
            this.reassignUpdatedRecords(context);
            this.get('statechart').sendEvent(this.get('successEvent'), context);
            return YES;
        }
        SC.Logger.debug('Not handled: didFinishChildRecords');
        return NO;
    },

    /***
     * Called in didFinishChildRecords
     * @param context
     */
    reassignUpdatedRecords: function (context) {
        // Fixes a bug in SC (TODO this might only apply to nested records)
        // For toOne properties.
        // The instance reference is always updated but the attribute id is not.
        // The fix is to set the instance property to itself, which is probably harmless
        var recordType = context.get('recordType') || context.getPath('content.firstObject.constructor');
        var properties = this.getProperties(context.getPath('content.firstObject')).filter(function(prop) {
            return recordType.prototype[prop].kindOf(SC.SingleAttribute);
        });
        context.get('content').forEach(function (content) {
            var madeFix = NO;
            properties.forEach(function (property) {
                if (content.get(property) && content.readAttribute(property) != content.get(property).get('id')) {
                    content.writeAttribute(property, content.get(property).get('id'));
                    madeFix = YES;
                }
            });
            // Make sure the record isn't dirtied
            if (madeFix)
                F.store.writeStatus(content.get('storeKey'), SC.Record.READY_CLEAN);
        });
    },

    /***
     * Receives failure messages and sends a specific event alerting the parent records that the children have failed
     * @param context
     */
    saveRecordsDidFail: function(context) {
        this.get('statechart').sendEvent('saveChildRecordsDidFail', context);
    },

    getProperties: function(record) {
        throw Error('Must override');
    },

    initialSubstate:'readyState',
    readyState:SC.State,

    enterState:function() {
        // Always use the _context set in the parentState, not the passed in context. This matters when recursing because
        // concurrent sessions receive the context of the concurrent base state, which we don't want
        var context = this._context = this.getPath('parentState._context');
        var records = context.get('content');
        // Assume all records are the same recordType
        var properties = this.getProperties(records.get('firstObject'));
        this._properties = properties;

        // Save each child record in a new SavingRecordsState substate of savingChildrenState
        var savingChildrenState = this.getState('%@.savingChildrenState'.fmt(this.get('fullPath')));
        var childRecordsThatAreBusyLoading = [];
        properties.forEach(function(propertyPath) {
            // Map the property of each each record and flatten into childRecords
            // It's possibly to have no child records if the property on all records is null or empty
            var childRecords = $.shallowFlatten(mapPropertyPath(records, propertyPath)).compact();
            // Note any child records that are BUSY_LOADING as a result of saving the main record
            // (e.g. Saving a new DbEntity will return a new FeatureBehavior that needs to load)
            childRecordsThatAreBusyLoading.pushObjects(
                childRecords.filterProperty('status', SC.Record.BUSY_LOADING)
            );
            if (childRecords.length > 0) {
                var substateName = 'saving%@State'.fmt(propertyPath.capitalize().camelize());
                if (savingChildrenState.getState(substateName)) {
                    // For some reason, the child state sometimes already exists
                    var substate = savingChildrenState.getState(substateName);
                    // Just update the context
                    substate._context = SC.Object.create({content:childRecords, store:context.get('store')});
                    // Use flag until we can destroy them
                    substate._active = YES;
                }
                else {
                    savingChildrenState.addSubstate(
                        substateName,
                        Footprint.SavingRecordsState,
                        // These are attributes of the state, not the context passed to its enter state
                        // We need to make sure that _context overrules the context passed in, since that will be the parent's
                        // Therefor SavingRecordsState.enterState prioritizes the _context
                        {_context: SC.Object.create({content:childRecords, store:context.get('store')}), _active:YES }
                    );
                }
            }
        }, this);
        // We now have substates with which to recurse on each child record.
        // If the saving of the main record caused a child record to reload, we need to wait for that
        // record to finish loading. Once all child records are save them
        if (childRecordsThatAreBusyLoading.get('length') > 0) {
            // Wait for children to load
            this.gotoState(
                this.loadingChildRecordsState,
                SC.Object.create({content: childRecordsThatAreBusyLoading})
            );
        }
        else {
            // Just save the children
            this.invokeOnce('gotoSubstateIfNeeded');
        }
    },

    /***
     * Simply wait for child records to be READY_CLEAN and then proceed to savingChildrenState
     */
    loadingChildRecordsState: Footprint.LoadingState.extend({
        didLoadEvent:'childRecordsDidLoad',
        /***
         * We have to check the status of each record since we have no query or ToManyArray
         */
        checkRecordStatuses: YES,
        recordArray: function(context) {
            return context.get('content')
        },
        childRecordsDidLoad: function() {
            this.invokeOnce(this.gotoSubstateIfNeeded);
        }
    }),

    /***
     * Goes to the savingChildrenState with concurrent substates if any were created.
     * Otherwise sends the didFinishChildRecords event
     */
    gotoSubstateIfNeeded: function() {
        if (this.getPath('savingChildrenState.substates.length') > 0)
            this.gotoState('%@.savingChildrenState'.fmt(this.get('fullPath')), this._context);
        else
            this.get('statechart').sendEvent('didFinishChildRecords', this._context);
    },

    savingChildrenState: SC.State.extend({
        substatesAreConcurrent:YES,

        enterState: function(context) {
            this._savingRecordsQueue = [];
            this._context = context;
            this.get('substates').forEach(function(substate) {
                if (!substate._active)
                    return;

                // TODO
                // This should never be undefined, but sometimes is when we reenter substates
                // Hopefully the solution is to property destroy the child states each time
                (substate.getPath('_context.content') || []).forEach(function(childRecord) {
                    this._savingRecordsQueue.push(childRecord);
                }, this);
            }, this);
            if (this._savingRecordsQueue.length == 0) {
                // No records to save
                this.get('statechart').sendEvent('didFinishChildRecords', this._context);
            }
        },
        exitState: function(context) {
            // Destroy dynamic child substates on exit so we can recreate them on the next run
            // TODO this causes instability
            /*
            this.getPath('substates').forEach(function (substate) {
                substate.destroy();
                this.set(substate.get('name'), undefined);
            }, this);
            */
            this._savingRecordsQueue = null;
            this._context = null;
        },

        /**
         * Respond to a child state finishing
         * @param context
         */
        didFinishRecords: function(context) {
            var handled = NO;
            this.get('substates').forEach(function(substate) {
                if (!substate._active)
                    return;

                if (!handled && substate.getPath('_context.content') == context.get('content')) {
                    handled = YES;
                    SC.Logger.debug('Handled %@'.fmt(context.getPath('content.firstObject.constructor')));
                    var dequeueRecords = [];
                    substate.getPath('_context.content').forEach(function(childRecord) {
                        dequeueRecords.push(childRecord);
                    }, this);
                    this._savingRecordsQueue.removeObjects(dequeueRecords);
                    if (this._savingRecordsQueue.length == 0) {
                        this.get('statechart').sendEvent('didFinishChildRecords', this._context);
                    }
                }
            }, this);
            if (handled)
                return YES;
            SC.Logger.debug('Not handled: didFinishRecords');
            return NO;
        }
    })
});
