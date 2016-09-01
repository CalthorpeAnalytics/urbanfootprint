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


sc_require('views/overlay_view');
sc_require('views/info_views/analysis_module/environmental_constraint_management_view');

Footprint.ConstraintSectionView = SC.View.extend({
    classNames: ['footprint-constraint-section-view', 'footprint-map-overlay-section'],
    childViews: ['contentView', 'overlayView'],

    overlayView: Footprint.OverlayView.extend({
        contentBinding: SC.Binding.oneWay('Footprint.analysisModulesEditController.content'),
        statusBinding:SC.Binding.oneWay('*content.status')
    }),

    contentView: Footprint.EnvironmentalConstraintModuleManagementView.extend({
        layout: {top:0}
    })
});
