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

sc_require('views/info_views/info_view');
sc_require('views/label_select_view');

Footprint.SelectInfoView = Footprint.InfoView.extend({
    classNames: "footprint-select-info-view".w(),
    /**
     * The content is the list of items to select from
     */
    content:null,
    // Defaults to content.status. Optionally override to someone else's status
    status: null,

    selection: null,
    recordType:null,
    itemTitleKey:null,
    allowsMultipleSelection:null,
    emptyName:null,
    includeNullItem:NO,
    includeNullItemIfEmpty:NO,
    firstSelectedItem:null,
    // Indicates if items in the list can be selected
    isSelectable:YES,
    nullTitle: '----',
    nullTitleIfEmpty: null,
    // Max height of the panel popup
    maxHeight: 330,
    // The layout of the button and width of the menu. Use menuWidth property to override the
    // menu width.
    contentLayout: {},
    // Optional different width for the menu than the button
    menuWidth: null,
    // Optional icon to show for the button instead of the selected item title
    icon: null,

    // The action to take when selecting an item, defaults to 'doPickSelection'
    selectionAction: null,
    // The option target of the selectionAction, defaults to null
    targetAction: null,

    contentView: Footprint.LabelSelectView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        // The action to take when selecting an item, defaults to 'doPickSelection'
        selectionActionBinding: SC.Binding.oneWay('.parentView.selectionAction'),
        // An optional target of the selectionAction
        selectionTargetBinding: SC.Binding.oneWay('.parentView.selectionTarget'),

        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('*content.status'),
        parentViewStatus: null,
        parentViewStatusBinding: SC.Binding.oneWay('*parentView.status'),
        status: function() {
            return this.get('parentViewStatus') || this.get('contentStatus');
        }.property('parentViewStatus', 'contentStatus').cacheable(),

        selectionBinding: '.parentView.selection',
        isSelectableBinding: '.parentView.isSelectable',
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        allowsMultipleSelectionBinding: SC.Binding.oneWay('.parentView.allowsMultipleSelection'),
        emptyNameBinding: SC.Binding.oneWay('.parentView.emptyName'),
        includeNullItemBinding: SC.Binding.oneWay('.parentView.includeNullItem'),
        includeNullItemIfEmptyBinding: SC.Binding.oneWay('.parentView.includeNullItemIfEmpty'),
        nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),
        nullTitleIfEmptyBinding: SC.Binding.oneWay('.parentView.nullTitleIfEmpty'),
        maxHeightBinding: SC.Binding.oneWay('.parentView.maxHeight'),
        menuWidthBinding: SC.Binding.oneWay('.parentView.menuWidth'),
        iconBinding: SC.Binding.oneWay('.parentView.icon')
    })
});
