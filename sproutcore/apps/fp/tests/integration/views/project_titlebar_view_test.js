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


var pane, view;

module("Footprint.ProjectToolbarView", {
    setup: function () {
        pane = viewSetup({
            contentSetup: function () {
                stop(1000);
                Footprint.regionActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Region)).toArray()[0],
                    setTimeout(function () {
                        Footprint.projectActiveController.set('content', Footprint.projectsController.toArray()[0]);
                        start();
                    }, 500)
                );
            },

            views: function () {
                return [Footprint.ProjectToolbarView.extend({
                })];
            }
        });
        view = pane.childViews[0];
    },

    teardown: viewTeardown()
});

test("Tests that policy set tree was created correctly", function () {

    stop(20000); // delay main thread to allow break points to take
    // Make sure the controller has content
    setTimeout(function () {
        var data = {
            listController: Footprint.projectsController,
            listControllerPath: 'Footprint.projectsController',
            contentView: view.getPath('buttonLayout.selectView'),
            contentViewPath: 'ProjectToolbarView.selectView',
            itemActiveController: Footprint.projectActiveController,
            itemActiveControllerPath: 'Footprint.projectActiveController'
        };
        // Validate the selectView, which changes the active project
        selectViewValidation(pane, data);
        // Validate the titleView, which simply displays the project name
        var titleView = view.get('titleView');
        equals(titleView.get('value'), data.itemActiveController.getPath('content.name'), "Expect %@ label to match %@'s label".fmt('ProjectToolbarView.titleView', data.itemActiveControllerPath));
        start()
    }, 1000);
});
