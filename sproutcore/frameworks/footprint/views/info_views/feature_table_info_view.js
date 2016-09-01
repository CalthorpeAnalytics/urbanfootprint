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

sc_require('views/info_views/table_info_view');
sc_require('views/query_export_view');

Footprint.FeatureTableInfoView = Footprint.TableInfoView.extend({
    classNames: 'footprint-query-info-results-view'.w(),
    childViews: ['titleView', 'sparseArrayProgressView', 'zoomToSelectionView', 'serverTableExportView', 'contentView', 'overlayView'],
    layout: {top: 125, bottom: .05, left: 0, right: 0.4},

    // TODO Revisions aren't enabled yet
    showRowDisclosureButton: YES,
    rowDisclosureButtonAction: 'toggleFeatureRevisions',

    layerSelection: null,
    layerSelectionStatus: null,
    layerSelectionStatusBinding: SC.Binding.oneWay('*layerSelection.status'),
    layerSelectionFeatureLength: null,
    // Enable the zoom to selection button
    zoomToSelectionIsVisible: YES,

    // The description of the items for the title property
    itemDescription: null,

    /***
     * Indicates if the items are loading or loaded, and how many are loaded.
     * The total shown is the total for the SC.SparseArray as well, not how many items of the SparseArray are loaded
     */
    title: function () {
        var layerSelectionFeatureLength = this.get('layerSelectionFeatureLength');
        return '%@ %@'.fmt(
            this.get('status') & SC.Record.READY || this.get('status') === SC.Record.EMPTY ?
                this.getPath('content.length') || 0 :
                layerSelectionFeatureLength ? 'Loading %@'.fmt(layerSelectionFeatureLength) : 'Loading',
            this.get('itemDescription')
        );
    }.property('content', 'status', 'itemDescription', 'layerSelectionFeatureLength').cacheable(),

    overlayStatus: function() {
        return Math.max(this.get('status'), this.get('layerSelectionStatus'));
    }.property('status', 'layerSelectionStatus').cacheable(),

    zoomToSelectionView: Footprint.ZoomToSelectionView.extend({
        classNames: 'footprint-table-infoview-zoom-to-selection-view'.w(),
        layout: { right: 150, width: 175, top: 4, height:24},
        isVisibleBinding: SC.Binding.oneWay('.parentView.zoomToSelectionIsVisible'),
        isEnabledBinding: SC.Binding.notZero('.parentView*layerSelection.features_count', NO),
        title: 'Zoom map to selection',
        action:'zoomToSelectionExtent',
        hint:'Zoom to the highlighted feature(s) in the table. You can highlight multiple rows by holding the shift key',
        toolTip:'Zoom to the highlighted feature(s) in the table. You can highlight multiple rows by holding the shift key'
    }),

    serverTableExportView: Footprint.QueryExportView.extend({
        classNames: 'footprint-table-info-export-button'.w(),
        layout: {height: 24, width: 100, right: 0.02, top: 4},
        contentBinding: SC.Binding.oneWay('.parentView.layerSelection'),
        action: 'doQueryResultExport',
        isSummaryBinding: SC.Binding.oneWay('.parentView.isSummary'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.READY)
    }),
    /***
     * Exports the table by dumping the dataset locally.
     * We don't use this anymore. We use serverTableExportView
     */
    localTableExportView: Footprint.QueryExportView.extend({
        classNames: 'footprint-table-info-export-button'.w(),
        layout: { height: 24, width: 100, right: 0.02, top: 4},
        contentBinding:SC.Binding.oneWay('.parentView.content'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        columns: null,
        columnsBinding: SC.Binding.oneWay('.parentView.columns'),
        formattedContent: null,
        formattedContentBinding: SC.Binding.oneWay('.parentView.formattedContent'),
        /***
         * This is what is exported. formattedContent won't be complete (if content is an SC.SparseArray)
         * until all records are loaded. That's why we call the special action doLoadRemainingAndExport
         */
        exportContent: function() {
            // Create a matrix whose first row is the column names
            // and each subsequent row is an item of the formattedContent
            var columns = this.get('columns');
            var formattedContent = this.get('formattedContent');
            if (!columns || !formattedContent)
                return;
            var columnValues = columns.map(function(column) {
                return column.get('valueKey');
            });
            return [columnValues].concat(formattedContent.map(function(obj) {
                return columnValues.map(function(columnValue) {
                    return obj.get(columnValue);
                }, this);
            }, this));
        }.property('columns', 'formattedContent').cacheable(),

        isLocalExport: YES,
        action: 'doRemainingAndExport',
        isReady: null,
        isReadyBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.READY),
        notLoadingSparseArray: null,
        notLoadingSparseArrayBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.READY_SPARSE_ARRAY_LOADING).not(),
        isEnabledBinding:SC.Binding.and('.isReady', '.notLoadingSparseArray')
    })
});
