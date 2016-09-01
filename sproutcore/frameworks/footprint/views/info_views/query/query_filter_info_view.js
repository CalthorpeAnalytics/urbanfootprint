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

sc_require('views/info_views/query/query_filter_view');

Footprint.QueryFilterInfoView = Footprint.InfoView.extend({
    childViews:'queryFilterView removeButtonView'.w(),
    classNames:'footprint-query-filter-info-view'.w(),

    // Content should be set to the editable LayerSelection

    searchContext: null,

    /***
     * Presents the input view and drop downs of available attributes, equality symbols, conjunctions, and value ranges
     */
    queryFilterView: Footprint.QueryFilterView.extend({
        title: 'Filter',
        layout: {right: 20},
        hing: 'Enter query filter conditions from the available attributes',
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        // Bind to the filtered items so that the user's typing shortens the list
        // TODO Turning off 'AUTO COMPLETE' functionality for SCAG pilot
        //filteredItemsBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.filteredItems'),
        // contentBinding: SC.Binding.oneWay('*filteredItems.content'),
        filteredItemsBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.content'),
        contentBinding: SC.Binding.oneWay('*filteredItems'),
        selectionBinding: 'Footprint.availableFieldsWithJoinsController.selection',
        queryStringsProperty: 'filter_string',

        layerSelection: null,
        layerSelectionBinding: SC.Binding.oneWay('.parentView.content'),
        layerSelectionStatus: null,
        layerSelectionStatusBinding: SC.Binding.oneWay('.parentView*content.status'),

        /***
         *  Value property section
         **/

        topSectionIsVisible: null,
        topSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.topSectionIsVisible'),
        dataManagerIsVisible: null,
        dataManagerIsVisibleBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.content').equalsValue('query'),

        /***
         * Reset the value to its controller whenever the Query Manager opens
         */
        topSectionIsVisibleObserver: function() {
            var layerSelection = this.get('layerSelection');
            var layerSelectionStatus = this.get('layerSelectionStatus');
            var topSectionIsVisible = this.get('topSectionIsVisible');
            var dataManagerIsVisible = this.get('dataManagerIsVisible');
            if (this.get('layerSelection')) {
                // Only set the value if ready and this view is visible
                // TODO There shouldn't be any harm in setting the value when not visible, but
                // there was a side effect to it at one time, so verify the need for the latter two conditions.
                if ((this.getPath('layerSelection.status') & SC.Record.READY)  &&
                    this.get('topSectionIsVisible') &&
                    this.get('dataManagerIsVisible')) {

                    this.set('value', this.getPath('layerSelection.query_strings.filter_string'));
                }
            }
            else {
                // Clear the value if we have no LayerSelection, like in the background layer case
                this.set('value', null);

            }
        }.observes('.layerSelection', '*layerSelection.status', '.topSectionIsVisible', '.dataManagerIsVisible'),

        /***
         * Update the controller whenever the value changes
         */
        valueObserver: function() {
            Footprint.layerSelectionEditController.setPath('query_strings.filter_string', this.get('value'));
        }.observes('.value'),

        /*** End value property section ***/

        // The parsed searchContext of the queryString. Two way binding since the searchContext
        // is created here
        searchContextBinding: '.parentView.searchContext',
        /***
         * The view's controller's searchString should be set if
         * the right-most clause of the query is a property. It should also be set if
         * an AND or other conjunction or open paren was just entered and now we have whitespace
         */
        searchContextObserver: function() {
            var matchesProperty ='contentView.labelSelectView.matchesSearchClause';
            var searchContext = this.get('searchContext');
            if (!searchContext)
                return;
            var tokenTree = searchContext.get('tokenTree');
            var clause = searchContext.get('clause');
            var tokenType = searchContext.get('tokenType');
            var searchString = searchContext.get('searchString');
            var tokenTreeBeforeFragment = searchContext.get('tokenTreeBeforeFragment');
            var tokenTreeFragment = searchContext.get('tokenTreeFragment');
            var featureAttribute = Footprint.queryFeatureAttributeActiveController.get('content');
            // Doesn't parse and fragment with conjunction as the previous token tree value and no right hand side
            if (tokenTreeFragment && tokenTreeBeforeFragment && ['AND', 'OR', 'NOT', '('].contains(tokenTreeBeforeFragment['tokenValue']) && !tokenTreeBeforeFragment['rightSide']) {
                // Set an empty search string since the last token is an equality symbol
                Footprint.availableFieldsWithJoinsController.setIfChanged(
                    'searchString',
                    tokenTreeFragment['tokenValue']);
                this.setPath(matchesProperty, YES);
            }
            // Parses and tokenType is a property and no feature attribute
            // This doesn't handle the rare case of compare two properties to each other
            else if (!featureAttribute && clause && 'PROPERTY' == tokenType) {
                Footprint.availableFieldsWithJoinsController.setIfChanged(
                    'searchString',
                    searchContext.get('searchString'));
                this.setPath(matchesProperty, YES);
            }
            // Does not parse and fragment tokenType is a PROPERTY and tokenValue doesn't match conjunction (which looks like a property when incomplete)
            else if (tokenTreeBeforeFragment && tokenTreeFragment && tokenTreeFragment['tokenType'] == 'PROPERTY' &&
                !Footprint.conjunctionsController.get('content').find(function(conjunction) {
                    return conjunction.indexOf(tokenTreeFragment['tokenValue']) == 0;
                })) {
                Footprint.availableFieldsWithJoinsController.setIfChanged(
                    'searchString',
                    tokenTreeFragment['tokenType']);
                this.setPath(matchesProperty, YES);
            }
            else {
                Footprint.availableFieldsWithJoinsController.setIfChanged(
                    'searchString',
                    null);
                this.setPath(matchesProperty, NO);
            }
            this.propertyDidChange(matchesProperty);
        }.observes('.searchContext')
    }),

    /***
     * Clears the query filter_string along with the LayerSelection's filter property
     */
    removeButtonView: Footprint.RemoveButtonView.extend({
        layout: {width: 10, height: 11, right: 6},
        classNames:['footprint-remove-button-view'],
        isVisibleBinding: SC.Binding.oneWay('.parentView*content.query_strings.filter_string').bool(),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        action: 'doClearFilter'
    })
});
