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


sc_require('views/add_button_view');
sc_require('views/menu_button_view');

Footprint.EditButtonView = Footprint.MenuButtonView.extend({

    classNames: "theme-button-gray theme-button theme-button-shorter".w(),
//    iconBinding: SC.Binding.oneWay('.parentView.icon'),
    // TODO the keyEquivalents will have to be overridden per view section, otherwise each could apply to several views
    menuItems: function () {
        return this.get('defaultMenuItems');
    }.property('defaultMenuItems').cacheable(),

    defaultMenuItems: [
        // View and edit the selected item's attributes
        { title: 'Get Info', keyEquivalent: 'ctrl_i', action: 'doGetInfo'},
        { title: 'New', keyEquivalent: 'ctrl_a', action: 'doCreateRecord'},
        { title: 'Clone', keyEquivalent: 'ctrl_c', action: 'doCloneRecord'},
        { title: 'Export', keyEquivalent: 'ctrl_e', action: 'doExportRecord'},
        { isSeparator: YES},
        // Remove the selected item
        { title: 'Remove', keyEquivalent: ['ctrl_delete', 'ctrl_backspace'], action: 'doRemove'},
        { title: 'Apply', keyEquivalent: ['ctrl_r'], action: 'doApply'}
    ],

    itemsBinding: SC.Binding.oneWay('.menuItems')
});
