/*
 * UrbanFootprint v1.5
 * Copyright (C) 2017 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */


sc_require('states/loading_config_entity_states');

/***
 * The default post-login state, whether for an authenticated session or an anonymous demo session
 * @type {Class}
 * TODO rename states to have State suffix
 */
Footprint.LoadingAppState = SC.State.design({

    didLoadGlobalConfigController: function() {
        this.gotoState('loadingRegionsState');
    },
    didLoadRegionController: function() {
        var regionController = this.get('loadingController');
        this.getPath('loadingRegionsState.loadingController').forEach(function(region) {
            var delegate = Footprint.regionActiveController.get('configEntityDelegate');
            var loadingRegionStateClass = delegate.get('loadingRegionStateClass');


            // TODO for some reason loadingProjectsState doesn't run if this is null
            if (loadingRegionStateClass) {
                // By adding a substate to a concurrent state that supports concurrent classes, this will
                // run when we enter the state, along with the loadingProjectState itself
                this.get('loadingProjectsState').addSubstate('loading%@State'.fmt(region.get('key').classify()), loadingRegionStateClass);
            }
        }, this);
        this.gotoState('loadingProjectsState');
    },
    didLoadProjects: function() {
        this.gotoState('loadingScenarioDependenciesState');
    },
    didLoadScenarioDependencies: function() {
        this.gotoState('loadingScenariosState');
    },
    didLoadScenarioController: function(context) {
        if (Footprint.store.find(Footprint.Scenario).get('length') == 0)
            throw "Improperly configured. No Scenarios exist"
        // Goto without a sending the context. The receiver expect a single Scenario, not the list
        this.gotoState('showingAppState')
    },

    didFailLoadingController: function(context) {
        SC.AlertPane.error({
            message: 'Login Error',
            description: "There was an error logging you in. Please alert the system's administrator. Sorry for the inconvenience!",
            buttons: [{
                title: 'OK',
                action: 'doLogout'
            }]
        })
    },

    enterState: function() {
        Footprint.getPath('loginPage.mainPane').remove();
        Footprint.mainPage.get('loadingPane').append();
    },

    exitState:function() {
        this.getPath('statechart.mainPage.loadingPane').remove();
    },

    initialSubstate:'loadingGlobalConfigState',

    // These states are loaded sequentially
    loadingGlobalConfigState: SC.State.plugin('Footprint.LoadingGlobalConfigState'),
    loadingRegionsState: SC.State.plugin('Footprint.LoadingRegionsState'),
    loadingProjectsState: SC.State.plugin('Footprint.LoadingProjectsState', {
        // Limit to the loaded Projects
        parentConfigEntity: null,
        parentConfigEntityBinding: SC.Binding.oneWay('*parentController.content'),
    }),
    loadingScenariosState: SC.State.plugin('Footprint.LoadingScenariosState', {
        // Limit to the loaded Projects
        parentConfigEntity: null,
        parentConfigEntityBinding: SC.Binding.oneWay('*parentController.content'),
    }),
    loadingScenarioDependenciesState: SC.State.plugin('Footprint.LoadingScenarioDependenciesState', {
        // The following substates load concurrently
        // These are currently all global but could be modified to load constrained to the loaded
        // scenario(s)
        loadingConfigEntityCategoriesState: SC.State.plugin('Footprint.LoadingConfigEntityCategoriesState', {
            loadingController: Footprint.configEntityCategoriesController
        }),
        loadingBuiltFormTagsState: SC.State.plugin('Footprint.LoadingBuiltFormTagsState', {
            loadingController: Footprint.builtFormTagsController
        }),
        loadingDbEntityTagsState: SC.State.plugin('Footprint.LoadingDbEntityTagsState', {
            loadingController: Footprint.dbEntityAllTagsController
        }),
        loadingDbEntityCategoriesState: SC.State.plugin('Footprint.LoadingDbEntityCategoriesState', {
            loadingController: Footprint.dbEntityAllCategoriesController
        }),
        loadingBuildingUseDefinitionsState: SC.State.plugin('Footprint.LoadingBuildingUseDefinitionsState', {
            loadingController: Footprint.buildingUseDefinitionsController
        }),
        loadingBehaviorsState: SC.State.plugin('Footprint.LoadingBehaviorsState', {
            loadingController: Footprint.behaviorsController
        }),
        //
        //loadingIntersectionsState: SC.State.plugin('Footprint.LoadingIntersectionsState', {
        //    loadingController: Footprint.intersectionsController
        //})
        //loadingPolicySetsState:SC.State.plugin('Footprint.LoadingIntersectionsState', {
        //    loadingController: Footprint.policySetsController,
        //    eventKey: 'policySetsController'
        //})
    }),
});
