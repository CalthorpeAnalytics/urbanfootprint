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


module("Footprint.policiesControllers", {
    setup: function() {
        setupApplicationForControllerTesting(
            {
                stateSetup: bypassLoginState
            }
        );
    },

    teardown: controllerTeardown
});

test("Testing policyCategoriesTreeController", function() {

    // Give the test enough time to complete the asynchronous timeout handlers
    stop(10000);

    setTimeout(function() {
        // Verify that PolicySet instances at the first level of the tree
        var policyCategories = Footprint.policyCategoriesTreeController.get('treeItemChildren');
        assertNonZeroLength(policyCategories, 'Footprint.policyCategoriesTreeController.arrangedObjects');
        assertKindForList(Footprint.PolicyCategory, policyCategories, 'Footprint.policyCategoriesTreeController.arrangedObjects');
        // Verify that Policy instances at the second level of the tree
        assertNonZeroLength(policyCategories[0].get('treeItemChildren'),
            'Footprint.policyCategoriesTreeController.treeItemChildren[0].treeItemChildren');
        assertKindForList(Footprint.Policy, policyCategories[0].get('treeItemChildren'),
            'Footprint.policyCategoriesTreeController.treeItemChildren[0].treeItemChildren');
        // Restart the main thread
        start();
    }, 2400);
});
