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


sc_require('views/section_views/analysis_module_section_view');
sc_require('views/section_views/layer_section_view');
sc_require('views/section_views/edit_section_view');
sc_require('views/section_views/constraint_section_view');
sc_require('views/section_views/scenario_edit_result_view');

/**
 * The sidebar on the right that can show analysis, editors, and the new query ui
 */
Footprint.RightSidebarView = SC.View.extend({
    childViews: ['modulesView', 'editorsView', 'constraintsView'],
    classNames: ['footprint-right-sidebar-view'],

     /***
     * This is the section that pops out when the user hits the Analysis tab
     */
     modulesView: Footprint.AnalysisModuleSectionView.extend({
         isVisible: NO,
         isVisibleBinding: 'F.mainPaneButtonController.analysisModuleSectionIsVisible',
         transitionShow: SC.View.SLIDE_IN,
         transitionShowOptions: {direction: 'left', duration: 0.2},
         transitionHide: SC.View.SLIDE_OUT,
         transitionHideOptions: {duration: 0.2}
     }),

     /***
     * This is the section that pops out when the user hits the Editor tab
     */
     editorsView: Footprint.EditSectionView.extend({
         layout: {width: 275, right: 0, borderLeft: 1, top: 0, zIndex: 2},
         isVisible: NO,
         isVisibleBinding: 'F.mainPaneButtonController.editSectionIsVisible',
         transitionShow: SC.View.SLIDE_IN,
         transitionShowOptions: {direction: 'left', duration: 0.2},
         transitionHide: SC.View.SLIDE_OUT,
         transitionHideOptions: {duration: 0.2}
     }),

     constraintsView: Footprint.ConstraintSectionView.extend({
         layout: {width: 275, bottom: 100, right: 275, borderLeft: 1, top: 0, zIndex: 1},
         isVisible: NO,
         isVisibleBinding: 'F.mainPaneButtonController.constraintIsVisible',
         transitionShow: SC.View.SLIDE_IN,
         transitionShowOptions: {
             direction: 'left',
             duration: 0.2
         },
         transitionHide: SC.View.SLIDE_OUT,
         transitionHideOptions: {duration: 0.2}
     }),

     environmentalConstraintButtonView: SC.ButtonView.extend({
         // This button is rotated, making its layout a bit fiddly.
         layout: {top: 95, right: 235, height: 20, width: 100, rotateZ: -90, zIndex: 3},
         classNames: ['theme-button', 'theme-button-gray', 'theme-button-shorter', 'theme-button-flat-bottom'],
         valueBinding: 'Footprint.mainPaneButtonController.constraintIsVisible',
         icon: function () {
             if (this.get('value')) return sc_static('images/section_toolbars/pulldown.png');
             else return sc_static('images/section_toolbars/pullup.png')
         }.property('value').cacheable(),
         title: function () {
             if (this.get('value')) return 'Collapse';
             else return 'Constraints';
         }.property('value').cacheable(),
         buttonBehavior: SC.TOGGLE_BEHAVIOR,
         editSectionIsVisible: null,
         editSectionIsVisibleBinding: 'F.mainPaneButtonController.editSectionIsVisible',
         activeLayerBinding: 'F.layerActiveController.content',
         activeScenarioBinding: 'F.scenarioActiveController.content',
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
         transitionShowOptions: {direction: 'left', duration: 0.15},
         transitionHide: SC.View.SLIDE_OUT,
         transitionHideOptions: {direction: 'right', duration: 0.15}
     })
});
