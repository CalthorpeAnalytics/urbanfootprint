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


sc_require('controllers/controllers');

Footprint.analysisModulesController = SC.ArrayController.create(Footprint.RecordControllerChangeSupport, {
    selectedItemDidChangeEvent:'analysisModuleDidChange',
    contentDidChangeEvent:'analysisModulesDidChange'
});

/***
 * The base controller used to edit the AnalysisModules, which for now just means saving them in order to
 * run them. This is extended by controllers below to manage AnalysisModules based on their situation in the app
 */
Footprint.AnalysisModulesEditController = Footprint.EditArrayController.extend({
    allowsEmptySelection: NO,
    firstSelectableObject: function() {
        return (this.get('content') || []).find(function(analysisModule) {
            // Pick core if it exists
            return analysisModule.get('key')=='vmt'
        }) || this.get('firstObject');
    }.property('content'),
    sourceController: Footprint.analysisModulesController,
    isEditable:YES,
    recordType: 'Footprint.AnalysisModule',
    parentEntityKey: 'config_entity',
    parentRecordBinding: SC.Binding.oneWay('Footprint.scenariosController*selection.firstObject')
});

/**
 * All AnalysisModules. Used for loading/updating
 */

Footprint.analysisModulesEditController = Footprint.AnalysisModulesEditController.create({
    selectionBinding: SC.Binding.from('Footprint.analysisModulesController.selection')
});

/***
 * Manages the right-side view of analysis modules. I believe the only reason this is
 * separated from Footprint.analysisModulesEditController is because the Data Manager approve/merge tool
 * is an AnalysisTool that doesn't go on the right side
 */
Footprint.analysisModulesRightSideEditController = Footprint.AnalysisModulesEditController.create({
    // Keep the selection bound two-way to analysisModulesEditController
    selectionBinding: SC.Binding.from('Footprint.analysisModulesEditController.selection'),

    allContent: null,
    allContentBinding: SC.Binding.oneWay('Footprint.analysisModulesEditController.content'),

    allContentStatus: null,
    allContentStatusBinding: SC.Binding.oneWay('Footprint.analysisModulesEditController*content.status'),

    /***
     * The allowed Analysis Modules based on matching tools
     * This is also refreshed by the statechart when allContent loads
     */
    content: function() {
        if (this.get('allContent')) {
            return this.get('allContent').filter(function (module) {
                var analysis_tool = module.getPath('analysis_tools.firstObject');
                return analysis_tool.getPath('behavior.key') == 'behavior__analysis_tool'
            })
        }
    }.property('allContent', 'allContentStatus').cacheable(),

    // We have no status of our own since we filter the content
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.analysisModulesEditController.status'),

    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('Footprint.scenariosController.selection'),

    firstSelectableObject: function() {
        return (this.get('status') & SC.Record.READY) && this.getPath('selection.length') === 0 ? this.get('allContent').find(function(item) {
            var analysis_tool = item.getPath('analysis_tools.firstObject');
            return analysis_tool.getPath('behavior.key') == 'behavior__analysis_tool'
        }) : null;
    }.property('allContent')
});


Footprint.environmentalConstraintModuleController = SC.ArrayController.create({
    allowsEmptySelection:YES,
    recordType: Footprint.environmentalConstraintModuleController
});

Footprint.environmentalConstraintModuleEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:YES,
    sourceController: Footprint.environmentalConstraintModuleController,
    isEditable:YES,
    recordsAreUpdating: NO,
    recordType: Footprint.EnvironmentalConstraintUpdaterTool,
    parentEntityKey: 'config_entity',
    parentRecordBinding: SC.Binding.oneWay('Footprint.scenariosController*selection.firstObject')
});


Footprint.mergeModuleController = SC.ArrayController.create({
    allowsEmptySelection:YES,
    recordType: Footprint.mergeModuleController
});

Footprint.mergeModuleEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:YES,
    sourceController: Footprint.mergeModuleController,
    isEditable:YES,
    recordsAreUpdating: NO,
    recordType: Footprint.MergeUpdaterTool,
    parentEntityKey: 'config_entity',
    parentRecordBinding: SC.Binding.oneWay('Footprint.scenariosController*selection.firstObject')
});


Footprint.supplementalModuleControllerLookup = SC.Object.create({
    environmental_constraint: Footprint.environmentalConstraintModuleController,
    merge_module: Footprint.environmentalConstraintModuleController
});

Footprint.supplementalModuleEditControllerLookup = SC.Object.create({
    environmental_constraint: Footprint.environmentalConstraintModuleEditController,
    merge_module: Footprint.mergeModuleEditController
});
