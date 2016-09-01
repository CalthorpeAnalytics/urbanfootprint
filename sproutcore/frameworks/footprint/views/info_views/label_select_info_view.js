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

sc_require('views/label_select_view');

/***
 * A LabelSelectView along with a label
 * @type {*|SC.RangeObserver|Class|void}
 */
Footprint.LabelSelectInfoView = SC.View.extend({
    layout: { height: 44 },
    classNames: ['footprint-label-select-info-view'],
    childViews:['nameTitleView', 'labelSelectView'],
    title: null,

    content: null,
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    /**
     * Default to the content's status. Override if needed
     */
    status: function() {
        return this.get('contentStatus');
    }.property('contentStatus').cacheable(),
    itemTitleKey:null,
    includeNullItem:null,
    includeNullItemIfEmpty:null,
    nullTitle:null,
    nullTitleIfEmpty:null,
    selection: null,
    action: null,
    toolTip: null,
    buttonLayout: { top: 20, height: 24 },
    selectedItem: null,
    selectedItemBinding: '.labelSelectView.selectedItem',
    menuWidth: null,
    maxHeight: null,

    nameTitleView: Footprint.LabelView.extend({
        layout: {height:20},
        classNames: ['footprint-editable-title-view'],
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    labelSelectView: Footprint.LabelSelectView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        classNames:['footprint-label-select-view'],
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        selectionBinding: '.parentView.selection',
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        includeNullItemBinding: SC.Binding.oneWay('.parentView.includeNullItem'),
        includeNullItemIfEmptyBinding: SC.Binding.oneWay('.parentView.includeNullItemIfEmpty'),
        nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),
        nullTitleIfEmptyBinding: SC.Binding.oneWay('.parentView.nullTitleIfEmpty'),
        selectionActionBinding: SC.Binding.oneWay('.parentView.action'),
        toolTipBinding: SC.Binding.oneWay('.parentView.toolTip'),
        maxHeightBinding: SC.Binding.oneWay('.parentView.maxHeight'),
        menuWidthBinding: SC.Binding.oneWay('.parentView.menuWidth')
    })
});
