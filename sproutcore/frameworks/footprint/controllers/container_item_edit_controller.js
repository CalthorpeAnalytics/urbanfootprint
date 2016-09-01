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
 * For items that are stored in set, like BuiltForms and Policies, this extension takes care of adding newly saved items to the active set via postSave
 * @type {*}
 */
Footprint.ContainerItemEditController = SC.ObjectController.extend({
    /**
     * This is the EditController of the container to which new items need to be added
     */
    containerEditController: null,
    /**
     * The property of the container that contains the items (e.g. 'built_forms' for BuiltFormSet)
     */
    containerItemProperty:null,

    /*
    * Used to make sure the conterEditController.objectController is READY_CLEAN before editing the active container
     */
    _containerObjectController:null,
    /***
     * After saving the item we need to add it to the active container if it's new.
     * TODO in the future it should be possible to add it to multiple sets based on the UI.
     * @param records: The saved records
     * @param created: YES if the item is newly created, NO if it was simply updated
     */
    onSaved: function(records, created) {
        if (created) {
            var containerEditController = this.get('containerEditController');
            this.set('_containerObjectController', containerEditController.get('objectController'));
        }
    },
    _updatingContainer: function() {
        if (this.getPath('_containerObjectContent.status')===SC.Record.READY_CLEAN) {
            this.set('_containerObjectController', null);
            var containerEditController = this.get('containerEditController');
            containerEditController.updateCurrent();
            var container = containerEditController.get('content');
            container.get('containerItemProperty').pushObject(this.get('content'));
            containerEditController.save();
        }
    }.observes('._containerObjectContent'),

    _toStringAttributes: function() {
        return 'recordType state content objectController'.w();
    }
});
