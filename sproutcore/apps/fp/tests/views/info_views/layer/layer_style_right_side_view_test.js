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

/*global module, test, AsyncTest, ok, equals */
var rightSideView, pane;

sc_require('views/info_views/layer/layer_style_right_side_view.js');

module('Footprint.LayerStyleRightSideView', {

    setup: function() {
        rightSideView = Footprint.LayerStyleRightSideView.create();
        pane = SC.Pane.create({
            childViews: [rightSideView],
            layout: { width: 400, height: 400, centerY: 0, centerX: 0 },
        });
        pane.append();
    },

    teardown: function() {
        pane.destroy();
    },
});

test('The view can be disabled', AsyncTest(function(done) {
    var disabledViewPaths = [
        'symbologyTypeView.selectView',
        'attributeSelectView',
        'symbologyContainerView.contentView',
    ];

    // wait for sproutcore to settle
    setTimeout(function() {

        disabledViewPaths.forEach(function(path) {
            var view = rightSideView.getPath(path);
            ok(view, 'Should have child view ' + path);

            equals(view.get('isEnabled'), true, 'Should be enabled by default');
        });

        rightSideView.set('isEnabled', false);

        setTimeout(function() {

            disabledViewPaths.forEach(function(path) {
                var view = rightSideView.getPath(path);
                equals(view.get('isEnabled'), false, path + ' should be disabled');
                done();
            });
        });

    });

}));
