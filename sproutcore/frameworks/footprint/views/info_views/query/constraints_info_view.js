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


sc_require('views/info_views/toggle_button_info_view');

Footprint.ConstraintsInfoView = SC.View.extend({
    childViews:'constrainToBoundsButtonInfoView'.w(),
    classNames:'footprint-query-info-constraints-view'.w(),
    // The LayerSelection instance
    content: null,
    nonGeographicLimitationsExist: null,

    constrainToBoundsButtonInfoView: Footprint.ToggleButtonInfoView.extend({
        layout: {left: 50, height: 20, top: 10},
        classNames:'footprint-query-info-constrain-to-bounds-button-info-view'.w(),
        // Only enable this toggle if filters and/or joins are specified
        isEnabledBinding: SC.Binding.and('.parentView.isEnabled', '.parentView.nonGeographicLimitationsExist'),
        // Hiding this view when there is no selection
        isVisibleBinding: SC.Binding.oneWay('.parentView*content.bounds.coordinates.length').bool(),
        title: function() {
            return this.get('isEnabled') ?
                'Limit Results to Selected Area' :
                'Results Limited to Selected Area';
        }.property('isEnabled').cacheable(),
        toolTip: function() {
            return this.get('isEnabled') ?
                'When checked, limits results to the selected area on the map in addition to the above filters' :
                'Enabled only when filters or joins are specified above';
        }.property('isEnabled').cacheable(),
        contentBinding: '.parentView*content.selection_options',
        contentValueKey: 'constrain_to_bounds',
        // Query immediately when this is checked or unchecked
        action:'doExecuteQuery'
    })
});
