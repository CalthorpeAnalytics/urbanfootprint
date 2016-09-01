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
sc_require('views/overlay_view');
sc_require('views/updating_overlay_view');
sc_require('views/progress_overlay_view');
sc_require('views/info_views/zoom_to_selection_info_view');

Footprint.TableInfoView = Footprint.InfoView.extend({
    classNames: ['footprint-table-info-view'],
    childViews: ['titleView', 'sparseArrayProgressView', 'contentView', 'overlayView'],
    layout: {height: 150},
    // YES if displaying summary query results
    isSummary: NO,
    /**
     * Required. The formatted content used by the TableDelegate to render a cell.
     * This could be equal to content, but content is unformatted records that are
     * possibly backed by an SC.SparseArray. formattedContent only supplies content
     * for rows that have been loaded in the SparseArray.
    */
    formattedContent: null,
    /**
     * Required. The formatted columns of the table
     */
    columns: null,
    /***
     * Required. The status of the content
     */
    status:null,
    /***
     * Optional. The selected row(s)
     */
    selection: null,
    /***
     * Optional. The recordType of the content
     */
    recordType: null,
    /***
     * Optional. If the content is based on a Footprint.LayerSelection, set it here
     */
    layerSelection: null,

    /***
     * The row count
     */
    count: null,

    /***
     * The title of the table
     */
    title: null,

    // Set this to the status that should make the overlay visible if the status is BUSY
    overlayStatus: null,
    // The layout of the title for the table
    titleViewLayout: {left: 0.01, height: 16, width: 250, top: 8},
    // The layout of the TableView. Required, default {}
    tableViewLayout: {},
    // Allows multiple selection on the table unless disabled
    allowsMultipleSelection: YES,
    // Set to YES to show a disclosure button next to the left of each row
    showRowDisclosureButton: NO,
    // The action of the disclosure button if shown. The context of this button
    // will contain the row content as 'content'
    rowDisclosureButtonAction: 'toggleFeatureRevisions',
    // Only show the overlay if the status is busy. If you set this to NO, the overlay will show when
    // the status is not ready
    showOnBusyOnly: YES,

    // This full overlay is visible if either feature of layerSelection status is BUSY
    overlayView: Footprint.OverlayView.extend({
        layout: {left: 0.01, right: 0.02, top: 30},
        contentBinding:SC.Binding.oneWay('.parentView.content'),
        statusBinding:SC.Binding.oneWay('.parentView.overlayStatus'),
        // This stops the overlay view being visible when the content is empty
        showOnBusyOnly: SC.Binding.oneWay('.parentView.showOnBusyOnly')
    }),

    /***
     * The title of the table. This should show how many results
     * there are and possibly indicate when loading.
     */
    titleView: SC.LabelView.extend({
        classNames: 'footprint-infoview-title-view'.w(),
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        valueBinding: '.parentView.title'
    }),

    /**
     * Manages loading of records if the underlying content uses an SC.SparseArray
     */
    sparseArrayProgressView: SC.View.extend({
        childViews: ['updatingOverlayView', 'progressOverlayView', 'loadRemainingResultsButtonView'],
        classNames: 'sparse-array-progress-view',
        layout: {left:260, right:300, height: 28},

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),

        // The following are used if the content is using an SC.SparseArray
        sparseArray: null,
        sparseArrayBinding: SC.Binding.oneWay('*content.storeKeys').allowIfKindOf(SC.SparseArray),

        // Only show this view if there is a SparseArray
        isVisibleBinding: SC.Binding.oneWay('.sparseArray'),

        // The progress
        progress: null,
        progressBinding: SC.Binding.oneWay('*sparseArray.portionLoaded'),

        // Indicates that no all SparseArray indexes have loaded
        sparseArrayNotComplete: null,
        sparseArrayNotCompleteBinding: SC.Binding.oneWay('.progress').equalTo(1).not(),

        /***
         * Shows a spinner when SparseArrayContent is loading.
         * This is only shown when the user hasn't clicked the button
         * to incrementally download all features. In that case
         * the progressView will show instead
         */
        updatingOverlayView: Footprint.UpdatingOverlayView.extend({
            layout: {left: 0, width: 35, height: 25, top: 4},
            statusBinding: SC.Binding.oneWay('.parentView.status'),
            isOverlayVisibleBinding: SC.Binding.oneWay('.status').equalsStatus(SC.Record.READY_SPARSE_ARRAY_ADDING)
        }),
        /***
         * This button appears to allow the user to load all results if a SparseArray is in use.
         * Clicking this button will incrementally load all results and turn on the progressOverlayView
         */
        loadRemainingResultsButtonView: SC.ButtonView.extend({
            classNames: ['footprint-load-all-results-button-view'],
            layout: {left: 40, width: 125, top: 4, height: 24},
            title: 'Background load',
            toolTip: 'Rows are loaded by scrolling. Click to load all rows in the background',
            action: 'doLoadRemaining',
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            statusBinding: SC.Binding.oneWay('.parentView.status'),
            // Indicates that the SparseArray is not in the process of loading all indexes
            isReadyClean: null,
            isReadyCleanBinding: SC.Binding.oneWay('.status').equalsStatus(SC.Record.READY_CLEAN),
            isReadyCleanAndNotCompleted: null,
            isReadyCleanAndNotCompletedBinding:SC.Binding.and('.parentView.sparseArrayNotComplete', '.isReadyClean'),
            // Only visible if the SparseArray has not loaded everything and is not in the process of doing so
            isVisibleBinding: SC.Binding.oneWay('.parentView.sparseArrayNotComplete'),
            isEnabledBinding: SC.Binding.and('.parentView.isEnabled','.isReadyCleanAndNotCompleted')
        }),

        /***
         * Used to indicate a continuous incremental download of all records.
         * This is also used for exporting of features (see feature_table_info_view.js)
         */
        progressOverlayView: Footprint.ProgressOverlayView.extend({
            layout: {left: 170, height: 16, width: 100, top: 8},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            statusBinding: SC.Binding.oneWay('.parentView.status'),
            progressBinding: SC.Binding.oneWay('.parentView.progress'),
            sparseArrayContinuous: null,
            sparseArrayContinuousBinding: SC.Binding.oneWay('.status').matchesStatus(SC.Record.READY_SPARSE_ARRAY_CONTINUOUS),
            isOverlayVisibleBinding: SC.Binding.oneWay('.sparseArrayContinuous', '.parentView.sparseArrayNotComplete')
        })
    }),


    /****
     * The table is bound to the Footprint.featureTableController, which does the work
     * of converting the raw Records to SC.Objects that contain mapped attributes
     * that we actually want to show in the table.
     */
    contentView: SCTable.TableView.design({
        layoutBinding: SC.Binding.oneWay('.parentView.tableViewLayout'),

        displayProperties: ['formattedContent'],
        tableRowDisplayProperties: ['parentView.formattedContent'],

        createTableRowView: function() {
            return SCTable.TableRowView.extend({
                formattedContent: null,
                formattedContentBinding: SC.Binding.from('formattedContent', this),
                displayProperties: ['formattedContent'],
                shouldHighlightRowOnMouseOver: this.get('shouldHighlightRowOnMouseOver')
            });
        },

        allowsMultipleSelectionBinding: SC.Binding.oneWay('.parentView.allowsMultipleSelection'),

        // The content backed by an SC.SparseArray
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        // The content accessed by the TableDelegate to render each cell
        formattedContent: null,
        formattedContentBinding: SC.Binding.oneWay('.parentView.formattedContent'),
        columnsBinding: SC.Binding.oneWay('.parentView.columns'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        selection: null,
        selectionBinding: '.parentView.selection',
        recordType: null,
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        layerSelection: null,
        layerSelectionBinding: SC.Binding.oneWay('.parentView.layerSelection'),

        /***
         * Override the renderTableCellContent (from the SC.TableDelegate) so that we can
         * map some column values to more readable things. This is especially true of
         * association relationships when we want a friendly toString version of the association
         * @param tableView
         * @param renderContext
         * @param rowContent
         * @param rowIndex
         * @param column
         * @param columnIndex
         * @returns {*}
         */
        renderTableCellContent: function(tableView, renderContext, rowContent, rowIndex, column, columnIndex) {
            var formattedContent = this.get('formattedContent');
            var formattedRowContent = rowContent && formattedContent && formattedContent.get(rowIndex);

            var columnContent = String(
                    formattedRowContent ?
                        formattedRowContent.get(column.get('valueKey')):
                        columnIndex==0 ? 'Loading...' : '');

            // Right align numbers, except for id
            var divClass  = 'text';
            var spanClass = '';
            if (!isNaN(columnContent) && (column.get('valueKey') !== 'id')) {
                divClass  = 'numeric';
                spanClass = 'numeric-content';
            }

            return renderContext.push('<div class="%@"><span class="%@">%@</span></div>'.fmt(
                divClass,
                spanClass,
                SC.RenderContext.escapeHTML(columnContent)));
        },

        // TODO disclosure not yet implemented
        // Set to YES to show a disclosure button next to the left of each row
        showRowDisclosureButton: SC.Binding.oneWay('.parentView.showRowDisclosureButton'),
        // The action of the disclosure button if shown. The context of this button
        // will contain the row content as 'content'
        rowDisclosureButtonAction: SC.Binding.oneWay('.parentView.rowDisclosureButtonAction')
    })
});
