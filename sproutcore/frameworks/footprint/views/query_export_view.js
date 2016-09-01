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


Footprint.QueryExportView = SC.View.extend({
    classNames: ['footprint-query-export-view'],
    childViews: ['exportButtonView'],
    // The raw content
    // For local exports this is a list of features (no longer used)
    // For server exports this is a LayerSelection instance
    content: null,
    // For local exports only. The final content to export
    exportContent: null,
    // For local exports only. The record type for the table name
    recordType: null,
    // Default NO. For server exports only. Indicates summary query results are desired
    isSummary: NO,

    /***
     * Always export from the server
     */
    isLocalExport: NO,
    action: 'doQueryResultExport',

    exportButtonView: SC.ButtonView.extend({
        classNames: ['footprint-export-button-view'],
        layout: {width:100, right:0},
        title: 'Export as CSV',
        isLocalExport: null,
        isLocalExportBinding: SC.Binding.oneWay('.parentView.isLocalExport'),
        actionBinding: SC.Binding.oneWay('.parentView.action'),
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        exportContent: null,
        exportContentBinding: SC.Binding.oneWay('.parentView.exportContent'),
        recordType: null,
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        isSummary: null,
        isSummaryBinding: SC.Binding.oneWay('.parentView.isSummary'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    })
});
