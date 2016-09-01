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


sc_require('views/info_views/analysis_module_running_view');

Footprint.AnalysisModuleView = SC.View.extend({
    classNames: "footprint-manage-module-view".w(),
    childViews: ['executeModuleView', 'exportSummaryTableButtonView', 'analysisModuleStatusView'],
    layout: {height: 120},
    title: null,
    titleBinding: SC.Binding.oneWay('.parentView.title'),
    editAssumptionsAction: null,
    editAssumptionsActionBinding: SC.Binding.oneWay('.parentView.editAssumptionsAction'),

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.resultSummaryTableController.content'),
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.resultSummaryTableController.resultLibraryStatus'),

    isExportVisible: function() {
        var isEnabled = NO;
        if (this.get('content') && this.getPath('content.query')) {
            if (this.getPath('content.query').length > 1) {
                isEnabled = YES;
            }
        }
        return isEnabled;
    }.property('content', 'status').cacheable(),

    executeModuleView: SC.ButtonView.extend({
        layout: { left: 15, height: 28, top:15, width: 90 },
        classNames: ['theme-button', 'theme-button-blue', 'theme-button-short'],
        title: 'Run Module',
        action: 'doUpdateAnalysisModule'
    }),

    exportSummaryTableButtonView: SC.ButtonView.design({
        classNames: ['footprint-query-info-query-button-view', 'theme-button', 'theme-button-gold'],
        layout: {top: 19, left: 120, height: 20, width: 100},
        isVisibleBinding: SC.Binding.oneWay('.parentView.isExportVisible'),
        title: 'Export Summary',
        action: 'doResultTableExport',
        contentBinding: '.parentView.content',
        toolTip: 'Export Summary Table'
    }),

    analysisModuleStatusView: SC.View.extend({
        classNames:['footprint-analysis-module-status-view'],
        childViews: ['moduleLabelView', 'analysisModuleRunningView'],
        layout: {bottom: 5, left: 5, right: 30, height: 60},
        backgroundColor: 'lightgrey',
        content: null,
        contentBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController*selection.firstObject.analysis_tools.firstObject'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController.status'),

        moduleLabelView: SC.LabelView.extend({
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView*content.updated'),
            value: function() {
                if (this.get('content')) {
                    return 'Last Updated: %@'.fmt(this.getPath('content'))
                }
                else {
                    return 'Content Loading...'
                }
            }.property('content', 'contentStatus').cacheable(),
            layout: {height: 20, left: 5, top: 5, right: 20}
        }),

        analysisModuleRunningView: Footprint.AnalysisModuleRunningView.extend({
            backgroundColor: '#ff6666',
            enabledLayout: {top: 0, left: 0},
            content: null,
            contentBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController*selection.firstObject')
        })
    })
});
