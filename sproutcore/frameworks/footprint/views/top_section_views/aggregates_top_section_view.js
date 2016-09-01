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


Footprint.AggregatesTopSectionView =  SC.View.extend({

    childViews: ['queryContentView', 'tableContentView'],
    layerName: null,
    layerNameBinding: SC.Binding.oneWay('Footprint.layerActiveController.name'),
    title: function() {
        return 'Summarize Columns from %@'.fmt(this.get('layerName'));
    }.property('layerName'),

    // Toggle off to hide the summary fields (e.g. group by)
    showSummaryFields: YES,
    // TODO ideally these are in the declaration of the view subclass
    content:null,
    contentBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.content'),

    selection: null,
    selectionBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.selection'),
    recordType: null,
    recordTypeBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.recordType'),
    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),
    layerSelectionStatus: null,
    layerSelectionStatusBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.layerSelectionStatus'),
    // The formatted content actually shown by the table
    formattedContent: null,
    formattedContentBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.formattedContent'),
    columns: null,
    columnsBinding: SC.Binding.oneWay('Footprint.featureAggregatesTableController.columns'),
    summarySelection: null, // TODO always null for no
    status: null,
    statusBinding: SC.Binding.oneWay('*layerSelectionStatus'),
    isEnabled: function() {
        return (!(this.get('status') & SC.Record.BUSY)) && (this.get('layerSelectionStatus') & SC.Record.READY);
    }.property('layerSelectionStatus', 'status').cacheable(),

    queryContentView: SC.View.extend({
        classNames:'footprint-query-info-content-view'.w(),
        layout: {left: 0, width: 400},
        childViews:['titleView', 'aggregatesView', 'groupByView', 'joinColumnsView', 'constraintsInfoView',
            'joinStringLabelView', 'queryStringLabelView', 'clearSelectionButtonView', 'queryButtonView'],

        summaryContent: null,
        summaryContentBinding: '.parentView.summaryContent',

        layerSelection: null,
        layerSelectionBinding: '.parentView.layerSelection',

        showSummaryFields: null,
        showSummaryFieldsBinding: SC.Binding.oneWay('.parentView.showSummaryFields'),

        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

        title: null,
        titleBinding: '.parentView.title',

        recordType: null,
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),

        titleView: SC.LabelView.extend({
            classNames: "footprint-infoview-title-view".w(),
            layout: {left: 10, height: 24, top: 5},
            valueBinding: '.parentView.title'
        }),

        joinStringLabelView: SC.LabelView.extend({
            classNames: "footprint-editable-10font-bold-title-view".w(),
            layout: {left: 20, height: 16, top: 30, right: 105},
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView*layerSelection.joins'),
            value: function(){
                var filter_string = this.getPath('content');
                if (filter_string) {
                    return 'Join Table: %@'.fmt(filter_string)
                }
                else {
                    return 'No Join Tables'
                }
            }.property('content').cacheable()
        }),

        queryStringLabelView: SC.LabelView.extend({
            classNames: "footprint-editable-10font-bold-title-view".w(),
            layout: {left: 30, height: 16, top: 50, right: 105},
            constrainToBounds: null,
            constrainToBoundsBinding: SC.Binding.oneWay('.parentView*layerSelection.selection_options.constrain_to_bounds'),
            bounds: null,
            boundsBinding: SC.Binding.oneWay('.parentView*layerSelection.bounds.coordinates'),
            filterString: null,
            filterStringBinding: SC.Binding.oneWay('.parentView*layerSelection.query_strings.filter_string'),
            value: function(){
                var bounds = this.get('bounds');
                var constrainToBounds = this.get('constrainToBounds') && bounds && bounds.length > 0;
                var filterString = this.get('filterString');
                var conditions = [filterString, constrainToBounds ? 'Painted selection': null].compact();

                return 'Where: %@'.fmt(conditions.length > 0 ?
                    conditions.join(' and ') :
                    'Summarize all')
            }.property('filterString', 'bounds', 'constrainToBounds').cacheable()
        }),

       aggregatesView: Footprint.InfoView.extend({
            childViews:'titleView contentView RemoveButtonView joinColumnsView'.w(),
            classNames:'footprint-query-info-aggregates-view'.w(),
            layout: {left:10, top:75, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            title: 'Aggregates',
            toolTip: 'Enter aggregates (e.g. SUM(du), AVG(emp))',
            isVisibleBinding: SC.Binding.oneWay('.parentView.showSummaryFields'),
            contentBinding: '.parentView*layerSelection.query_strings',

            contentView: Footprint.EditableModelStringView.extend({
                classNames: ['footprint-editable-content-view'],
                layout: {left: 0.2, right:52},
                contentBinding: '.parentView.content',
                contentValueKey: 'aggregates_string',
                toolTip: 'Available aggregations queries: \n \n SUM(column_name): Sum column values \n AVG(column_name): Average of column values \n COUNT(column_name): Count of rows \n MAX(column_name): Maximum value in column \n MIN(column_name): Minimium value in column'
            }),
            joinColumnsView: Footprint.JoinColumnsInfoView.extend({
                layout: {right: 26, width: 24},
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                recordTypeBinding:SC.Binding.oneWay('.parentView.recordType'),
                contentBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.content'),
                selectionBinding: 'Footprint.availableFieldsWithJoinsController.selection',
                queryStringsProperty: 'aggregates_string'
            }),
            RemoveButtonView: Footprint.RemoveButtonView.extend({
                layout: {right: 0, width: 24},
                isVisibleBinding: SC.Binding.oneWay('.parentView*content.aggregates_string').bool(),
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                action: 'doClearAggregates'
            })
        }),

        groupByView: Footprint.InfoView.extend({
            childViews:'titleView contentView RemoveButtonView joinColumnsView'.w(),
            classNames:'footprint-query-info-group-by-view'.w(),
            layout: {left:10, top:105, height: 24},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            title: 'Group By',
            toolTip: 'Enter group-by columns of main or join table (e.g. blockgroup)',
            contentBinding: '.parentView*layerSelection.query_strings',
            isVisibleBinding: SC.Binding.oneWay('.parentView.showSummaryFields'),

            contentView: Footprint.EditableModelStringView.extend({
                classNames: ['footprint-editable-content-view'],
                layout: {left: 0.2, right:52},
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                contentBinding: '.parentView.content',
                contentValueKey: 'group_by_string'
            }),
            joinColumnsView: Footprint.JoinColumnsInfoView.extend({
                layout: {right: 26, width: 24},
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                recordTypeBinding:SC.Binding.oneWay('.parentView.recordType'),
                contentBinding: SC.Binding.oneWay('Footprint.availableFieldsWithJoinsController.content'),
                selectionBinding: 'Footprint.availableFieldsWithJoinsController.selection',
                queryStringsProperty: 'group_by_string'
            }),
            RemoveButtonView: Footprint.RemoveButtonView.extend({
                layout: {right: 0, width: 24},
                isVisibleBinding: SC.Binding.oneWay('.parentView*content.group_by_string').bool(),
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
                action: 'doClearGroupBy'
            })
        }),

        constraintsInfoView: Footprint.ConstraintsInfoView.extend({
            layout: {top:150, height: 40, left: 0, right: 130},
            contentBinding: '.parentView.layerSelection',
            // If filter or aggregates are specified, allow the user to
            // toggle between limiting to the geographic selection or not
            nonGeographicLimitationsExistBinding: SC.Binding.or(
                '*content.query_strings.filter_string',
                '*content.query_strings.aggregates_string'),
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
        }),

        clearSelectionButtonView: SC.ButtonView.design({
            classNames: ['footprint-query-info-clear-button-view', 'theme-button', 'theme-button-gold'],
            layout: {bottom: 10, right: 80, height: 20, width: 45},
            tableViewLayout:  {left: 0.01, right: 0.02, top: 30, bottom: 0},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            title: 'Clear',
            action: 'doClearSelection',
            // We pass the layerSelection content to the action
            contentBinding: '.parentView.content',
            toolTip: 'Clear Selection'
        }),

        queryButtonView: SC.ButtonView.design({
            classNames: ['footprint-query-info-query-button-view', 'theme-button', 'theme-button-green'],
            layout: {bottom: 10, right: 24, height: 20, width: 45},
            isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
            title: 'Query',
            action: 'doExecuteQuery',
            // We pass the layerSelection content to the action
            contentBinding: '.parentView.layerSelection',
            toolTip: 'Execute Query'
        })
    }),

    tableContentView: Footprint.FeatureTableInfoView.extend({
        classNames: "footprint-query-info-summary-results-view".w(),
        layout: {left: 400},
        // Indicates a summary view of the features for folks like the export button
        isSummary: YES,
        itemDescription: 'Feature Summary',
        tableViewLayout:  {left: 0.01, right: 0.02, top: 30, bottom: 0},
        parentOneWayBindings: [
            'content', 'formattedContent', 'columns', 'status',
            'selection', 'recordType', 'layerSelection'],

        // The overlay is visible if layerSelection status is BUSY
        overlayStatus: function() {
            return this.get('status');
        }.property('status').cacheable()
    })
});
