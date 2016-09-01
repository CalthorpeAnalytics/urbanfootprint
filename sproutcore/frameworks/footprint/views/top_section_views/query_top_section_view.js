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



sc_require('views/info_views/query/query_info_view');
sc_require('views/info_views/query/constraints_info_view');
sc_require('views/info_views/query/join_columns_info_view');
sc_require('views/info_views/select_attribute_info_views');
sc_require('views/info_views/query/query_filter_info_view');

Footprint.QueryTopSectionView = SC.View.extend({

    classNames: ['query-top-section-view'],
    childViews: ['queryContentView', 'tableContentView'],
    layerName: null,
    layerNameBinding: SC.Binding.oneWay('Footprint.layerActiveController.name'),
    title: function() {
        return 'Select features from %@'.fmt(this.get('layerName'));
    }.property('layerName'),
    // Toggle off to hide the summary fields (e.g. group by)
    showSummaryFields: YES,
    // We use the edit controller so the table updates as the user edits
    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.featureTableController.content'),
    // The formatted content actually shown by the table
    formattedContent: null,
    formattedContentBinding: SC.Binding.oneWay('Footprint.featureTableController.formattedContent'),
    // The columns to use for the result table
    columns: null,
    columnsBinding: SC.Binding.oneWay('Footprint.featureTableController.columns'),
    // Use the active controller here so that the table doesn't refresh when we commit edits
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.featureTableController.status'),
    selection: null,
    selectionBinding: SC.Binding.from('Footprint.featureTableController.selection'),
    recordType: null,
    recordTypeBinding: SC.Binding.oneWay('Footprint.featureTableController.recordType'),
    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),
    layerSelectionStatus: null,
    layerSelectionStatusBinding: SC.Binding.oneWay('Footprint.featureTableController.layerSelectionStatus'),

    searchContext: null,
    searchContextBinding: 'Footprint.availableFieldsWithJoinsController.searchContext',

    isEnabled: function() {
        return (!(this.get('status') & SC.Record.BUSY)) && (this.get('layerSelectionStatus') & SC.Record.READY);
    }.property('layerSelectionStatus', 'status').cacheable(),

    queryContentView: SC.View.extend({
        classNames:'footprint-query-content-view'.w(),
        layout: {left: 10, width: 390},
        childViews:['constraintsInfoView', 'titleView', 'filterView', 'joinView', 'outOfSyncLabelView', 'clearSelectionButtonView', 'queryButtonView'], // , 'revisionHistoryButtonView'

        content: null,
        contentBinding: '.parentView.content',

        layerSelection: null,
        layerSelectionBinding: '.parentView.layerSelection',

        showSummaryFieldsBinding: SC.Binding.oneWay('.parentView.showSummaryFields'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        title: null,
        titleBinding: '.parentView.title',

        recordType: null,
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),

        selection: null,
        selectionBinding: SC.Binding.oneWay('.parentView.selection'),

        searchContext: null,
        searchContextBinding: '.parentView.searchContext',

        titleView: SC.LabelView.extend({
            classNames: 'footprint-infoview-title-view'.w(),
            layout: {left: 0, height: 24, top: 5},
            valueBinding: '.parentView.title'
        }),

        /***
         * Presents the filter input and accompanying dropdowns
         */
        filterView: Footprint.QueryFilterInfoView.extend({
            layout: {top:30, height: 90},
            contentBinding: '.parentView.layerSelection',
            searchContextBinding: '.parentView.searchContext',
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        }),

        joinView: Footprint.QueryJoinInfoView.extend({
            layout: {top: 130, height: 24, right: 140},
            contentBinding: SC.Binding.oneWay('Footprint.joinLayersController.arrangedObjects'),
            // Make the menuWidth wider than the button to fit long names
            menuWidth: 300,
            // The status is based on the controller tracking content items--content itself has no status
            statusBinding: SC.Binding.oneWay('Footprint.joinLayersController.status'),
            selectionBinding: 'Footprint.joinLayersController.selection',
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        }),

        outOfSyncLabelView: Footprint.LabelView.extend({
            layout: {top: 124, height: 32, width: 130, right: 0 },
            classNames: ['footprint-out-of-sync-label-view'],
            displayProperties: ['isVisible'],

            submitIsEnabled: null,
            submitIsEnabledBinding: SC.Binding.oneWay('.parentView.queryButtonView.isEnabled'),

            constrainActiveLayerToQuery: null,
            constrainActiveLayerToQueryBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController*selection_options.constrain_to_query'),
            constrainEditLayerToQuery: null,
            constrainEditLayerToQueryBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController*selection_options.constrain_to_query'),

            queryFilterViewValue: null,
            // Binding this simply doesn't work
            queryFilterViewValueObserver: function() {
                this.setIfChanged('queryFilterViewValue', Footprint.layerSelectionEditController.getPath('query_strings.filter_string'));
            }.observes('Footprint.layerSelectionEditController*query_strings.filter_string'),

            /***
             * Returns YES if and only if the query results were created with data manager hidden, meaning they
             * were created by dragging a shape on the map, and now the data manager is visible.
             * This lets us tell the user to resubmit the query to get filtered results
             */
            isVisible: function() {
                return this.get('submitIsEnabled') && !this.get('constrainActiveLayerToQuery') && this.get('constrainEditLayerToQuery')
                    && this.get('queryFilterViewValue');
            }.property('submitIsEnabled', 'constrainActiveLayerToQuery', 'constrainEditLayerToQuery', 'queryFilterViewValue'),

            value: 'Results are not filtered. Click Query to filter.'
        }),

        constraintsInfoView: Footprint.ConstraintsInfoView.extend({
            layout: {top:160, height: 30, left: 0, right: 135},
            contentBinding: '.parentView.layerSelection',
            // If filter or joins are specified, allow the user to
            // toggle between limiting to the geographic selection or not
            nonGeographicLimitationsExistBinding: SC.Binding.or(
                '*content.query_strings.filter_string',
                '*content.joins.firstObject'),
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        }),


        clearSelectionButtonView: SC.ButtonView.design({
            classNames: ['footprint-query-info-clear-button-view', 'theme-button', 'theme-button-gold'],
            layout: {bottom: 10, right: 70, height: 24, width: 50},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            title: 'Clear',
            action: 'doClearSelection',
            // We pass the layerSelection content to the action
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            toolTip: 'Clear Selection'
        }),

        queryButtonView: SC.ButtonView.design({
            classNames: ['footprint-query-info-query-button-view', 'theme-button', 'theme-button-green'],
            layout: {bottom: 10, right: 10, height: 24, width: 50},
            searchContext: null,
            searchContextBinding: SC.Binding.oneWay('.parentView.searchContext'),
            // Only enabled if the tokenTree exists, meaning the query parses
            isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '*searchContext.tokenTree').bool(),
            title: 'Query',
            action: 'doExecuteQuery',
            // We pass the layerSelection content to the action
            contentBinding: '.parentView.content',
            toolTip: 'Execute Query'
        })
    }),

    tableContentView: Footprint.FeatureTableInfoView.extend({
        tableViewLayout:  {left: 0.01, right: 0.02, top: 30, bottom: 0},
        layout: {left: 400},
        itemDescription: 'Query/Selection Results',
        layerSelectionFeatureLengthBinding: SC.Binding.oneWay('*layerSelection.features_count'),
        parentOneWayBindings: [
            'content', 'formattedContent', 'columns', 'status', 'recordType', 'layerSelection'],
        selectionBinding: '.parentView.selection'
    })
});
