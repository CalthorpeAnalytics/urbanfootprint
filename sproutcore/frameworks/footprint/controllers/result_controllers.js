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


sc_require('models/presentation_models');
sc_require('controllers/config_entities/scenario_controllers');
sc_require('controllers/presentation_controllers');

Footprint.resultLibrariesController = Footprint.PresentationsController.create({
    contentBinding:SC.Binding.oneWay('Footprint.scenarioActiveController*presentations.results'),

    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.scenarioActiveController*presentations.status'),

    editSectionIsVisible: null,
    editSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.mainPaneButtonController.editSectionIsVisible'),

    analysisModuleSectionIsVisible: null,
    analysisModuleSectionIsVisibleBinding: SC.Binding.oneWay('Footprint.mainPaneButtonController.analysisModuleSectionIsVisible'),

    activeAnalysisModule: null,
    activeAnalysisModuleBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController.selection'),

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    selectionObserver: function() {
        if ((this.get('status') & SC.Record.READY) && this.get('content')) {
            var results = this.get('content').filter(function (library) {
                return library.get('key') == "result_library__application"
            });
            this.selectObject(results.firstObject());

            if (this.get('activeAnalysisModule') && this.get('analysisModuleSectionIsVisible')) {
                var analysisKey = this.getPath('activeAnalysisModule.firstObject.key');
                if (['water', 'energy', 'fiscal', 'vmt', 'agriculture_analysis', 'public_health'].contains(analysisKey)) {
                    var results = this.get('content').filter(function (library) {
                        return library.get('key') == "result_library__%@".fmt(analysisKey)
                    });
                    this.selectObject(results.firstObject())
                }
            }
            if (this.get('activeLayer') && this.get('editSectionIsVisible')) {
                if ('behavior__agriculture_scenario' == this.getPath('activeLayer.db_entity.feature_behavior.behavior.key') ||
                        'behavior__base_agriculture' == this.getPath('activeLayer.db_entity.feature_behavior.behavior.key')) {
                    var results = this.get('content').filter(function (library) {
                        return library.get('key') == "result_library__agriculture_analysis".fmt(analysisKey)
                    });
                    this.selectObject(results.firstObject())
                }
            }
        }
    }.observes('.status', '.content', '.analysisModuleSectionIsVisible', '.activeAnalysisModule', '.activeLayer', '.editSectionIsVisible')
});

Footprint.resultLibraryActiveController = Footprint.PresentationController.create({
    presentationsBinding:SC.Binding.oneWay('Footprint.resultLibrariesController.content'),
    keyBinding: SC.Binding.oneWay('Footprint.resultLibrariesController*selection.firstObject.key'),
    keysBinding: SC.Binding.oneWay('.results').transform(function(value) {
        if (value && value.get('status') & SC.Record.READY)
            return value.mapProperty('db_entity').mapProperty('key');
    })
});

/**
 * The results of the active resultLibraryActiveController. Results are subclasses of PresentationMedium instances
 * @type {*}
 */

Footprint.resultsController = Footprint.PresentationMediaController.create({
    presentationBinding: SC.Binding.oneWay('Footprint.resultLibraryActiveController.content'),
    contentBinding: SC.Binding.oneWay('Footprint.resultLibraryActiveController.results')
});

//
///**
// * This aggregates the public-facing properties of the other controllers
// * The resentationMedium instances for results represent Result instances
// * @type {*|void}
// */
//
//Footprint.resultLibraryContent = Footprint.LibraryContent.create({
//    presentationController: Footprint.resultLibraryActiveController,
//    presentationMediaController:Footprint.resultsController
//});
//
//
///***
// *  Aggregates the public-facing properties of the other controllers
// * @type {*|void}
// */
//
//Footprint.resultLibraryController = SC.ObjectController.create({
////    // Binding content makes all other properties accessible via delegation
//    contentBinding: SC.Binding.oneWay('Footprint.resultLibraryContent')
//});
//
///***
// * Binds to the currently selected Result
// * @type {*}
// */
//
//Footprint.resultActiveController = Footprint.PresentationMediumActiveController.create({
//    listController: Footprint.resultsController
//});
//

/***
 * Edits the active Result, a clone of the active Result, or a brand new Result
 * @type {*|void}
 */
Footprint.resultEditController = Footprint.PresentationMediumEditController.create({
//    objectControllerBinding:'Footprint.resultActiveController'
});

Footprint.resultSummaryTableController = SC.ObjectController.create({
    resultContent: null,
    resultContentBinding: SC.Binding.oneWay('Footprint.resultsController.content').defaultValue(null),
    resultStatus: null,
    resultStatusBinding: SC.Binding.oneWay('Footprint.resultsController.status'),
    content: function () {
        if (this.get('resultStatus') & SC.Record.READY) {
            var result = this.get('resultContent').filter(function (result) {
                return result.getPath('configuration.result_type') == 'summary_table';
            }).sortProperty('name');
            if (result)
                return result[0];
        }
    }.property('resultContent', 'resultStatus').cacheable(),

    resultFieldsTitleLookup: function() {
       if (!this.get('content')) {
            return []
        }
        var attributeToColumn = this.getPath('configuration.attribute_to_column');
        var columnToLabel = this.getPath('configuration.column_to_label');
        return mapToSCObject(
            this.getPath('configuration.attributes'),
            function(attribute) {
                return [attribute, columnToLabel[attributeToColumn[attribute]]]
            })
    }.property('content').cacheable(),

    columns: function() {
       if (!this.get('content')) {
            return []
        }
        return this.getPath('configuration.attributes').map(function(attribute) {
            return SC.Object.create(SCTable.Column, {
                name: this.get('resultFieldsTitleLookup').get(attribute) || attribute,
                valueKey: attribute,
                width: 150
            })
        }, this)
    }.property('content').cacheable()
});

//Footprint.resultControllers = Footprint.ControllerConfiguration.create({
//    editController:Footprint.resultEditController,
//    itemsController:Footprint.resultsController,
//    recordSetController:Footprint.resultLibraryController
//});
