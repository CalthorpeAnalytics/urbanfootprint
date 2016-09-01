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

sc_require('views/top_section_views/aggregates_top_section_view');
sc_require('views/top_section_views/approval_top_section_view');
sc_require('views/top_section_views/query_top_section_view');
sc_require('views/top_section_views/manage_scenario_top_section_view');


/**
 * Panel that displays different section_views depending on the user's choice.
 * Currently this supports the ManageScenarioTopSectionView, the QueryTopSectionView, the AggregatesTopSectionView,
 * and for Data Managements Sites the ApprovalTopSectionView.
 *
 * The Panel slides down and up to allow a fuller view of the map.
 */

Footprint.TopViewPanel = SC.View.extend({
    childViews: ['closePanelButton', 'activeTopViewPanel'],

    transitionShow: SC.View.SLIDE_IN,
    transitionShowOptions: { duration: 0.2 },
    transitionHide: SC.View.SLIDE_OUT,
    transitionHideOptions: { direction: 'left', duration: 0.2 },

    closePanelButton: SC.ImageButtonView.extend({
        layout: {left: 8, top: 8, width: 16, height:16},
        classNames: ['footprint-close-panel-button-view'],
        action: 'doCloseTopSection',
        image: 'close-panel-icon'
    }),

    activeTopViewPanel: SC.ContainerView.extend({
        layout: {left: 30 },
        activeTopViewProperty: null,
        activeTopViewPropertyBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.view'),

        nowShowing: function() {
            if (this.getPath('activeTopViewProperty')) {
                return this.get('activeTopViewProperty');
            }
        }.property('activeTopViewProperty').cacheable()
    })
});
