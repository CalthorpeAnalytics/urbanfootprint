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

/***
 * In the case of cloning a record, we need to prepare for cloning
 * by making sure that all toOne and toMany attributes are fully loaded.
 * TODO. This isn't recursive yet but needs to be. I needs to load all
 * toOne and toMany records, then upon loading to call itself to load
 * all the toOne/toMany records of those loaded records. That
 * functionality should probably be encapuslated in LoadingRecordsState,
 * which can prevent infinite loops.
 */
Footprint.PrepareForCrudState = SC.State.extend({

    initialSubstate: 'initialState',
    initialState: SC.State,

    enterState: function(context) {
        this._context = context;
        this._store = this.getPath('parentState._store');
        this.prepareContent(context);
    },

    exitState: function() {
        this._context = null;
        this._store = null;
    },

    /***
     * Loads all child records that need to be fully loaded prior to cloning. Once complete
     * the top-level record is cloned.
     */
    cloningRecordsState: Footprint.LoadingRecordsState.extend({

        enterState: function(context) {
            this._store = this.getPath('parentState._store');
            sc_super();
        },

        didLoadRecords: function(context) {
            // Get the nested version of the content even if its already nested
            // Non-nested would be adding from the main interface, nested would be
            // adding from the modal interface that has a list of nested store records
            // The list is likely using a separate nestedStore
            if (context.getPath('length') != 1)
            // TODO we can support cloning multiple items if useful
                throw Error("Trying to clone from non singular context");
            var nestedSourceContent = this._store.materializeRecord(context.getPath('firstObject.storeKey'));
            // Do the clone
            try {
                var content = nestedSourceContent.cloneRecord(context.get('firstObject'));
            }
            catch(e) {
                // Catch exception raise by framework bug in footprint_record_cloning.js
                if (e.message != "Could not perform clone due to a bug in the framework. Please close the dialog box and try again.")
                    throw e;
            }
            Footprint.statechart.sendEvent('crudDidComplete', toArrayController(context, {content:content}));
        }
    }),

    /***
     * Handles local create or clone of a record and returns edit or the record target for update/view
     * @param context
     * @returns the content as an array
     */
    prepareContent: function(context) {

        // If we are not re-entering this state after a successful save or failure, set up the nested store
        // and clone the record
        var content;

        // The passed in or selected item. This might be the source record of a clone
        // or the record to be updated or deleted.
        // It might also be a cloned/created item when we're returning here by clicking
        // on a new item in the list
        var recordsEditController = context.get('recordsEditController');
        var sourceContextController = toArrayController(context, {content:
        // Set to passed in content if defined
            context.get('content') ||
                // Otherwise to the full selection or full content list
                (recordsEditController.getPath('selection.length') > 0 ?
                    recordsEditController.get('selection').toArray() : // toArray to force ordering
                    // Default to all for stuff like features
                    recordsEditController.get('content'))
        });

        // Get the content array status or individual record status
        if (!sourceContextController.get('status') || sourceContextController.get('status') !== SC.Record.READY_NEW) {
            if (context.get('crudType') === 'create') {
                // Create a record for each content item (whatever it is) or create a single record
                // content items are simply objects that can seed the records.
                content = context.get('content') || [{}].map(function(dataHash) {
                    return this._store.createRecord(
                        context.get('recordType'),
                        dataHash,
                        Footprint.Record.generateId());
                }, this);

                // Use the record type's _createSetup function to copy over
                // minimum values, like a config_entity's parent_config_entity
                // The seed record must be a complete record, not a new one
                var seedRecord;
                for(var i=0; i<recordsEditController.length(); i++) {
                    var record = recordsEditController.objectAt(i);
                    if (record.get('id') > 0) {
                        seedRecord = record;
                        break;
                    }
                }
                if (!seedRecord) {
                    throw Error("Cannot create a new record without any existing record as a template")
                }
                content.forEach(function(record) {
                    record._createSetup(seedRecord);
                }, this);
                this.get('statechart').sendEvent('crudDidComplete', toArrayController(sourceContextController, {content:content}));
            }
            else if (context.get('crudType') === 'clone') {
                this.get('statechart').gotoState('cloningRecordsState', sourceContextController);
            }
            else {
                // For all other cases of non-new sourceContent
                // This can be one or more items in an array
                this.get('statechart').sendEvent('crudDidComplete', sourceContextController);
            }
        }
        else {
            // If we have content that is a new record then being here means
            // that we are reentering this state.
            // This is also the update/view/delete case of existing records
            this.get('statechart').sendEvent('crudDidComplete', sourceContextController);
        }
    }
});
