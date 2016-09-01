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


var pane = null, view = null;
module("Footprint.ScenariosView", {

    setup: function () {

        pane = viewSetup({
            contentSetup: function () {
                Footprint.projectActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Project)).toArray()[0]
                );
            },

            scenariosLoaded: function () {
                logStatus(Footprint.scenariosController, 'Footprint.scenariosController');
                if (Footprint.scenariosController.get('status') === Footprint.Record.READY_CLEAN) {
                    // Default to the first Scenario for now
                    Footprint.scenarioActiveController.set('content', Footprint.scenariosController.content.toArray()[0]);
                }
            }.observes('Footprint.scenariosController.status'),

            views: function () {
                return [Footprint.ScenarioSectionView.extend({
                    layout: { top: 0, width: .50 }
                })];
            }
        });
        view = pane.childViews[0];
    },

    teardown: viewTeardown()
});

test("Tests that scenarios tree was created correctly", function () {

    // Make sure the controller has content
    stop(20000); // delay main thread up to a second to allow breakpoints to work

    var contentViewPath = 'listView.contentView';
    var params = {
        controllers: Footprint.scenarioControllers,
        controllersPath: 'Footprint.scenarioControllers',
        contentView: view.getPath(contentViewPath),
        contentViewPath: 'Footprint.ScenariosView.' + contentViewPath,
        editbarView: view.toolbarView.editbarView
    };
    treeViewValidation(pane, params);
});
