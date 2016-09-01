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

sc_require('views/section_views/map_section_view');
sc_require('views/section_views/visible_layer_section_view');
sc_require('views/left_sidebar_view');
sc_require('views/right_sidebar_view');
sc_require('views/right_sidebar_buttons_view');
sc_require('views/section_views/scenario_edit_result_view');

/**
 * The entire bottom of the application, meaning everything not in TopViewPanel
 */
Footprint.BottomView = SC.SplitView.extend(SC.SplitChild, {
    layoutBinding:'F.topSectionVisibleViewController.bottomSectionLayout',
    childViews: ['leftSidebarView', 'centerView'],

    leftSidebarView: Footprint.LeftSidebarView.extend(SC.SplitChild, {
        // Smoothly resize.
        sizeOffset:-2,
        canCollapse:YES,
        transitionAdjust: SC.View.SMOOTH_ADJUST,
        transitionAdjustOptions: { duration: 0.2 },
        size: 350
    }),

    centerView:SC.View.extend(SC.SplitChild, {
        autoResizeStyle: SC.RESIZE_AUTOMATIC,
        sizeOffset:-2,
        positionOffset:3,
        canCollapse:NO,

        childViews: ['mapView', 'layersMenuView', 'scenarioEditResultView', 'rightSidebarView', 'rightSidebarButtonsView'],

        mapView: Footprint.MapSectionView,

        /***
         * The layer ordering view that slides over the map.
         * This view will be moved to the main layer view on the left
         */
        layersMenuView: Footprint.VisibleLayerSectionView.extend({
            layout: { width: 250, borderRight: 1, top:25 },
            isVisible: NO,
            isVisibleBinding: 'F.layersVisibleController.layersMenuSectionIsVisible',
            transitionShow: SC.View.SLIDE_IN,
            transitionShowOptions: { duration: 0.2 },
            transitionHide: SC.View.SLIDE_OUT,
            transitionHideOptions: { direction: 'left', duration: 0.2 }
        }),

        /***
         * The stats on the bottom center of the map
         */
        scenarioEditResultView: Footprint.ScenarioEditResultView.extend({
            layout: {left: 100, right: 375, borderBottom: 1, bottom: 0, height: 60},
            editSectionIsVisibleBinding: SC.Binding.oneWay('F.mainPaneButtonController.editSectionIsVisible'),
            activeLayerBinding: SC.Binding.oneWay('F.layerActiveController.content'),
            activeScenarioBinding: SC.Binding.oneWay('F.scenarioActiveController.content'),
            isVisible: function () {
                if (this.getPath('activeLayer') &&
                    this.getPath('activeLayer.db_entity.feature_behavior.behavior.key') ==
                    'behavior__scenario_end_state' && this.get('editSectionIsVisible')) {
                    return YES
                }
                else {
                    return NO
                }
            }.property('activeLayer', 'editSectionIsVisible', 'activeScenario').cacheable(),
            transitionShow: SC.View.SLIDE_IN,
            transitionShowOptions: {direction: 'left', duration: 0.25},
            transitionHide: SC.View.SLIDE_OUT,
            transitionHideOptions: {direction: 'right', duration: 0.25}
        }),

        rightSidebarView: Footprint.RightSidebarView.extend({
            layout: {width: 350, right: 0, borderLeft: 1, top: 25},
            // Only make the this view visible if one of its section_views is visible
            isVisibleBinding: SC.Binding.oneWay('F.mainPaneButtonController.anySectionVisible')
        }),

        // The right sidebar buttons that open/close the various right sidebar section_views
        rightSidebarButtonsView: Footprint.RightSidebarButtonsView.extend({
            layout: {top: 30, height:260, width: 20, right: 0}
        })
    })
});
