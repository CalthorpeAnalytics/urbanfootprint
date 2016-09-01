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

/**
 * Test the controllers manage the library of DbEntiti of the active ConfigEntity, and possibly other libraries, such as lists of charts, etc.
 *:w
module("Footprint.layLibraryControllers", {
    setup: function() {
        setupApplicationForControllerTesting(
            {
                stateSetup:bypassLoginState
            }
        );
    },

    teardown: controllerTeardown
});

test("Testing layersController", function() {

    // Give the test enough time to complete
    stop(30000);
    var params = {
        controllers: Footprint.layerControllers,
        controllersPath: 'Footprint.layersControllers',
        recordType: Footprint.PresentationMedium
    };
    Footprint.TestForLaryLibraryControllers = testListController(params);

    setTimeout(function() {
        // We exepct one PresentationMedium per db_entity
        var expectedLength = Footprint.scenarioActiveController.getPath('content.db_entities').length;
        ok(expectedLength > 0, "No DbEntities found for the active ConfigEntity");
        assertLength(
            expectedLength,
            Footprint.layersController.get('content'),
            'Footprint.layersController.content');
        assertKindForList(
            Footprint.PresentationMedium,
            Footprint.layersController.get('content'),
            'Footprint.layersController.content');
        // Restart the main thread
        start();
    }, 8000);
});
