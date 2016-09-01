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


sc_require('views/section_toolbars/editing_toolbar_view');
sc_require('views/section_toolbars/edit_title_view');
sc_require('views/label_select_view');

/**
 * Replaces the awful SC.SelectView with a label and a menu button
 * @type {Class}
 * TODO SC.PopupButtonView.extend({ init: function() { sc_super(); this.menu.st'anchor', this) } })
 * This will set anchor and allow binding to the "parentView"
 */
Footprint.LabelSelectToolbarView = Footprint.EditingToolbarView.extend({
    layout: {height: 24},
    classNames: "footprint-label-select-toolbar-view".w(),
    icon: null,
    selection:null,

    titleView: Footprint.EditTitleView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        activeRecordBinding: SC.Binding.oneWay('.parentView.activeRecord'),
        menuItemsBinding: SC.Binding.oneWay('.parentView.menuItems'),
        controlSizeBinding: SC.Binding.oneWay('.parentView.controlSize'),
        titleBinding: SC.Binding.oneWay('.parentView.title'),
        iconBinding: SC.Binding.oneWay('.parentView.icon'),

        contentBinding: SC.Binding.oneWay('.parentView.content'),
        selection: null,
        selectionBinding: '.parentView.selection',

        itemTitleKey: null,
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),

        labelView: Footprint.LabelSelectView.extend({
            layout: {height: 24, left: 31, right: 2},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selection: null,
            selectionBinding: '.parentView.selection',
            selectedItemBinding: '.parentView.selection.firstObject',
            itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey')
        })
    })
});
