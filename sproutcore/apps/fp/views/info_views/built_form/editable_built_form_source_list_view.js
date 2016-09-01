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


sc_require('views/info_views/built_form/editable_input_field_view');

Footprint.EditableBuiltFormSourceListView = SC.View.extend(SC.Control, {
    classNames: ['footprint-built-form-percent-list-scroll-view'],
    layout: { height: 24 },
    childViews: ['nameLabelView', 'residentialChartView', 'dwellingUnitLabelView', 'employmentLabelView', 'percentView'],
    // Content is what we are editing, which is a BuildingTypeComponentPercent instance a PlacetypeComponentPercent instance, or similar
    content: null,
    subclassedContent: null,

    // BuiltForm editing disabled
    /*
    removeButtonView: Footprint.DeleteButtonView.extend({
        layout: { left: 2, width: 16, top: 2, height: 16},
        action: 'doRemoveRecord',
        contentBinding: SC.Binding.oneWay('.parentView.content')
    }),
    */

    nameLabelView: SC.LabelView.extend({
        layout: { left: 25, height: 18, top: 2 },
        valueBinding: SC.Binding.oneWay('.parentView*subclassedContent.name')
    }),

    dwellingUnitLabelView: SC.LabelView.extend({
        layout: { right: 135, width:45, height: 20},
        rawData: null,
        rawDataBinding: SC.Binding.oneWay('.parentView*subclassedContent.flat_building_densities.dwelling_unit_density'),
        value: function(){
            return parseFloat(this.get('rawData')).toFixed(1);
        }.property('rawData').cacheable(),
        backgroundColor: '#F0F8FF',
        textAlign: SC.ALIGN_CENTER
    }),
    employmentLabelView: SC.LabelView.extend({
        layout: { right: 90, width:45, height: 20 },
        rawData: null,
        rawDataBinding: SC.Binding.oneWay('.parentView*subclassedContent.flat_building_densities.employment_density'),
        value: function(){
            return parseFloat(this.get('rawData')).toFixed(1);
        }.property('rawData').cacheable(),
        backgroundColor: '#F0F8FF',
        textAlign: SC.ALIGN_CENTER
    }),

    percentView: Footprint.EditableFloatFieldItemView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        // Editing of BuiltForms is disabled
        isEditable: NO,
        layout: { right: 0, width: 90, height: 20},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'percent',
        isPercent: YES,
        // Limit percent decimal places to 2
        validator: function() {
            return SC.Validator.Number.create({places:2});
        }.property().cacheable()
    })
});
