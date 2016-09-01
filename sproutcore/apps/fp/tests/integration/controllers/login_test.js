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
// Project:   Footprint.loginController Unit Test
// ==========================================================================


module("Footprint.loginController", {
    setup: function() {
        setupApplicationForControllerTesting(
            {
                stateSetup: function() {
                    // NOTE: loginContent and the Login model no longer exist. - Dave P
                    login = Footprint.store.find(SC.Query.local(Footprint.Login)).toArray()[0];
                    Footprint.loginContent.set('username', login.get('username'))
                    Footprint.loginContent.set('password', login.get('password'))
                }
            }
        );
    },

    teardown: controllerTeardown
});


test("Testing userController", function() {

    // Set the loginContent to simulate the form entry
    // Wait for the server
    stop(3000);
    setTimeout(function() {
        SC.RunLoop.begin();
        SC.RunLoop.end();
        assertStatus(Footprint.userController.content, Footprint.Record.READY_CLEAN, 'Footprint.userController');
        assertCurrentState(Footprint.LoadingApp);
        start();
    }, 1000);
});
