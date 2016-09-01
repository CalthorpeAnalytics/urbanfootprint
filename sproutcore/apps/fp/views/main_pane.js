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

sc_require('views/header_bar_view');
sc_require('views/top_view_tool_view');
sc_require('views/top_view_panel');
sc_require('views/bottom_view');

Footprint.MainPane = SC.MainPane.extend({
    childViews: ['headerBarView', 'bodyView'],

    headerBarView: Footprint.HeaderBarView.extend({
        layout: { height: 35 }
    }),

    bodyView: SC.View.extend({
        layout: { top: 35},
        childViews: ['topView', 'mainView'],

        topView: SC.ContainerView.extend({
            isVisibleBinding: 'Footprint.topSectionVisibleViewController.topSectionIsVisible',
            layoutBinding:'Footprint.topSectionVisibleViewController.topSectionLayout',
            layout: {height: 200},
            childViews: ['topViewPanel'],

            topViewPanel: Footprint.TopViewPanel.extend({
                layout: {left: 0}
            })
        }),

        mainView: Footprint.BottomView.extend({
            layout: {top: 200, bottom: 0}
        })
    })
});
