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


sc_require('states/loading_records_state');
sc_require('states/prepare_for_crud_state');
sc_require('states/saving_records_state');

/***
 * This is the main state that CrudState uses for editing and saving.
 * Typically it coincides with a modal dialog, although its possible to run this without
 * one as well
 */
Footprint.CrudModalState = SC.State.extend({

    // ---------------------
    // Actions & Events
    //

    /***
     * By default discard changes to the nested store upon entering this state.
     * In the case where changes have already been made before entering the CrudState,
     * set this to NO. This occurs for cases like upload where changes begin before the modal is open
     */
    discardNestedStoreOnEnter: YES,

    /***
     * Called by one of the CRUD actions. This handler will be called when we are already in the modal.
     * It might respond to a clone, create or create action, so it sends us to the crudRecordsState
     * so that we are ready to perform those actions.
     * @param context
     */
    doProcessRecord: function (context) {
        var recordType = this.getPath('_context.recordType');
        // For modal info panes we don't have to worry about a new recordType coming through. That will only
        // happen if it changes from an action on that modal (e.g. BuiltForm subclasses). For non-modals,
        // we simply exit the state and re-enter with the new recordType, assuming that the non-modal will
        // preserve its state upon reopening.
        if (recordType && recordType !== context.get('recordType')) {
            if (this.parentState._infoPane.getPath('closeForNewModalPane')) {
                this.gotoState(this.modalState, context);
                return;
            }
            else {
                // Switching recordTypes within a modal. Reset the _recordsEditController
                this.initializeController(context);
            }
        }
        // Respond to the passed in content and crudType by preparing a clone, new record, etc.
        this.get('statechart').gotoState(this.crudRecordsState, context);
    },

    /***
     * Responds to an edit controller changing selection.
     * If that controller, the context, matches this _recordsEditController
     * change to the new selection
     * @param context
     */
    selectedRecordChangeObserved: function (context) {
        // Make sure this is our recordEditController changing
        if (SC.Set.create(context.getPath('selection')).isEqual(SC.Set.create(this._context.get('content'))))
            return;

        var content = this._recordsEditController.getPath('selection').toArray();
        this.get('statechart').sendEvent('selectedRecordDidChange', toArrayController(this._context, {content: content}));
    },
    /***
     * Separate the event out in-case we need to disable calling prepareContenxtState during a save.
     * This problem is acute when deleting a record. Going to parepareContentState disrupts the save (delete) process.
     * @param context
     */
    selectedRecordDidChange: function (context) {
        this.get('statechart').gotoState(this.crudRecordsState, context);
    },
    /***
     * Close the modal, clearing any changes without saving them.
     * This is here and not in showingModalState in case the user has to close during a saingRecordState
     * If the context contains content (either an item or array), those items will be processed.
     * Otherwise this._recordsEditController.content will be used
     */
    doPromptCancel: function (context) {
        context = context || SC.Object.create();
        var postConfirmAction = context.get('postConfirmAction') || 'doCancel';

        // If all records in the controller are new or clean, just delete without a prompt
        var nestedStore = this._recordsEditController.get('store');
        var unclean_statuses = [SC.Record.READY_NEW, SC.Record.READY_DIRTY];
        var content = context.get('content');
        var newOrDirtyRecords = (content ?
            arrayOrItemToArray(content) :
            this._recordsEditController).map(function (record) {

            var storeKey = record.get('storeKey');
            var status = nestedStore.peekStatus(storeKey);
            return unclean_statuses.contains(status) ? nestedStore.materializeRecord(storeKey) : null;
        }, this).compact();

        // No changes, proceed
        if (newOrDirtyRecords.get('length') == 0) {
            this.get('statechart').sendAction(postConfirmAction, toArrayController(context, {confirm: YES}));
            return;
        }

        SC.AlertPane.warn({
            message: 'The following items were edited but not saved: %@. Discard changes or go back?'.fmt(
                newOrDirtyRecords.mapProperty('name').join(', ')
            ),
            description: '',
            caption: '',
            confirm: YES, // Used by the action
            buttons: [
                {title: 'Go Back'},
                {title: 'Discard', action: postConfirmAction}
            ]
        });
    },
    doCancel: function (context) {
        this.get('statechart').sendEvent('modalDidCancel', context);
        this.gotoState(this.parentState.noModalState);
    },

    /***
     * Revert the changes to the current record
     */
    doPromptRevert: function (context) {
        var postConfirmAction = (context && context.get('postConfirmAction')) || 'doRevert';

        // If all records in the controller are new or clean, just delete without a prompt
        var nestedStore = this._recordsEditController.get('nestedStore');
        var unclean_statuses = [SC.Record.READY_NEW, SC.Record.READY_DIRTY];
        var newOrDirtyRecords = this._recordsEditController.map(function (record) {
            var storeKey = record.get('storeKey');
            var status = nestedStore.peekStatus(storeKey);
            return unclean_statuses.contains(status) ? nestedStore.materializeRecord(storeKey) : null;
        }, this).compact();
        // No changes, proceed
        if (newOrDirtyRecords.get('length') == 0) {
            this.get('statechart').sendAction(postConfirmAction, toArrayController(context, {confirm: YES}));
            return;
        }

        SC.AlertPane.warn({
            message: 'You are about revert the following item%@ edited but not saved: %@. Changes will be discarded.'.fmt(
                newOrDirtyRecords.get('length') ? 's' : '',
                newOrDirtyRecords.mapProperty('name').join(', ')
            ),
            description: '',
            caption: '',
            confirm: YES, // Used by the action
            buttons: [
                {title: 'Go Back'},
                {title: 'Continue', action: postConfirmAction}
            ]
        });
    },
    doRevert: function () {
        this.gotoState(this.parentState.noModalState);
    },
    // ---------------------
    // Substates
    //

    initialSubstate: 'initialState',
    initialState: SC.State,

    enterState: function (context) {
        this._context = context;
        this._store = Footprint.store.get('autonomousStore');
        // Normally we discard changes to the store upon enter to have a clean nested store
        if (this.get('discardNestedStoreOnEnter'))
            this._store.discardChanges();
        // Setup the recordsEditController. This is called whenever the recordType/recordsEditController changes,
        // not just on enterState
        this.initializeController(context);
        this.get('statechart').sendAction('doShowModal', context);
        // Process the content. This will send us to the crudRecordsState
        this.doProcessRecord(context);
    },

    exitState: function () {

        this.get('statechart').sendEvent('modalDidExit');

        if (this._recordsEditController) {
            // Stop observing the selection
            this._recordsEditController.removeObserver('selection', this, 'selectedRecordChangeObserved');

            // Deselect all objects in case we are selected records that will be removed
            // The controller should be wired up to reselect the selection of the source controller.
            this._recordsEditController.deselectObjects(this._recordsEditController.get('selection'));
        }

        // Discard changes
        if (this._store) {
            // Normally we discard changes to the store upon exit to clean the nested store
            if (this.get('discardNestedStoreOnEnter'))
                this._store.discardChanges();
            this._store = null;
        }
        this._store = null;

        // Cleanup
        this._recordsEditController = null;
        this._context = null;
        this.get('statechart').sendAction('doHideModal');
    },

    initializeController: function (context) {

        // If a different recordsEditController was previously used for a different recordType,
        // stop observing its selection
        if (this._recordsEditController)
            this._recordsEditController.removeObserver('selection', this, 'selectedRecordChangeObserved');

        this._recordsEditController = context.get('recordsEditController');
        // Set the nestedStore of the controller. This updates its content query
        // to a new query with this nestedStore
        if (context.get('cycleNestedStore')) {
            if (!this._store.get('isDestroyed'))
                this._store.discardChanges();
            this._store = Footprint.store.get('autonomousStore');
        }
        this._recordsEditController.set('store', this._store);
        // For recordTypes that have a dependencyContext, initialize the dependency recordsEditController too
        var dependencyRecordsEditController = context.getPath('dependencyContext.recordsEditController');
        if (dependencyRecordsEditController)
            dependencyRecordsEditController.set('store', this._store);

        // Observe changes to the selection so we can reset the content
        this._recordsEditController.addObserver('selection', this, 'selectedRecordChangeObserved');
    },


    /***
     * In the case of cloning a record, we need to prepare for cloning
     * by making sure that all toOne and toMany attributes are fully loaded.
     * TODO. This isn't recursive yet but needs to be. I needs to load all
     * toOne and toMany records, then upon loading to call itself to load
     * all the toOne/toMany records of those loaded records. That
     * functionality should probably be encapuslated in LoadingRecordsState,
     * which can prevent infinite loops.
     */
    crudRecordsState: Footprint.PrepareForCrudState.extend({
        crudDidComplete: function (context) {
            this.gotoState(
                this.parentState.modalReadyState,
                context);
        }
    }),

    /***
     * Called as a method by enterState, and triggered as an action by CrudState's
     * CRUD actions (see above).
     */
    // All modal actions (e.g. closing the modal) can only be taken from the
    // ready state. Once in the saving state, the user is blocked from taking
    // actions until the save action completes or fails.
    modalReadyState: SC.State.plugin('Footprint.CrudModalReadyState'),

    savingRecordsState: SC.State.plugin('Footprint.SavingRecordsState', {
        // -------------------------
        // Save Events
        //

        // parent state
        modalState: SC.outlet('parentState'),
        // grandparent state
        crudState: SC.outlet('parentState.parentState'),

        /***
         * Override the parent's event handler to ignore selection changes.
         * @param context
         */
        selectedRecordDidChange: function (context) {

        },

        // Override to send an events for RecordsAreReady state
        startingCrudState: function (context) {
            // Announce to RecordsAreReady states that the CRUD started.
            // This will be handled and ignored for recursive calls
            this.get('statechart').sendEvent('crudDidStart', context);
        },

        /***
         * Called when all records, including children, have completed CRUD.
         * @param context
         */
        didFinishRecords: function (context) {
            if (context.getPath('content.firstObject.constructor') !== this._context.getPath('content.firstObject.constructor')) {
                logWarning('Context recordType: %@ does not match our recordType: %@. ChildRecordCrudState should have handled this event!'.fmt(
                    context.getPath('content.firstObject.constructor'),
                    this._context.getPath('content.firstObject.constructor'))
                );
                return NO;
            }
            // All good, send the updated records to the main store
            this.get('modalState')._store.commitChanges(YES);

            // Announce to RecordsAreReady states that the CRUD finished
            this.get('statechart').sendEvent('crudDidFinish', this._context);
            if (context['doClose']) {
                // If doClose is passed then attempt to close the dialog now that save has completed
                this.get('modalState').doPromptCancel(context);
            }
            else if (this.get('crudState')._infoPane) {
                // Slight hack: If we have an info pane open, go back to the ready state so
                // the user can continue editing.
                // TODO it's possible that _context was already nulled out by the exitState, so use the parentState's if needed
                this.gotoState(this.get('modalState').modalReadyState, this._context || this.getPath('parentState._context'));
            }
            else {
                // If we're doing editing-in-the-blind, go
                // all the way back to noModalState.
                this.gotoState(this.get('crudState').noModalState);
            }
            return YES;
        },

        /***
         * Handle failure messages from the child record crud states
         * @param context
         * @returns {window.YES|*}
         */
        saveChildRecordsDidFail: function (context) {
            this.saveRecordsDidFail(context);
            return YES;
        },
        /***
         * Called when saving fails at one of several spots along the way.
         */
        saveRecordsDidFail: function (context) {
            // Cancel any updates in progress. We don't want to discard
            // what the user has done, just set records that are in a loading
            // state back to READY_NEW or READY_DIRTY
            this.get('statechart').sendAction('softCancelUpdate');

            var pluralizedContext = toArrayController(this.get('modalState')._context);
            SC.AlertPane.warn({
                message: 'Failed to %@ records. Report this error if it recurs.'.fmt(this.get('crudType')),
                description: 'Record Types: %@'.fmt(uniqueRecordTypes(pluralizedContext.get('store'), pluralizedContext.get('content')).join(', '))
            });
            // Announce that the records failed to update so that a state can reset their record status
            this.get('statechart').sendEvent('recordsDidFailToUpdate', pluralizedContext);
        },

        saveBeforeRecordsDidFail: function (context) {
            var pluralizedContext = toArrayController(
                this.get('modalState')._context,
                {content: context.get('content')});
            SC.AlertPane.warn({
                message: 'Failed to create/update prerequisite records. Report this error if it recurs.',
                description: 'Record Types: %@'.fmt(uniqueRecordTypes(pluralizedContext.get('store'), pluralizedContext.get('content')).join(', '))
            });
            // Goto our readyState so that the user can attempt to update again.
            this.gotoState(this.get('modalState').modalReadyState, pluralizedContext);
        },

        saveAfterRecordsDidFail: function (context) {
            var pluralizedContext = toArrayController(
                this.get('modalState')._context,
                {content: context.get('content')});
            SC.AlertPane.warn({
                message: 'Failed to %@ dependent records. Report this error if it recurs.'.fmt(context.get('crudType')),
                description: 'Record Types: %@'.fmt(uniqueRecordTypes(pluralizedContext.get('store'), pluralizedContext.get('content')).join(', '))
            });
            // Goto our readyState so that the user can attempt to update again.
            this.gotoState(this.get('modalState').modalReadyState, pluralizedContext);
        },
        /***
         * Called by the above actions whenever saving fails at any step.
         */
        recordsDidFailToUpdate: function (context) {
            var pluralizedContext = toArrayController(
                this.get('modalState')._context,
                {content: context.get('content')});
            pluralizedContext.get('content').forEach(function (record) {
                record.set('progress', 0);
                Footprint.changeRecordStatus(this._store, record,
                    SC.Record.ERROR,
                    record.get('id') < 0 ?
                        SC.Record.READY_NEW :
                        SC.Record.READY_DIRTY);
            }, this);
            // Slight hack: If we have an info pane open, go back to the ready state so
            // the user can continue editing. If we're doing editing-in-the-blind, go
            // all the way back to noModalState.
            if (this.get('crudState')._infoPane) {
                // TODO sometimes the context is nulled out by the exitState
                this.gotoState(this.get('modalState').modalReadyState, context || this.getPath('parentState._context'));
            }
            else
                this.gotoState(this.get('crudState').noModalState);
        },

        // -------------------------
        // Internal support
        //
        enterState: function (context) {
            // Crud Saving indicator on
            context.setPath('recordsEditController.isSaving', YES);
            this._active = YES;
            // Reset the status indicator on the main store records.
            context.forEach(function (record) {
                F.store.materializeRecord(record.get('storeKey')).set('progress', 0);
            });
            return sc_super();
        },
        exitState: function (context) {
            // Crud Saving indicator off
            (context || this._context).setPath('recordsEditController.isSaving', NO);
            return sc_super();
        }
    })
});
