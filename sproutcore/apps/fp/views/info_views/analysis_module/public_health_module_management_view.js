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


sc_require('views/info_views/analysis_module/label_result_views');
sc_require('views/info_views/analysis_module/analysis_module_view');

Footprint.PublicHealthModuleManagementView = SC.View.extend({

    classNames: "footprint-public-health-module-management-view".w(),
    childViews: ['manageModuleView', 'moduleResultsView', 'exportSummaryTableButtonView', 'outcomesTableView'],

    allResultsStatus: null,
    allResults: null,

    title: 'Public Health Module',

    analysisModule: null,
    analysisModuleBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController*selection.firstObject'),

    allResultsBinding: SC.Binding.oneWay('Footprint.resultsController.content'),
    allResultsStatusBinding: SC.Binding.oneWay('Footprint.resultsController.status'),

    content: function () {
        if (this.get('allResultsStatus') & SC.Record.READY)
            var content = this.get('allResults').filter(function (result) {
                return result.getPath('db_entity.key') == 'result__ph_outcomes_table';
            });
            if (content)
                return content[0];
    }.property('allResults', 'allResultsStatus').cacheable(),

    contentFirstObject: null,
    contentFirstObjectBinding : SC.Binding.oneWay('*content.firstObject'),

    manageModuleView: Footprint.AnalysisModuleView,

    moduleResultsView: SC.View.extend({
        classNames: "footprint-module-results-view".w(),
        childViews: ['scenarioTitleView'],
        layout: {top: 120},

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.contentFirstObject'),

        scenarioTitleView: SC.LabelView.extend({
            layout: {top: 10, left: 10, right: 10, height: 24},
            scenarioName: null,
            scenarioNameBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.name'),
            value: function () {
                return '%@ Outcomes:'.fmt(this.get('scenarioName'));
            }.property('scenarioName')
        })
    }),

    outcomesTableView: SCTable.TableView.design({
        classNames: "footprint-outcomes-table-view".w(),
        layout: {top: 165, left: 10, right: 25, bottom: 50},
        contentBinding: SC.Binding.oneWay('Footprint.resultSummaryTableController*content.query'),
        columnsBinding: SC.Binding.oneWay('Footprint.resultSummaryTableController.columns')
    })
});
