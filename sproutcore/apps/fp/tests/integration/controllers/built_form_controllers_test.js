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
/*globals Footprint module test ok equals same stop start */


module("Footprint.builtFormsControllers", {
    setup: function() {
        setupApplicationForControllerTesting(
            {
                stateSetup: bypassLoginState
            }
        );
    },
    teardown: controllerTeardown
});


test("Testing builtFormCategoriesTreeController", function() {
    // Give the test enough time to complete
    stop(30000);
    var params = {
        controllers: Footprint.builtFormControllers,
        controllersPath: 'Footprint.builtFormControllers',
        recordType: Footprint.BuiltForm
    };
    Footprint.TestForBuiltFormControllers = testTreeController(params);
});
