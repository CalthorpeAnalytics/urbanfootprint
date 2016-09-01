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

sc_require('views/builtformsview');
var pane, view;

module("footprint.builtformsview", {
    setup: function () {
        pane = viewSetup({
            contentSetup: function () {
            },
            views: function () {
                return [Footprint.BuiltFormsView.extend({
                    layout: { top: 0, width: .25 }
                })];
            }
        });
        view = pane.childViews[0];
    },

    teardown: function () {
        viewTeardown();
    }
});

test("Check the tree view bound to the BuiltForm data", function () {

    // Make sure the controller has content
    stop(1500000); // delay main thread up to a second to allow breakpoints to work

    throw "die so we can interact";
    var contentViewPath = 'listView.contentView';
    var params = {
        controllers: Footprint.builtFormControllers,
        controllersPath: 'Footprint.builtFormControllers',
        contentView: view.getPath(contentViewPath),
        contentViewPath: 'Footprint.BuiltFormsView.' + contentViewPath,
        editbarView: view.toolbarView.editbarView
    };
    treeViewValidation(pane, params);
});
