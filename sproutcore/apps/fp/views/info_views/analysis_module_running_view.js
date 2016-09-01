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


Footprint.AnalysisModuleRunningView = SC.View.extend({
    classNames:['footprint-analysis-module-running-view'],
    childViews: ['progressBarView'],
    enabledLayout: null,
    content: null,
    isEnabledBinding: SC.Binding.oneWay('.progressBarView.isVisible'),
    analysisModuleSectionIsVisible: null,
    analysisModuleSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.mainPaneButtonController.analysisModuleSectionIsVisible'),
    editSectionIsVisible: null,
    editSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.mainPaneButtonController.editSectionIsVisible'),
    layout: function() {
        if (!this.get('isEnabled')) {
            return {height: 0, bottom: 0}
        }
        return this.get('enabledLayout')
    }.property('isEnabled').cacheable(),

    progressBarView: Footprint.ProgressBarView.extend({
        layout: {top: 0, left: 0},
        nestedStoreContentBinding: SC.Binding.oneWay('.parentView.content'),
        titleViewLayout: {left: 10, top: 5, height: 25, right: 10},
        progressBarLayout: {top: 35, bottom: 5, left: 10, right: 10},
        title: 'Saving...',
    })
});
