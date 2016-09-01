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

sc_require('controllers/config_entities/scenario_controllers');
sc_require('controllers/sets_controllers');

Footprint.builtFormSetsController = Footprint.SetsController.create({
    listControllerBinding: SC.Binding.oneWay('Footprint.scenariosController'),
    property:'built_form_sets'
});


Footprint.urbanBuiltFormSetsController = Footprint.SetsController.create({
    listControllerBinding: SC.Binding.oneWay('Footprint.scenariosController'),
    property:'built_form_sets',
    allContent: null,
    allContentBinding: SC.Binding.oneWay('Footprint.builtFormSetsController.content'),

    allContentStatus: null,
    allContentStatusBinding: SC.Binding.oneWay('Footprint.builtFormSetsController*content.status'),

    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    content: function() {
        if (this.get('status') & SC.Record.READY) {
            return this.get('allContent').filter(function(built_form_set) {
                return built_form_set.getPath('key') != 'sacog_rucs'
            })
        }
    }.property('allContent', 'allContentStatus').cacheable(),
    // We have no status of our own since we filter the content
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.builtFormSetsController.status'),

    editSectionIsVisible: null,
    editSectionIsVisibleBinding:  'F.mainPaneButtonController.editSectionIsVisible',

    selectionObserver: function() {
        if (this.get('content')) {
            Footprint.urbanBuiltFormSetsController.selectObject(this.getPath('content.firstObject'));
        }
    }.observes('content', 'activeScenario', '*activeScenario.status', 'editSectionIsVisible')
});


Footprint.agricultureBuiltFormSetsController = Footprint.SetsController.create({
    listControllerBinding: SC.Binding.oneWay('Footprint.scenariosController'),
    property:'built_form_sets',

    allContent: null,
    allContentBinding: SC.Binding.oneWay('Footprint.builtFormSetsController.content'),

    activeScenario: null,
    activeScenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    allContentStatus: null,
    allContentStatusBinding: SC.Binding.oneWay('Footprint.builtFormSetsController*content.status'),

    content: function() {
        if (this.get('status') & SC.Record.READY) {
            return this.get('allContent').filter(function(built_form_set) {
                return built_form_set.getPath('key') == 'sacog_rucs'
            })
        }
    }.property('allContent', 'allContentStatus').cacheable(),
    // We have no status of our own since we filter the content
    status: null,
    statusBinding: SC.Binding.oneWay('Footprint.builtFormSetsController.status'),

    editSectionIsVisible: null,
    editSectionIsVisibleBinding:  'F.mainPaneButtonController.editSectionIsVisible',

    selectionObserver: function() {
        if (this.get('content')) {
            Footprint.agricultureBuiltFormSetsController.selectObject(this.getPath('content.firstObject'));
        }
    }.observes('content', 'activeScenario', '*activeScenario.status', 'editSectionIsVisible')
});
/***
 * The active builtFormSet bound to that of the ConfigEntity's selected BuiltFormSet so that the user can change it.
 * Changing it causes the ConfigEntity to be updated on the server
 * @type {*}
 */

Footprint.urbanBuiltFormSetActiveController = Footprint.ActiveController.create({
    listController:Footprint.urbanBuiltFormSetsController
});
Footprint.agricultureBuiltFormSetActiveController = Footprint.ActiveController.create({
    listController:Footprint.agricultureBuiltFormSetsController
});

//    /***
//     * Observe the active layer and change the built form set if the layer corresponds to a specific built_form_set
//     */
//    layerActiveControllerObserver: function() {
//        if ((Footprint.layerActiveController.get('status') & SC.Record.READY) === SC.Record.READY) {
//            if (!Footprint.layerActiveController.didChangeFor('showingBuiltFormPanel', 'content'))
//                return this;
//            var built_form_set_key = Footprint.urbanBuiltFormSetsController.getPath('selection.firstObject.key');
//            if (built_form_set_key) {
//                Footprint.urbanBuiltFormSetsController.selectObject(
//                    Footprint.store.find(SC.Query.local(
//                        Footprint.BuiltFormSet, {
//                            conditions: 'key = {key}',
//                            key: built_form_set_key
//                        })).firstObject());
//            }
//        }
//    }.observes('Footprint.layerActiveController.status')
