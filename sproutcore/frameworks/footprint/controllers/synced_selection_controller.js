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
 * A selection controller whose contents is a list of selectable values. Zero or one items in the list are selected,
 * depending on the property values of the editController.content indicated by the property at propertyKey. If all
 * of editController's content property values are identical, then that single identical item will be the selection
 * of this controller. If the controller's selection is updated to a new value or no value, all the editController's
 * content property values will be updated accordingly. If not all values are identical then there is no selected item.
 *
 */


Footprint.SyncedSelectionController = SC.ArrayController.extend(Footprint.SingleSelectionSupport, {

    /***
     * Set this to the controller whose content items are being bulk viewed or edited
     */
    editController:null,
    editControllerContent:null,
    editControllerContentBinding:SC.Binding.oneWay('.editController.content'),

    propKey:null,

    /***
     * Whenever the content changes select an item of the ArrayController if the content all have the same
     * property value
     */
    editControllerObserver: function() {
        if (this.get('editControllerContent').mapProperty(this.get('propKey')).uniq().length==1)
            this.selectObject(this.get('editControllerContent').firstObject().get(this.get('propKey')));
        else
            this.deselectObjects(this.get('selection'));
    }.observes('editControllerContent')
});
