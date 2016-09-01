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
 * Called as a method by enterState, and triggered as an action by CrudState's
 * CRUD actions (see crud_state).
 */
// All modal actions (e.g. closing the modal) can only be taken from the
// ready state. Once in the saving state, the user is blocked from taking
// actions until the save action completes or fails.
Footprint.CrudModalReadyState = SC.State.extend({
    /***
     * Delete the selected record
     * @param context
     */
    doPromptDeleteRecord:function(context) {
        var pluralizedContext = toArrayController(
            this.parentState._context,
            {content:context.get('content'), crudType:'delete'});

        if (pluralizedContext.filter(function(record) {
            return record.get('status') !== SC.Record.READY_NEW;
        }, this).get('length') == 0) {
            this.doDeleteRecord(context);
            return;
        }

        SC.AlertPane.warn({
            message: 'You are about to remove the following item%@: %@. All data will remain intact on the server.'.fmt(
                pluralizedContext.get('length') > 1 ? 's' : '', // TODO auto-pluralize
                pluralizedContext.mapProperty('name').join(', ')
            ),
            description: '',
            caption: '',
            content: pluralizedContext.get('content'),
            buttons: [
                { title: 'Cancel' },
                { title: 'Proceed', action:'doDeleteRecord' }
            ]
        });
    },
    doDeleteRecord: function(context) {
        var pluralizedContext = toArrayController(
            this.parentState._context || {},
            {content:context.get('content'), crudType:'delete'});
        // Set the deleted property on the record.
        pluralizedContext.forEach(function(record) {
            record._deleteSetup();
        });
        // If these are all new records just return. They are delete from view
        // and will be discarded when the state exits.
        if (pluralizedContext.filter(function(record) {
            return record.get('status') !== SC.Record.READY_NEW;
        }, this).get('length') == 0) {
            // Tell the recordsEditController to update its content
            // For some reason its local query can't pick up the record.delete flag being set
            this.parentState._recordsEditController.propertyDidChange('content');
            return;
        }

        // Deselect all objects in case we are selected records that will be removed
        // The controller should be wired up to reselect the selection of the source controller
        // Remove created records (that weren't saved)
        // Find the minimum selection index to reselect the adjacent object after
        var selection = this.parentState._recordsEditController.get('selection');
        if (selection) {
            var selIndexes = selection.indexSetForSource(context.get('content'));
            this._index = selIndexes ? selIndexes.min : 0;
        }
        this.get('statechart').sendAction('doSave', pluralizedContext);
    },
    /***
     * Pack up our things and go to the save state.
     **/
    doSave: function(context) {
        // Use the content already in the _context unless context passes a new one in. This would
        // only be the case for an inline delete button or similar that operates on a single record
        // and saves immediately. We also use the context if we want all of the edit controller's
        // content that is dirty to be saved. This latter case needs a refactor.
        // Normally a save all button will be hit, which means no content passed in.
        var pluralizedContext = toArrayController(
            this.parentState._context || {},
            // If context.content is present use it instead but make sure only new and dirty items are used
            context && context.get('content') ? {content:context.get('content') } : {});
        this.gotoState(this.parentState.savingRecordsState, pluralizedContext);
    },

    /***
     * Calls save followed by cancel
     * @param context
     */
    doSaveAndClose: function(context) {
        var pluralizedContext = toArrayController(
            {doClose: YES},
            this.parentState._context || {},
            // If context.content is present use it instead but make sure only new and dirty items are used
            context.get('content') ? {content:context.get('content') } : {});
        this.gotoState(this.parentState.savingRecordsState, pluralizedContext);
    },

    enterState: function(context) {

        // Create the complete context. This will get passed around with the content overridden sometimes
        // when different content is the target of an action
        this._context = SC.ArrayController.create({
            content: context.get('content'),
            store: this.getPath('parentState._store'),
            recordType:context.get('recordType'),
            recordsEditController:context.get('recordsEditController')
        });

        // Sometimes we enter the state without a recordType. It's not clear why.
        // reset the _context to the parent state's
        if (!this._context.get('recordType')) {
            logWarning("this._context lacked a recordType");
            this._context = this.getPath('parentState._context');
        }

        // Verify that the content matches the recordType
        this._context.content.forEach(function(record) {
            if (!record.instanceOf(this._context.get('recordType')))
                throw "Content %@ does not match recordType %@".fmt(record.constructor, recordType)
        }, this);
        // Set the complete context up the line
        this.setPath('parentState._context', this._context);
        this.setPath('parentState.parentState._context', this._context);

        // Select content on the next run loop
        if (context.get('content'))
            this.invokeNext(this.selectContent);
    },
    selectContent: function() {
        this._context.get('recordsEditController').selectObjects(this._context.get('content'));
    }
});
