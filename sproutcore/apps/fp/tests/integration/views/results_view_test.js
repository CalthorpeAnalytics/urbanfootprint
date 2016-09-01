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


var pane = null, view=null;
module("Footprint.ResultsView", {

    setup: function() {

        pane = viewSetup({
            contentSetup: function() {
                Footprint.projectActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Project)).toArray()[0]
                );
                Footprint.scenarioActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Scenario)).toArray()[0]
                );
            },

            views: function() {
                return [Footprint.ResultSectionView.extend({
                    layout: { top:0, width:.50 }
                })];
            }
        });
        view = pane.childViews[0];
    },

    teardown: viewTeardown()
});

test("Tests that scenarios tree was created correctly", function() {

 stop(200000000); // delay main thread up to a second to allow any breakpoints to work
    // Make sure the controller has content
    setTimeout(function() {
        throw "SDF";
    }, 10000);
});
