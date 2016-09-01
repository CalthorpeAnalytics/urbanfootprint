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



Footprint.FootprintSelectView = SC.SelectView.extend({
    contentController: null,
    itemsBinding: SC.Binding.oneWay('*contentController.content'),
    itemTitleKey: null,
    selection: null,
    selectionBinding: SC.Binding.from('*contentController.selection'),

    selectedItemObserver: function () {
        if (this.get('selection') && this.getPath('selection.firstObject')) {
            var selection = this.getPath('selection.firstObject');
            var selection_item = selection.get(this.get('itemTitleKey'));
            //return if there is no selection item defined
            if (!selection_item && this.get(this.get('itemTitleKey'))) { return }
            var selectedItem = this.get('items').find(function (item) {
                return item.get(this.get('itemTitleKey')) == selection_item
            }, this);

            this.setPath('value', selectedItem);
        }
        else {
            this.set('value', null);
        }
    }.observes('.selection', '.items'),

    selectionObserver: function () {
        if (this.get('selection')) {
            var menuValue = this.getPath('menu.selectedItem.title');
            var contentConroller = this.get('contentController');
            var itemTitleKey = this.get('itemTitleKey');
            //sometimes when selecting from this button this value is null
            if (menuValue) {
                contentConroller.selectObject(this.get('items').find(function(obj) {
                    return obj.get(itemTitleKey)==menuValue;
                }));
            }
        }
    }.observes('*menu.selectedItem.title')
});
