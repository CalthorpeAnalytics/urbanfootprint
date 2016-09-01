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

/***
 * Tests the Footprint.LayerLibraryView data binding, event handling, and rendering.
 */
module("Footprint.EditableModelStringView", {
    setup: function() {
        pane = viewSetup({
            contentSetup: function() {

                Footprint.scenarioActiveController.set('content',
                    Footprint.store.find(SC.Query.local(Footprint.Scenario)).toArray()[0]
                );
            },

            views: function() {
                return [Footprint.EditableModelStringView.extend({
                    layout: { top:0, width:.30, height:20},
                    valueBinding : 'Footprint.scenarioActiveController.name'
                })];
            }
        });
        view = pane.childViews[0];
        view.isEditingObserver = function() {
            pane.$().css('position', 'relative');
        }.observes('Footprint.scenarioActiveController.name');
    },

    teardown: viewTeardown()
});

test("Tests editing and binding of a Footprint.EditableModelStringView", function() {

    stop(1000000); // delay main thread up to a second to allow any breakpoints to work
    // Make sure the controller has content
    setTimeout(function() {
        var value = view.get('value');
        var updatedValue = '%@__Test'.fmt(value);
        editLabel(view);
        // The inline editor resets positioning to absolute, hiding the test results
        equals(updatedValue, view.get('value'), "Expected value %@ to become %@".fmt(value, updatedValue));
        start();

    }, 1000);
});
