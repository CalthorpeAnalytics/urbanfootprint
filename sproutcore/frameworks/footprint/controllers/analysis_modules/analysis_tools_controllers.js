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

/**
 * TODO I can't get the models to load before this controller, so recordTypes are wrapped
 */

/***
 * Contains the one Footprint.EnvironmentalConstraintUpdateTool
 */
Footprint.environmentalConstraintUpdaterToolController = SC.ArrayController.create({
    allowsEmptySelection:YES,
    recordType: function() {return Footprint.EnvironmentalConstraintUpdaterTool;}.property()
});

/***
 * Contains the nested store version of the Footprint.EnvironmentalConstraintUpdateTool
 */
Footprint.environmentalConstraintUpdaterToolEditController = Footprint.EditArrayController.create({
    allowsEmptySelection:YES,
    sourceController: Footprint.environmentalConstraintUpdaterToolController,
    isEditable:YES,
    recordsAreUpdating: NO,
    recordType: function() {return Footprint.EnvironmentalConstraintUpdaterTool;}.property(),
    parentEntityKey: 'config_entity',
    parentRecordBinding: SC.Binding.oneWay('Footprint.scenariosController*selection.firstObject')
});

/***
 * Contains the one Footprint.MergeUpdaterTool
 */
Footprint.mergeUpdaterToolController = SC.ArrayController.create({
    allowsEmptySelection: YES,
    recordType: function() {return Footprint.MergeUpdaterTool;}.property()
});

/***
 * Contains the nested store version of the Footprint.MergeUpdaterTool
 */
Footprint.mergeUpdaterToolEditController = Footprint.EditArrayController.create( {
    allowsEmptySelection: YES,
    sourceController: Footprint.mergeUpdaterToolController,
    recordType: function() {return Footprint.MergeUpdaterTool;}.property(),
    isEditable: YES,
    recordsAreUpdating: NO,
    // The AnalysisTool must be queried by checking for instances whose config_entity equals the activeScenario
    parentEntityKey: 'config_entity',
    parentRecordBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content')
});

/**
 * The AnalysisTools of the current AnalysisModules.
 * These are base class instances. The analysisToolControllerLookup
 * resolves them to a controller containing the subclass
 */
Footprint.analysisToolsController = SC.ArrayController.create({
    allowsEmptySelection: NO,
    analysisModule: null,
    analysisModuleBinding: SC.Binding.oneWay('Footprint.analysisModulesController*selection.firstObject'),
    contentBinding: SC.Binding.oneWay('*analysisModule.analysis_tools')
});

Footprint.analysisToolControllerLookup = SC.Object.create({
    environmental_constraint_updater_tool: Footprint.environmentalConstraintUpdaterToolController,
    merge_updater_tool: Footprint.mergeUpdaterToolController
});

Footprint.analysisToolEditControllerLookup = SC.Object.create({
    environmental_constraint_updater_tool: Footprint.environmentalConstraintUpdaterToolEditController,
    merge_updater_tool: Footprint.mergeUpdaterToolEditController
});
