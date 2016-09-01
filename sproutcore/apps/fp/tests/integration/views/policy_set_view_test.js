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

module("Footprint.PolicySetView", {
    setup: function() {
        pane = viewSetup({
            contentSetup: function() {
                Footprint.scenarioActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Scenario)).toArray()[0]
                );
                setTimeout(function() {
                }, 500);
            },

            views: function() {
                return [Footprint.PolicySetView.extend({
                    layout: { top:0, width:.50 }
                })];
            }
        });
        view = pane.childViews[0];
    },

    teardown: viewTeardown()
});

test("Tests that policy set tree was created correctly", function() {

    stop(20000); // ddelay the main thread so the delayed validation can work below
    // Make sure the controller has content
    setTimeout(function() {
        treeViewValidation(pane, {
            treeController: Footprint.policyCategoriesTreeController,
            treeControllerPath:'Footprint.policyCategoriesTreeController',
            contentView: view.getPath('listView.contentView'),
            contentViewPath: 'PolicySetView.listView.contentView',
            topLevelValidator: function(i, itemView, policyCategory) {
            },
            bottomLevelValidator: function(i, itemView, policy) {
                ok(!isNaN(itemView.get('valueView').get('value')), 'Expecting a numeric value the value property  for item index %@, representing instance %@'.fmt(i, policy.toString()));
            }
        });

        start()
    }, 1000);
});
