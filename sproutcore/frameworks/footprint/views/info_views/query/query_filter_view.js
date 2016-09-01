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


sc_require('views/info_view');
sc_require('views/info_views/select_attribute_info_views');
sc_require('views/info_views/query/query_filter_info_view');
sc_require('views/remove_button_view');


/***
 * Adds the attributes of selected join tables
 */
Footprint.QueryFilterView = Footprint.SelectAttributeInfoView.extend({
    // In addition to the SelectOrAddView of the contentView,
    // we add a SelectOrAddView for three more lists
    childViews: ['contentView', 'attributesOverlayView', 'equalitySymbolsView', 'conjunctionsView'],
    classNames:['footprint-select-attribute-with-joins-info-view'],
    inputViewLayout: {bottom: 30},
    buttonLayout: {left: 20, bottom: 6, height: 16, width: 140},
    inputView: SC.outlet('contentView.inputView'),
    isTextArea: YES,
    appendSelectionToInput: YES,
    // Use all the SC.Query characters and the space bar and parens
    searchSeparatorCharacters: ['\\s+', '\\)', '\\('].concat(
        getKeys(removeKeys(SC.Query.create().get('queryLanguage'), ['$']))
    ),

    // If isSelectable is YES, set this to indicate what property of LayerSelection.query_strings should
    // be impacted by the selection. This property is included the context of the action
    queryStringsProperty: null,

    filteredItems: null,

    // Show this if the searchString doesn't match anything
    nullTitle: "Select attributes",
    nullTitleIfEmpty: "No matches",

    /***
     * Override to support multiple popups
     */
    removeMenu: function() {
//      TODO For SCAG pilot the categoricalValuesView has been removed
//      ['contentView.labelSelectView', 'equalitySymbolsView', 'categoricalValuesView', 'conjunctionsView'].forEach(function(view)
        ['contentView.labelSelectView', 'equalitySymbolsView', 'conjunctionsView'].forEach(function(view) {
            this.getPath(view).removeMenu();
        }, this);
    },

    /***
     * Override to support multiple popups.
     */
    handleDownKey: function() {
        // TODO Turning off 'AUTO COMPLETE' functionality for SCAG pilot
        return;

        // Iterate through our LabelSelectViews and enable the one that has a searchString
        // The logic on each view makes it that only 0 or 1 will match what the user is typing along with context
        // and thus only one will have a searchString assigned to it
        ['contentView.labelSelectView', 'equalitySymbolsView', 'categoricalValuesView', 'conjunctionsView'].forEach(function(view) {
            var labelSelectView = this.getPath(view);
            if (labelSelectView.get('matchesSearchClause')) {
                labelSelectView.makeMenuContentFirstResponder();
                labelSelectView.selectFirstMenuItem();
            }
            else {
                labelSelectView.removeMenu();
            }
        }, this);
    },

    /***
     * Monitors the loading of the joined TemplateFeature
     */
    attributesOverlayView: Footprint.OverlayView.extend({
        layout: {left: 0, bottom: 6, height: 16, width: 16},
        imageSize: 16,
        showOnBusyOnly: YES,
        statusBinding: SC.Binding.oneWay('Footprint.joinedTemplateFeaturesController.status')
    }),

    /***
     * Select an equality symbol. This popup will popup whenever we detect that the user
     * has just typed an attribute or primitive. Then we filter based on what the user
     * types (e.g. < will show < or <=)
     */
    equalitySymbolsView: Footprint.LabelSelectForTextInputView.extend({
        layout: {left: 175, bottom: 6, height: 16, width: 45},
        classNames: ['equality-symbols-view'],
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        controlSize: SC.SMALL_CONTROL_SIZE,
        // TODO, ignoring searchString for SCAG Pilot Release
        // contentBinding: SC.Binding.oneWay('Footprint.equalitySymbolsController.filteredItems'),
        contentBinding: SC.Binding.oneWay('Footprint.equalitySymbolsController.content'),

        searchContextBinding: SC.Binding.oneWay('.parentView.searchContext'),
        searchContextObserver: function() {
            var searchContext = this.get('searchContext');
            var tokenTree = searchContext.get('tokenTree');
            var tokenType = searchContext.get('tokenType');
            var searchString = searchContext.get('searchString') || '';
            var tokenTreeBeforeFragment = searchContext.get('tokenTreeBeforeFragment');
            var tokenTreeFragment = searchContext.get('tokenTreeFragment');
            // Set the searchString if we have an equality symbol
            // but we have no space at the end, which would indicate the user is done with the equality symbol
            if (tokenTree && Footprint.equalitySymbolsController.get('content').contains(tokenType) && (!searchString.match(/\s+$/))) {
                this.setIfChanged(
                    'searchString',
                    tokenType);
                this.set('matchesSearchClause', YES);
            }
            // Unparseable and fragment is a PROPERTY tokenType and there is the search string is whitespace
            else if (tokenTreeBeforeFragment && tokenTreeFragment && tokenTreeFragment['tokenType'] == 'PROPERTY' && searchString.match(/\s+$/)) {
                this.setIfChanged(
                    'searchString',
                    '');
                this.set('matchesSearchClause', YES);
            }
            // Unparseable and the previous tokenType was a property
            else if (tokenTreeBeforeFragment && tokenTreeFragment && tokenTreeBeforeFragment['tokenType'] == 'PROPERTY') {
                this.setIfChanged(
                    'searchString',
                    tokenTreeFragment['tokenValue']);
                this.set('matchesSearchClause', YES);
            }
            else {
                this.setIfChanged(
                    'searchString',
                    null);
                this.set('matchesSearchClause', NO);
            }
            this.propertyDidChange('matchesSearchClause');
        }.observes('.searchContext'),
        searchStringBinding: 'Footprint.equalitySymbolsController.searchString',

        menuWidth: 100,
        nullTitle: '=,<',
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        /***
         * When we hit enter on the menu give focus to the inputView
         */
        targetInputViewBinding: SC.Binding.oneWay('.parentView.inputView'),
        toolTip: 'The available equality and comparison operators',

        // This will append the item to the input field
        selectionAction: 'doPickSelection'
    }),

    // TODO, left out for SCAG Pilot Release
    categoricalValuesView: Footprint.LabelSelectForTextInputView.extend({
        layout: {left: 185, bottom: 6, height: 16, width: 80},
        classNames: ['categorical-values-view'],
        controlSize: SC.SMALL_CONTROL_SIZE,

        queryFeatureAttributeStatus: null,
        queryFeatureAttributeStatusBinding: SC.Binding.oneWay('Footprint.queryFeatureAttributeActiveController.status').matchesStatus(SC.Record.READY),
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '.queryFeatureAttributeStatus'),
        // TODO, ignoring searchString for SCAG Pilot Release
        // Footprint.queryFeatureAttributeActiveController.filteredItems'),
        contentBinding: SC.Binding.oneWay('Footprint.queryFeatureAttributeActiveController.content'),

        searchContextBinding: SC.Binding.oneWay('.parentView.searchContext'),
        // Set if an equality symbol was last typed and we have whitespace to indicate the user is
        // done with that symbol. Also set if the user is typing a string or number
        // and we have a FeatureAttribute
        searchContextObserver: function() {
            var searchContext = this.get('searchContext');
            var tokenTree = searchContext.get('tokenTree');
            var tokenType = searchContext.get('tokenType');
            var searchString = searchContext.get('searchString') || '';
            var featureAttribute = Footprint.queryFeatureAttributeActiveController.get('content');
            var tokenTreeBeforeFragment = searchContext.get('tokenTreeBeforeFragment');
            var tokenTreeFragment = searchContext.get('tokenTreeFragment');

            // FeatureAttribute exists and...

            // the last token is an equality symbol and searchString is whitespace
            if (featureAttribute && Footprint.equalitySymbolsController.get('content').contains(tokenType) && searchString.match(/\s+$/)) {
                this.setIfChanged(
                    'searchString',
                    '');
                this.set('matchesSearchClause', YES);
            }
            // tokenType is a string or number and a FeatureAttribute exists and we're not on to whitespace yet
            else if (featureAttribute && ['STRING', 'NUMBER'].contains(tokenType) && !searchString.match(/\s+$/)) {
                this.setIfChanged(
                    'searchString',
                    searchContext.get('searchString'));
                this.set('matchesSearchClause', YES);
            }
            // does not parse and last symbol is an equality symbol and searchString is whitespace
            else if (featureAttribute && tokenTreeBeforeFragment && tokenTreeFragment && Footprint.equalitySymbolsController.get('content').contains(tokenTreeFragment['tokenType']) && searchString.match(/\s+$/)) {
                this.setIfChanged(
                    'searchString',
                    '');
                this.set('matchesSearchClause', YES);
            }
            else {
                this.setIfChanged(
                    'searchString',
                    null);
                this.set('matchesSearchClause', NO);
            }
            this.propertyDidChange('matchesSearchClause');
        }.observes('.searchContext'),
        searchStringBinding: 'Footprint.queryFeatureAttributeActiveController.searchString',

        /***
         * Override to escape values that are strings
         * @param value
         * @returns {*}
         */
        escapeValueIfNeeded: function(value) {
            return typeof(value)=='string' ? "'%@'".fmt(value) : value;
        },

        showAddButton: NO,
        nullTitle: 'Values',
        itemTitleKeyBinding: SC.Binding.oneWay('.parentView.itemTitleKey'),
        selectionActionBinding: SC.Binding.oneWay('.parentView.selectionAction'),
        /***
         * When we hit enter on the menu give focus to the inputView
         */
        targetInputViewBinding: SC.Binding.oneWay('.parentView.inputView'),
        toolTip: 'The values already in the database for the last attribute in the query',
        // This will append the item to the input field
        selectionAction: 'doPickSelection'
    }),

    conjunctionsView: Footprint.LabelSelectForTextInputView.extend({
        layout: {left: 235, bottom: 6, height: 16, width: 60},
        classNames: ['conjunctions-view'],
        nullTitle: 'AND',
        controlSize: SC.SMALL_CONTROL_SIZE,
        // TODO, ignoring searchString for SCAG Pilot Release
        // contentBinding: SC.Binding.oneWay('Footprint.conjunctionsController.filteredItems'),
        contentBinding: SC.Binding.oneWay('Footprint.conjunctionsController.content'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

        searchContextBinding: SC.Binding.oneWay('.parentView.searchContext'),
        // Set if we have a conjunction token type
        searchContextObserver: function() {
            var searchContext = this.get('searchContext');
            var tokenTree = searchContext.get('tokenTree');
            var clause = searchContext.get('clause');
            var tokenValue = searchContext.get('tokenValue');
            var searchString = searchContext.get('searchString');
            var tokenTreeBeforeFragment = searchContext.get('tokenTreeBeforeFragment');
            var tokenTreeFragment = searchContext.get('tokenTreeFragment');
            // Parseable tree where tokenValue matches conjunction
            if (tokenValue &&
                Footprint.conjunctionsController.get('content').find(function (value) {
                    return value.indexOf(tokenValue) >= 0;
                })
            ) {
                this.setIfChanged(
                    'searchString',
                    tokenValue);
                this.set('matchesSearchClause', YES);
            }
            // Parseable tree with left and right side and searchString is whitespace
            else if (tokenTree && tokenTree['leftSide'] && tokenTree['rightSide'] && searchString.match(/\s+$/)) {
                this.setIfChanged(
                    'searchString',
                    '');
                this.set('matchesSearchClause', YES);
            }
            // Not parseable but previous tree has a left and right side
            else if (tokenTreeBeforeFragment && tokenTreeFragment && tokenTreeBeforeFragment['leftSide'] && tokenTreeBeforeFragment['rightSide']) {
                this.setIfChanged(
                    'searchString',
                    tokenTreeFragment['tokenValue']);
                this.set('matchesSearchClause', YES);
            }
            else {
                this.setIfChanged(
                    'searchString',
                    null);
                this.set('matchesSearchClause', NO);
            }
            this.propertyDidChange('matchesSearchClause');
        }.observes('.searchContext'),
        searchStringBinding: 'Footprint.conjunctionsController.searchString',

        /***
         * When we hit enter on the menu give focus to the inputView
         */
        targetInputViewBinding: SC.Binding.oneWay('.parentView.inputView'),
        toolTip: 'Use AND or OR to combine field tests. AND means that items on both sides of AND must be true to make the whole entity true. OR means either can be true to make the whole entity true. Or ( ) to group clauses like in a math formula.',
        // This will append the item to the input field
        selectionAction: 'doPickSelection'
    })
});
