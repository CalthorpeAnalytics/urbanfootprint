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
  * Mixin to deduce a selectedItem from an ArrayController
  * @type {{content: null, contentBinding: SC.Binding, selectedItem: null, selectedItemBinding: SC.Binding}}
*/
Footprint.SelectedItem = {
    content:null,
    selectedItem:null,
    selectedItemBinding:SC.Binding.oneWay('*controller.selection').transform(function(value) {
        return value ? value.firstObject() : null;
    })
};
