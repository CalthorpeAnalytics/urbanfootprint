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

sc_require('views/item_views/label_select_for_text_input_view');
sc_require('views/item_views/select_or_add_input_view');

Footprint.SelectOrAddView = SC.View.extend({
    layout: {height: 24},
    classNames: ['footprint-select-or-add-view'],
    childViews: ['inputView', 'labelSelectView', 'addButtonView'],

    /***
     * The add button is optional since selecting can be enough by itself
     */
    showAddButton: YES,

    /***
     * The menu width when the popup opens
     */
    menuWidth: 150,

    /***
     * The layout of the inputView. By default it is right of the labelSelectView
     */
    inputViewLayout: {right: 66},

    /***
     * The layout of the popup button
     */
    buttonLayout: { right: 34, width: 30, centerY: 0, height: 18 },

    /***
     * The layout of the addButtonView if visible
     */
    addButtonLayout: {right: 0, width: 30, centerY: 0, height: 18},

    /***
     * If true make the inputView a text area instead of a single line
     */
    isTestArea: NO,

    /***
     * Normally the selected item replaces the input value. Set this to true to append
     * to the input value. If true the search string is only set to the portion of the
     * value after the last space or whatever is specified in searchSeparatorCharacters
     */
    appendSelectionToInput: NO,
    /***
     * If appendSelectionToInput is YES, these regex character expressions are used to to identify
     * what the current search string of the entire input value is. The search string
     * is always after the last of these characters if any exist, or the whole value
     * if they don't
     */
    searchSeparatorCharacters: ['\s+'],

    /***
     * The available items to choose from. If this content comes from a Footprint.SearchFilterMixin
     * controller, you can two-way bind searchString to the controller's searchString to make
     * the controller filter this content based on the searchString. The Footprint.SearchFilterMixin
     * specifies what property/ies the searchString searches
     */
    content: null,

    /***
     * The current value of the inputView
     */
    value: null,

    /***
     * A special setter used by the dropdown menu so that setting of the underlying value
     * is done more surgically by replacing the fragment of value that the menu item is matching
     */
    valueForMenu: null,

    /***
     * The current selection among the content. This can be empty if menu isn't open
     */
    selection: null,
    /**
     * The search string that filters the available content
     **/
    searchString: null,
    /**
     * The search context. See explanation below.
     **/
    searchContext: null,

    searchRegex: function() {
        if (this.get('appendSelectionToInput')) {
            // Look for anything after the last separator if one exists
            return new RegExp('.*(%@)(.*)'.fmt(this.get('searchSeparatorCharacters').join('|')));
        }
        return null;
    }.property('appendSelectionToInput', 'searchSeparatorCharacters').cacheable(),

    /***
     * Matches the last fragment after a whitespace
     */
    searchFragmentRegex: function() {
        return new RegExp('([^\s]+)$');
    }.property().cacheable(),

    /***
     * Either the portion of value after the last searchSeparatorCharacter
     * or the whole value. This is used to set the searchString or replace the portion
     * of value with a selected item. Returns a function that expects the current value
     */
    createSearchContext: function(value) {
        var tokenTree = Footprint.processQuery(value);
        var clause, searchString, tokenType;
        if (tokenTree) {
            // Get the clause furthest to the right side of the string
            // This will have
            clause = rightSideClause(tokenTree, null, -1);
            // If trailing whitespace, that is our search string. Otherwise it's the clause's token value
            var whitespaceMatch = (value || '').match(/(\s+)$/);
            searchString = (whitespaceMatch && whitespaceMatch[1]) || (clause && clause['tokenValue']);
            tokenType = clause && clause['tokenType'];
        }
        // If parsing fails we'll have a tree. The first element is the tree of what has parsed and the second
        // is the fragment that didn't parse
        var tree = clause && clause['tree'] && clause['tree'].isEnumerable ? clause['tree'] : null;
        return SC.Object.create({
            full: value,
            tokenTree: tokenTree && !tokenTree.error ? tokenTree : null,
            clause: clause,
            searchString: searchString,
            tokenType: tokenType,
            // These two values are set upon experiencing a parsing error
            tokenTreeBeforeFragment: tree && tree.slice(-2)[0],
            tokenTreeFragment: tree && tree.slice(-1)[0]
        });
    },

    /***
     * Called by the inputView to remove the popup menu. Delegate to labelSelectView
     */
    removeMenu: function() {
        this.get('labelSelectView').removeMenu();
    },

    /***
     * Called by the inputView when the DOWN key is pressed, meaning the user wants
     * to select something from the popup menu
     */
    handleDownKey: function() {
        var labelSelectView = this.get('labelSelectView');
        labelSelectView.makeMenuContentFirstResponder();
        labelSelectView.selectFirstMenuItem();
    },

    /***
     * The key that represents each item's title
     */
    itemTitleKey: null,

    /***
     * The title of the null item. This defaults to an empty string for the case when search removes all items
     */
    nullTitle: '',
    /***
     * The null title to use if no items are available
     */
    nullTitleIfEmpty: '',
    /***
     * Adds an item to the list to show as the default item when nothing is selected
     */
    includeNullItem: NO,
    /***
     * Whether to show the null item if the list is empty
     */
    includeNullItemIfEmpty: YES,
    /***
     * The default icon. Set null if no icon is needed
     */
    icon: sc_static('images/section_toolbars/pulldown.png'),

    /***
     * The name of the action to call when adding an item to the list
     */
    addAction: null,

    /***
     * Call doPickSelection on this whenever an item is picked from the dropdown.
     */
    selectionAction: 'doPickSelection',
    selectionTarget: function() { return this;}.property().cacheable(), // TODO should be able to do with an outlet
    actOnSelect: YES,

    /***
     * If the labelSelectView currently has focus we set our value to it
     * instead of the search string. Once the user restores focus to us
     * we restore the value to _typedString unless it was nulled by the
     * user actually clicking something in the list or hitting enter
     *
     * @param context: The popup view whose selection changed. Normally the labelSelectView
     */
    doPickSelection: function(context) {
        var selectedItem = context.get('selectedItem');
        if (selectedItem)
            this.get('inputView').setIfChanged('value', selectedItem);
    },


    /***
     * By default show the nullTitle if it exists for a hint
     */
    hint: function() {
        if (this.get('nullTitle'))
            return SC.String.loc(this.get('nullTitle'));
        return null;
    }.property('nullTitle').cacheable(),

    /***
     * The text input that receives selections from the LabelSelectView
     * It might set or append the value received
     */
    inputView: Footprint.SelectOrAddInputView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.inputViewLayout'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        appendSelectionToInputBinding: SC.Binding.oneWay('.parentView.appendSelectionToInput'),
        labelSelectViewBinding: SC.Binding.oneWay('.parentView.labelSelectView'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        searchStringBinding: '.parentView.searchString',
        searchContextBinding: '.parentView.searchContext',
        addActionBinding: SC.Binding.oneWay('.parentView.addAction'),
        hintBinding: SC.Binding.oneWay('.parent.hint'),
        selectedItemBinding: SC.Binding.oneWay('.labelSelectView.selectedItem'),
        selectedItemValueBinding: SC.Binding.oneWay('.labelSelectView.selectedItemValue'),
        valueBinding: SC.Binding.from('.parentView.value'),
        isTextAreaBinding: SC.Binding.oneWay('.parentView.isTextArea')
    }),

    /***
     * Select an existing item to add to the content. When the user types into the text input
     * we filter this list based on what they type
     */
    labelSelectView: Footprint.LabelSelectForTextInputView.extend({
        controlSize: SC.SMALL_CONTROL_SIZE,
        layoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        menuWidthBinding: SC.Binding.oneWay('.parentView.menuWidth'),
        includeNullItemIfEmptyBinding:SC.Binding.oneWay('.parentView.includeNullTitleIfEmpty'),
        nullTitleBinding: SC.Binding.oneWay('.parentView.nullTitle'),
        nullTitleIfEmptyBinding: SC.Binding.oneWay('.parentView.nullTitleIfEmpty'),
        iconBinding: SC.Binding.oneWay('.parentView.icon'),
        selectionBinding: '.parentView.selection',
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        selectionActionBinding: SC.Binding.oneWay('.parentView.selectionAction'),
        selectionTargetBinding: SC.Binding.oneWay('.parentView.selectionTarget'),
        searchContextBinding: SC.Binding.oneWay('.parentView.searchContext'),
        searchStringBinding: SC.Binding.oneWay('*searchContext.searchString'),
        /***
         * When we hit enter on the menu give focus to the inputView
         */
        targetInputViewBinding: SC.Binding.oneWay('.parentView.inputView')
    }),

    addButtonView: Footprint.AddButtonView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.addButtonLayout'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.showAddButton'),
        value: null,
        valueBinding: SC.Binding.oneWay('.parentView.inputView.value'),
        valueInItems: null,
        // Only allow adding of items typed in by the user or selected and put in the input box
        isEnabledBinding: SC.Binding.oneWay('.parentView.inputView.value').bool(),
        actionBinding: SC.Binding.oneWay('.parentView.addAction')
    })
});
