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


Footprint.AnalysisModuleSectionView = SC.View.extend({
    classNames: ['footprint-analytic-section-view', 'footprint-map-overlay-section'],
    childViews: ['analysisModuleSelectView', 'contentView', 'overlayView'],

    overlayView: Footprint.OverlayView.extend({
        contentBinding: SC.Binding.oneWay('Footprint.analysisModulesEditController.content'),
        statusBinding:SC.Binding.oneWay('*content.status')
    }),
    /**
     * Titlebar used to changed the active analytic module
     */
    analysisModuleSelectView:  Footprint.LabelSelectView.extend({
        layout: {height: 24, right: 20},
        contentBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController.content'),
        contentStatusBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController.status'),
        selectionBinding: 'Footprint.analysisModulesRightSideEditController.selection',
        isVisibleBinding: SC.Binding.oneWay('.content').notEmpty(false),
        itemTitleKey: 'name',
        // Conditionally give an empty list message
        scenarioNameBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.name'),
        includeNullItemIfEmpty:YES,
        nullTitle: function() {
            return '%@ analysis modules for %@'.fmt(this.get('contentStatus') & SC.Record.READY ? 'No':'Loading', this.get('scenarioName'));
        }.property('scenarioName', 'contentStatus').cacheable(),

        selectedItemBinding: '*selection.firstObject',

        resultsRefreshObserver: function() {
            if (this.getPath('selection.firstObject')) {
                var library_key = 'result_library__%@'.fmt(this.getPath('selection.firstObject.key'));
                var resultLibraries = Footprint.resultLibrariesController.get('content').filter(function (library) {
                    return library.getPath('key') == library_key;
                });
                resultLibraries.forEach(function (library) {
                    library.get('results').forEach(function v(result) {
                        result.refresh();
                    })
                })
            }
        }.observes('.selection', 'Footprint.mainPaneButtonController.analysisModuleSectionIsVisible'),

        nowShowingView:function() {
            if (this.getPath('selection.firstObject'))
                return 'Footprint.%@ModuleManagementView'.fmt(this.getPath('selection.firstObject.key').camelize().capitalize());
        }.property('selection').cacheable()
    }),

    contentView: SC.ContainerView.extend({
        classNames: 'footprint-analytic-section-content-view'.w(),
        layout: {top:24},
        nowShowingBinding: SC.Binding.oneWay('.parentView.analysisModuleSelectView.nowShowingView')
    })
});
