MODELS
------
See the models/ and fixtures/ directories.

The Scenario model, for example:

   ScenarioCategory:  (models/scenario_model.js)
     name
     scenarios
  
   Scenario:  (models/scenario_model.js)
     name
     population
     category

These models have fixtures with dummy data:
     
   ScenarioCategory.FIXTURES  (fixtures/config_entity_fixtures.js)
   Scenario.FIXTURES  (fixtures/config_entity_fixtures.js)



CONTROLLERS
-----------
See the controllers/ directory.

The controllers mediate between the model and the view.

In main.js, we set the content for the scenarioController:

    // main.js
    MainApp.scenariosController.set('content', MainApp.scenariosContent);

The controller and its content are defined in controllers/scenarios_controller.js.

The controller is a tree view controller:

    // controllers/scenarios_controller.js
    MainApp.scenariosController = SC.TreeController.create();

The content represents the root node of the tree view (SourceListView), and provides its children
by performing a query for every ScenarioCategory:

    // controllers/scenarios_controller.js
    MainApp.scenariosContent = SC.Object.create({
        name: "root",
        treeItemChildren: function(){
            return MainApp.store.find(SC.Query.local(MainApp.ScenarioCategory, { orderBy: 'guid' }));
        }.property(),
    });

The tree view finds this content by binding its "content" property to the controller's "arrangedObjects" property:

    // views/top_half_view.js
    scenariosView: SC.ScrollView.extend({
        contentView: SC.SourceListView.extend({
            contentBinding: SC.Binding.oneWay('MainApp.scenariosController.arrangedObjects'),
            contentValueKey: 'name',
        })
    })



VIEWS
-----
See the views/ directory.

The UI consists of the following view hierarchy:

 - MainPane (main_pane.js)
   - headerBarView
     - projectView
       - projectLogoView
       - projectSelectView
       - projectMenuView
     - clientView
       - titleView
       - clientLogoView
     - logoutButtonView
   - bodyView
     - topView
      - scenarioSectionView (scenario_section_view.js)
      - resultSectionView (result_section_view.js)
     - bottomView
       - sidebarView (sidebar_view.js)
         - layersView
         - toolsView
         - placetypesView
       - mapView (map_section_view.js)
       - settingsView (analysis_module_section_view.js - currently hidden)
     