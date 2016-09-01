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


Footprint.ActiveController = SC.ObjectController.extend({

    init: function() {
        sc_super();
        // We require from to be set right-off-the bat to avoid problems. We'd have to get rid of this if from were ever bound
        if (!this.get('listController'))
            throw "'listController' property is null or undefined. Perhaps it wasn't sc_required or was declared below this definition";
    },
    /***
     * Bind to the singleSelection property of the the listController. When the selection changes we update
     * our content. We need a default null here so that content doesn't come back as undefined. undefined bindings
     * mess up bindings with other controllers, which will consequently try to set the content property.
     */
    contentBinding: SC.Binding.from('.listController*selection.firstObject').defaultValue(null),

    observeControllerProperty:null,

    /***
     * An ArrayController or TreeController that has a selection to which we should two-way bind
     */
    listController:null,

    /***
     * Determines when the initialContentObserver should fire
     * For listControllers, like TreeControllers that can't delegate their status to anything,
     * optionally a custom status that determines when to trigger the initialContentObserver
     */
    listStatus:function() {
        return this.getPath('listController.status');
    }.property('listController'),

    /***
     * This sets it to the first item of listController.selection or failing that the
     * first item of listController or list. If content is bound this setting will quickly be undone
     *
     */
    initialContentObserver:function() {
        if (this.get('listStatus') & SC.Record.READY)
            this.set('content', this.firstItemOfSelectionSetOrFirstItemOfList());
    }.observes('*listController.status'),


    /***
     * Since our controllers currently only support one active item, take the first item of the selection set, or
     * the first item of the list if nothing is selected
     * @returns {*|Object|Object|Object|Object}
     */
    firstItemOfSelectionSetOrFirstItemOfList: function() {
        return this.getPath('listController.selection').length() > 0 ?
            this.getPath('listController.selection.firstObject') :
            this.firstItem()
    },
    /***
     * The first item of the listController if nothing is selected. Override this for TreeControllers, etc
     * @returns {*|Object|Object|Object|Object}
     */
    firstItem: function() {
        return this.getPath('listController.firstObject');
    },


    toString: function() {
        return this.toStringAttributes('content listController listStatus'.w());
    }

});
