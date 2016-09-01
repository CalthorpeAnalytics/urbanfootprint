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
sc_require('states/loading_concurrent_dependencies_state');
sc_require('states/crud_state');
sc_require('states/crud_modal_state');
sc_require('states/crud_modal_ready_state');

/***
 * Tracks a new DbEntity created on the server.
 * An instance of this state runs for every DbEntity that is currently being tracked
 * It has its
 */
Footprint.TrackNewDbEntityState = SC.State.extend({
    recordType: Footprint.DbEntity,
    loadingController: SC.ArrayController.create(),
    recordsEditController: null,
    recordsEditControllerBinding: SC.Binding.oneWay('.parentState.recordsEditController'),
    store: null,
    storeBinding: SC.Binding.oneWay('*recordsEditController.store'),
    didLoadEvent:'provisionalDbEntitiesDidLoad',

    // Set when the concurrent substate is created
    _context: null,


    doExitConcurrentState: function() {
    },

    enterState: function() {
        var context = this._context;

        // Invoke the following next so the state is done entering and bindings are updated
        this.invokeNext(function() {
            // Make sure the DbEntity is loaded in case it was requested from the server
            this.gotoState(
                this.newDbEntityIsReadyState,
                context
            );
        });
    },

    initialSubstate: 'readyState',
    readyState: SC.State,

    /***
     * New DbEntity has a separate CrudState since it doesn't actually save and has no modal.
     * This allows something else to use a modal while the upload and DbEntity save happens
     * This crudState simulates the save and then simply tracks post save progress
    */
    newDbEntityIsReadyState: SC.State.plugin('Footprint.DbEntitiesAreReadyState', {
        /***
         * Since the save already happened on the server, all we have to do
         * is call crudDidStart and crudDidFinish. This allows
         * Footprint.DbEntitiesAreReady to act as if it initiated the save
         * This puts us in the right state to track postSaveProgress.
         * Also call postSavePublisherStarted immediately, since we might miss that call from the server,
         * because the server starts post save processing immediately after the DbEntity is saved.
         */
        doSimulateSaveDbEntity: function(context) {
            // Call these as methods so that only our state handles them
            this.crudDidStart(context);
            this.invokeNext(function() {
                this.crudDidFinish(context);
                // Since we'll probably miss this call from the server, do it manually. If the server
                // message is picked up afterward it will just do the same thing twice, which is
                // to 0 the progress of the DbEntity
                this.postSavePublisherStarted(
                    SC.Object.create({class_name:'DbEntity', ids:[context.getPath('content.firstObject.id')]})
                )
            }, this)
        },

        /***
         * Override to quit this concurrent parent state
         * @param context
         */
        postSavePublishingFinished: function(context) {
            sc_super();
            this.parentState.doExitConcurrentState()
        },

        /***
         * Override to quit this concurrent parent state
         * @param context
         */
        postSavePublisherFailed: function(context) {
            sc_super();
            this.parentState.doExitConcurrentState()
        },

        enterState: function (context) {
            sc_super();
            // Call once the states have initialized
            this.invokeNext(function () {
                // Call directly, not as an event, so we don't trigger other concurrent states
                this.doSimulateSaveDbEntity(context);
            })
        }
    })
});
