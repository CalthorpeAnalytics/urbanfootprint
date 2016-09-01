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


Footprint.RightSidebarButtonsView = SC.View.extend({
     classNames: ['footprint-right-sidebar-button-view'],
     childViews: ['editSectionButtonView', 'analysisSectionButtonView'],

     editSectionButtonView: SC.ButtonView.extend({
         // This button is rotated, making its layout a bit fiddly.
         layout: {top: 30, height: 20, rotateZ: -90, zIndex: 3, right: -30, width: 80},
         classNames: ['theme-button', 'theme-button-gray', 'theme-button-shorter', 'theme-button-flat-bottom'],
         valueBinding: 'Footprint.mainPaneButtonController.editSectionIsVisible',
         icon: function () {
             if (this.get('value')) return sc_static('images/section_toolbars/pulldown.png');
             else return sc_static('images/section_toolbars/pullup.png')
         }.property('value').cacheable(),
         title: function () {
             if (this.get('value')) return 'Collapse';
             else return 'Editor';
         }.property('value').cacheable(),
         buttonBehavior: SC.TOGGLE_BEHAVIOR,
         // Enable the editor button if the panel is already open or the current layer is editable
         isEnabledBinding: SC.Binding.or('.value', 'Footprint.layerActiveController.layerIsEditable')
     }),

     analysisSectionButtonView: SC.ButtonView.extend({
         // This button is rotated, making its layout a bit fiddly.
         layout: {top: 115, height: 20, rotateZ: -90, zIndex: 3, right: -30, width: 80},
         classNames: ['theme-button', 'theme-button-gray', 'theme-button-shorter', 'theme-button-flat-bottom'],
         valueBinding: 'Footprint.mainPaneButtonController.analysisModuleSectionIsVisible',
         icon: function () {
             if (this.get('value')) return sc_static('images/section_toolbars/pulldown.png');
             else return sc_static('images/section_toolbars/pullup.png')
         }.property('value').cacheable(),
         title: function () {
             if (this.get('value')) return 'Collapse';
             else return 'Analysis';
         }.property('value').cacheable(),
         buttonBehavior: SC.TOGGLE_BEHAVIOR,
         rightSideContent: null,
         rightSideContentBinding: SC.Binding.oneWay('Footprint.analysisModulesRightSideEditController.content'),
         isEnabled: function() {
             if (this.get('rightSideContent') && this.getPath('rightSideContent').length > 0) {
                 return YES
             }
             return NO
         }.property('rightSideContent').cacheable()
     })

//     querySectionButtonView: SC.ButtonView.extend({
//         // This button is rotated, making its layout a bit fiddly.
//         layout: {top: 200, height: 20, rotateZ: -90, zIndex: 3, right: -30, width: 80},
//         classNames: ['theme-button', 'theme-button-gray', 'theme-button-shorter', 'theme-button-flat-bottom'],
//         valueBinding: 'Footprint.mainPaneButtonController.querySectionIsVisible',
//         icon: function () {
//             if (this.get('value')) return sc_static('images/section_toolbars/pulldown.png');
//             else return sc_static('images/section_toolbars/pullup.png')
//         }.property('value').cacheable(),
//         title: function () {
//             if (this.get('value')) return 'Collapse';
//             else return 'Query';
//         }.property('value').cacheable(),
//         buttonBehavior: SC.TOGGLE_BEHAVIOR
//     })
});
