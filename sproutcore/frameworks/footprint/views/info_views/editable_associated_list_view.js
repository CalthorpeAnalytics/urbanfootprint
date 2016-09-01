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

sc_require('views/item_views/select_or_add_view');
sc_require('views/label_view');
sc_require('views/editable_model_string_view');
sc_require('views/remove_button_view');

/**
 * Allows listing the associated items of a record as well as adding new or existing items to that list or creating
 * removing items from that list.
 */
Footprint.EditableAssociatedListView = SC.View.extend({

    classNames: ['footprint-editable-associated-list-view'],
    /***
     * The view has a title, a list of associated items, and a view to select or add from existing items
     */
    childViews:['titleView', 'scrollView', 'selectOrAddView'],
    /***
     * The collection of items of a record being edited. This should be A ChildRecordArray, ManyArray
     * or similar
    **/
    content: null,
    /***
     * The key of the item used to show it in the list
     */
    itemTitleKey: null,
    /***
     * All available items that can be selected and not filtered out by the searchString.
     * This can be bound to the filteredItems of a Footprint.SearchFilterMixin along
     * with searchString to limit the availalbe items to those matching the search string
     * and those not in the content
     */
    availableItems: null,
    /***
     * The user's selection among the available items. This should be the selection of
     * the Footprint.SearchFilterMixin controller
     */
    availableItemsSelection: null,
    /***
     * The search string that filters the available items
     */
    searchString: null,
    /**
     * The action to take when the user selects and existing item to add
    */
    selectionAction: null,
    /***
     * The action to take when the user adds a new item
     */
    addAction: null,
    /***
     * The action to take when the user removes an item
     */
    removeAction: null,

    // The title
    title: null,

    // Put this title in the associated item list when no items exist
    emptyTitle:  null,

    // The layout for the title view
    titleLayout: {height: 17, top: 0},

    titleView: Footprint.LabelView.extend({
        layout: SC.Binding.oneWay('.parentView.titleLayoutBinding'),
        classNames: ['footprint-editable-title-view'],
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    /***
     * A list of the current items of the record. These can be selected by the user for removal from the set
     */
    scrollView: SC.ScrollView.extend({
        classNames: ['footprint-editable-associated-list-scroll-view'],
        layout: {top: 17, bottom: 32},

        content:null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        itemTitleKey: null,
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        removeAction: null,
        removeActionBinding: SC.Binding.oneWay('.parentView.removeAction'),
        emptyTitle: null,
        emptyTitleBinding: SC.Binding.oneWay('.parentView.emptyTitle'),

        contentView: SC.SourceListView.extend({
            isEnabledBinding: SC.Binding.oneWay('.content').bool(),
            rowHeight: 20,
            isEditable: NO,
            actOnSelect: NO,
            items: null,
            itemsBinding: SC.Binding.oneWay('.parentView.parentView.content'),
            itemsStatus: null,
            itemsStatusBinding: SC.Binding.oneWay('*items.status'),
            itemTitleKey: null,
            itemTitleKeyBinding: SC.Binding.oneWay('.parentView.parentView.itemTitleKey'),
            emptyTitle: null,
            emptyTitleBinding: SC.Binding.oneWay('.parentView.parentView.emptyTitle'),
            // Creates a simple SC.Object for an empty title item
            emptyTitleItem: function() {
                var item = SC.Object.create();
                item.set(this.get('itemTitleKey'), this.get('emptyTitle'));
                return item;
            }.property('emptyTitle').cacheable(),

            content: function() {
                var items = this.get('items') || [];
                return (this.get('itemStatus')==SC.Record.EMPTY || items.get('length')==0) && this.get('emptyTitle') ?
                    [this.get('emptyTitleItem')] :
                    items;
            }.property('items', 'itemsStatus', 'items.[]', 'emptyTitle').cacheable(),

            removeAction: null,
            removeActionBinding: SC.Binding.oneWay('.parentView.parentView.removeAction'),

            exampleView: SC.View.extend(SC.Control, {
                classNames: ['footprint-source-list-item-view'],
                layout: { height: 24 },
                childViews: ['removeButtonView', 'nameLabelView'],
                // Content is what we are editing, which is an instance
                content: null,
                itemTitleKey: null,
                itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
                removeAction: null,
                removeActionBinding: SC.Binding.oneWay('.parentView.removeAction'),
                emptyTitle: null,
                emptyTitleBinding: SC.Binding.oneWay('.parentView.emptyTitle'),

                removeButtonView: Footprint.RemoveButtonView.extend({
                    layout: { left: 0, width: 10, centerY: 0, height: 11},
                    actionBinding: SC.Binding.oneWay('.parentView.removeAction'),
                    contentBinding: SC.Binding.oneWay('.parentView.content'),
                    items: null,
                    itemsBinding: SC.Binding.oneWay('.parentView.parentView.items'),
                    emptyTitle: null,
                    emptyTitleBinding: SC.Binding.oneWay('.parentView.emptyTitle'),
                    itemTitleKey: null,
                    itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
                    isVisible: function() {
                        return this.get('emptyTitle') &&
                            this.getPath('emptyTitle') != this.get('content').getPath(this.get('itemTitleKey'));
                    }.property('emptyTitle', 'content', 'itemTitleKey').cacheable()
                }),

                nameLabelView: Footprint.LabelView.extend({
                    classNames: ['footprint-editable-content-view'],
                    layout: { left: 20, width:370 },
                    isEditable: NO,
                    contentBinding: SC.Binding.oneWay('.parentView.content'),
                    contentValueKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey')
                })
            })
        })
    }),

    selectOrAddView: Footprint.SelectOrAddView.extend({
        layout: {bottom:0, height: 24, left: 0},
        contentBinding: SC.Binding.oneWay('.parentView.availableItems'),
        selectionBinding: '.parentView.availableItemsSelection',
        searchStringBinding: '.parentView.searchString',
        selectionActionBinding:  SC.Binding.oneWay('.parentView.selectionAction'),
        addActionBinding: SC.Binding.oneWay('.parentView.addAction'),
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
    })
});
