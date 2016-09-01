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

// ==========================================================================
// Project:   Footprint Unit Test
// ==========================================================================

module("Footprint.scenarioController", {
    setup: function() {
        setupApplicationForControllerTesting(
            {
                stateSetup:bypassLoginState
            }
        );
    },

    teardown: function() {
        controllerTeardown();
    }
});

test("Testing scenarioController", function() {

    ok('test');
    // Give the test enough time to complete the asynchronous timeout handlers
    stop(20000);

    var timeout=0;
    setTimeout(function() {
        logStatus(Footprint.globalConfigController, 'Footprint.globalConfigController');
        assertStatus(Footprint.globalConfigController, Footprint.Record.READY_CLEAN, 'Footprint.globalConfigController');
    }, timeout+=2000);

    setTimeout(function() {
        logStatus(Footprint.regionsController, 'Footprint.regionsController');
        assertStatus(Footprint.regionsController, Footprint.Record.READY_CLEAN, 'Footprint.regionsController');
    }, timeout+=2000);

    setTimeout(function() {
        logStatus(Footprint.projectsController, 'Footprint.projectsController');
        assertStatus(Footprint.projectsController, Footprint.Record.READY_CLEAN, 'Footprint.projectsController');
    }, timeout+=2000);

    setTimeout(function() {
        logStatus(Footprint.scenariosController, 'Footprint.scenariosController');
        assertStatus(Footprint.scenariosController, Footprint.Record.READY_CLEAN, 'Footprint.scenariosController');
        start();
    }, timeout+=5000);

});
