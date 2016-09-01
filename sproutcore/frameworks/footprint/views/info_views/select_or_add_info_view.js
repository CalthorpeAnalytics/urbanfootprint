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


sc_require('views/info_views/select_info_view');
sc_require('views/item_views/select_or_add_view');

/***
 * Presets a drop-down and an add button to allow one item to be selected to a list or to add a new item
 * to the list and make that the selected item
 */
Footprint.SelectOrAddInfoView = Footprint.SelectInfoView.extend({
    // By default show the add button. If we just need to select to do something, then don't show it
    showAddButton: YES,
    inputViewLayout: {right: 66},
    buttonLayout: { right: 34, width: 30, centerY: 0, height: 18},
    addButtonLayout: {right: 0, width: 30, centerY: 0, height: 18},
    isTextArea: NO,
    hint: null,
    appendSelectionToInput: NO,
    searchSeparatorCharacters: [' '],
    // This can be used to update the value of the input if the source controller changes
    value: null,
    searchString: null,
    searchContext: null,
    selectionAction: 'doPickSelection',
    icon: sc_static('images/section_toolbars/pulldown.png'),

    /***
     * Override to change default behavior. TODO handle this with events
     */
    handleDownKey: function() {
        var labelSelectView = this.get('labelSelectView');
        labelSelectView.makeMenuContentFirstResponder();
        labelSelectView.selectFirstMenuItem();
    },

    /***
     * Override Footprint.LabelSelectView with Footprint.SelectOrAddView
     * SelectOrAddView gives us an optional add button and an input field with search functionality
     */
    contentView: Footprint.SelectOrAddView.extend({

        /***
         * Delegate to parent. TODO use events instead
         */
        removeMenu: function() {
            this.get('labelSelectView').removeMenu();
        },

        /***
         * Delegate to parent. TODO use events instead
         */
        handleDownKey: function() {
            this.get('labelSelectView').handleDownKey();
        },

        /***
         * The layout of this view can be set by setting the parent view's contentViewLayout
         */
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
        inputViewLayoutBinding: SC.Binding.oneWay('.parentView.inputViewLayout'),
        buttonLayoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        isTextAreaBinding: SC.Binding.oneWay('.parentView.isTextArea'),
        appendSelectionToInputBinding: SC.Binding.oneWay('.parentView.appendSelectionToInput'),

        showAddButtonBinding: SC.Binding.oneWay('.parentView.showAddButton'),
        searchSeparatorCharactersBinding: SC.Binding.oneWay('.parentView.searchSeparatorCharacters'),

        searchStringBinding: '.parentView.searchString',
        searchContextBinding: '.parentView.searchContext',
        addActionBinding: SC.Binding.oneWay('.parentView.addAction'),

        valueBinding: SC.Binding.from('.parentView.value'),

        parentViewHint: null,
        parentViewHintBinding: SC.Binding.oneWay('.parentView.hint'),

        // The hint defaults to the null title
        hint: function() {
            return this.get('parentViewHint') || (this.get('nullTitle') ?
                SC.String.loc(this.get('nullTitle')) : null);
        }.property('nullTitle', 'parentViewHint'),

        /***
         * Everything below here matches to the LabelSelectView interface
         */

        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        // The action to take when selecting an item, defaults to 'doPickSelection'
        selectionActionBinding: SC.Binding.oneWay('.parentView.selectionAction'),

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
        nullTitle: null,
        nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),
        maxHeightBinding: SC.Binding.oneWay('.parentView.maxHeight'),
        menuWidthBinding: SC.Binding.oneWay('.parentView.menuWidth'),
        iconBinding: SC.Binding.oneWay('.parentView.icon')
    })
});
