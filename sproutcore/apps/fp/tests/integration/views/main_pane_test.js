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

/**
 * Tests the entire MainPane
 */
module("Footprint.MainPane", {
    setup: function() {
        pane = viewSetup({
            contentSetup: function() {
                // Rather than explicity controller bindings like we usually do for view tests, just start the statechart and skip the login state
                Footprint.statechart.initStatechart();
                bypassLoginState();
            },
            mainPane: Footprint.MainPane
        });
        view = pane.childViews[0];
    },

    teardown: viewTeardown()
});

test("Tests that policy set tree was created correctly", function() {

    stop(20000); // delay main thread to allow break points to take
    // Make sure the controller has content
    setTimeout(function() {
//        start()
    }, 1000);
});
