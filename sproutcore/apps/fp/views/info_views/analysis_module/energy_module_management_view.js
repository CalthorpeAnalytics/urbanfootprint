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

Footprint.EnergyModuleManagementView = SC.View.extend({

    classNames: "footprint-energy-module-management-view".w(),
    childViews: ['manageModuleView', 'moduleResultsView'],

    allResultsStatus: null,
    allResults: null,

    title: 'Energy Module',

    allResultsBinding: SC.Binding.oneWay('Footprint.resultsController.content'),
    allResultsStatusBinding: SC.Binding.oneWay('Footprint.resultsController.status'),

    analysisModule: null,
    analysisModuleBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController*selection.firstObject'),

    content: function () {
        if (this.get('allResultsStatus') & SC.Record.READY)
            return this.get('allResults').filter(function (result) {
                return result.getPath('db_entity.key') == 'result__energy';
            });
    }.property('allResults', 'allResultsStatus').cacheable(),

    contentFirstObject: null,
    contentFirstObjectBinding : SC.Binding.oneWay('*content.firstObject'),

    manageModuleView: Footprint.AnalysisModuleView,

    moduleResultsView: SC.View.extend({
        classNames: "footprint-module-results-view".w(),
        childViews: ['scenarioTitleView', 'totalEnergyResultView', 'residentialEnergyResultView', 'energyPerHHResultView', 'commercialEnergyResultView', 'commercialPerSqFtResultView'],
        layout: {top: 120},

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.contentFirstObject'),

        scenarioTitleView: SC.LabelView.extend({
            layout: {top: 10, left: 10, right: 10, height: 24},
            scenarioName: null,
            scenarioNameBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.name'),
            value: function() {
            return '%@:'.fmt(this.get('scenarioName'));
        }.property('scenarioName')
        }),

        totalEnergyResultView: Footprint.TwoValueLabeledResultView.extend({
            layout: {height: 45, top: 40, left: 10, right: 10},
            resultBinding: SC.Binding.oneWay('.parentView*content.query.firstObject'),
            column1Name: 'total_gas_use__sum',
            column2Name: 'total_electricity_use__sum',
            title:  'Total Energy Use',
            subTitle1:'Gas (thm)',
            subTitle2: 'Electricity (Kwh)'
        }),

        residentialEnergyResultView: Footprint.TwoValueLabeledResultView.extend({
            layout: {height: 45, top: 100, left: 10, right: 10},
            resultBinding: SC.Binding.oneWay('.parentView*content.query.firstObject'),
            column1Name: 'residential_gas_use__sum',
            column2Name: 'residential_electricity_use__sum',
            title: 'Residential Energy Use',
            subTitle1:'Gas (thm)',
            subTitle2: 'Electricity (Kwh)'
        }),

        commercialEnergyResultView: Footprint.TwoValueLabeledResultView.extend({
            layout: {height: 45, top: 160, left: 10, right: 10},
            resultBinding: SC.Binding.oneWay('.parentView*content.query.firstObject'),
            column1Name: 'commercial_gas_use__sum',
            column2Name: 'commercial_electricity_use__sum',
            title: 'Commercial Energy Use',
            subTitle1: 'Gas (thm)',
            subTitle2: 'Electricity (Kwh)'
        }),

        energyPerHHResultView: Footprint.TwoValueLabeledResultView.extend({
            layout: {height: 45, top: 220, left: 10, right: 10},
            resultBinding: SC.Binding.oneWay('.parentView*content.query.firstObject'),
            column1Name: 'residenital_per_hh_gas_use__sum',
            column2Name: 'residenital_per_hh_electricity_use__sum',
            title: 'Residenital Energy Use per Dwelling Unit',
            subTitle1: 'Gas (thm / du)',
            subTitle2: 'Electricity (Kwh / DU)'
        }),

        commercialPerSqFtResultView: Footprint.TwoValueLabeledResultView.extend({
            layout: {height: 45, top: 280, left: 10, right: 10},
            resultBinding: SC.Binding.oneWay('.parentView*content.query.firstObject'),
            column1Name: 'commercial_per_emp_gas_use__sum',
            column2Name: 'commercial_per_emp_electricity_use__sum',
            title: 'Commercial Energy Use per Employee',
            subTitle1: 'Gas (thm / emp)',
            subTitle2: 'Electricity (Kwh / emp)'
        })
    })
})
