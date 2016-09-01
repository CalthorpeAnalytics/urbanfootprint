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

sc_require('views/info_views/geography_info_view');
sc_require('views/info_views/tags_info_view');
sc_require('views/info_views/medium_info_view');
sc_require('views/section_views/built_form_section_view');
sc_require('views/info_views/color_info_view');
sc_require('models/built_form_models');
sc_require('views/info_views/built_form/urban_built_forms/editable_building_attribute_set_view');
sc_require('views/info_views/built_form/urban_built_forms/editable_building_top_view');
sc_require('views/info_views/built_form/urban_built_forms/building_summary_attributes_view');
sc_require('views/info_views/built_form/editable_built_forms_select_view');
sc_require('views/info_views/built_form/placetype_components_using_primary_component_view');
sc_require('views/info_views/info_pane_crud_buttons_view');
sc_require('views/info_views/built_form/manage_built_form_view');
sc_require('views/info_views/built_form/urban_built_forms/building_donut_chart_view');

/***
 * The pane used to edit the settings of a new or existing BuiltForm and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the BuiltForm if a DbEntity is being created here
 * @type {*}
 */
Footprint.ManageBuildingView = Footprint.ManageBuiltFormView.extend({
    classNames: ['footprint-add-building-view'],
    layout: {top:27},
    childViews:['overlayView', 'editableBuiltFormsSelectView', 'builtFormTopView', 'buildingChartsView', 'editableBuildingAttributesView', 'buildingSummaryAttributesView', 'toggleButtonsView', 'buildingTypesUsingBuildingView', 'buttonsView', 'buildingUseLabelSelectView'],

    recordType: Footprint.Building,
    recordsEditControllerBinding: SC.Binding.oneWay('Footprint.buildingsEditController'),

    overlayView: Footprint.OverlayView.extend({
        layout: { left:0, top: 0, zIndex:9999},
        contentBinding: SC.Binding.from('.parentView*selectedItem.flat_building_densities'),
        statusBinding: SC.Binding.oneWay('*content.status')
    }),

    editableBuiltFormsSelectView: Footprint.EditableBuiltFormsFullListView.extend({
        layout: { left:10, width:330, bottom: 40, top: 0, zIndex: 1},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        selectionBinding: SC.Binding.from('.parentView.selection')
    }),

    builtFormTopView: Footprint.EditableBuildingTopView.extend({
        layout: {left: 330, height:52, top: 0, width: 650},
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        contentBinding: SC.Binding.oneWay('.parentView.selectedItem')
    }),

    editableBuildingAttributesView: Footprint.EditableBuildingAttributeSetView.extend({
        layout: {left: 330, bottom:240, top: 52, width: 680},
        contentBinding: SC.Binding.from('.parentView*selectedItem.building_attribute_set'),
        selectedItemBinding: SC.Binding.from('.parentView.selectedItem')
    }),

    buildingChartsView: SC.View.extend({
        layout: {left: 350, bottom:10, height:230, width: 650},

        childViews: ['parcelCompTitleView', 'buildingDonutChartView', 'buildingCompTitleView', 'buildingCompositionDonutChartView'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem.building_attribute_set'),
        selectedItem: null,
        selectedItemBinding: SC.Binding.oneWay('.parentView.selectedItem'),


        parcelCompTitleView: SC.LabelView.extend({
            classNames: ['footprint-bold-title-view'],
            value: 'Parcel Composition',
            layout: {height: 20, left: 50, top:10}
        }),

        buildingDonutChartView: Footprint.buildingParcelAreaChartView.extend({
            layout: {left: 70, height:200, width: 200, top: 20},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selectedItemBinding: SC.Binding.oneWay('.parentView.selectedItem')
        }),

        buildingCompTitleView: SC.LabelView.extend({
            classNames: ['footprint-bold-title-view'],
            value: 'Building Use Mix',
            layout: {height: 20, left: 310, top:10}
        }),

        buildingCompositionDonutChartView: Footprint.builtFormCompositionAreaChartView.extend({
            layout: {left: 340, height:200, width: 200, top: 20},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selectedItemBinding: SC.Binding.oneWay('.parentView.selectedItem')
        })
    }),

    buildingTypesUsingBuildingView: Footprint.PlacetypeComponentsUsingPrimaryComponentView.extend({
        title: "Building Types Using Building",
        layout: {left: 1000, top: 0.7, bottom: 10},
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem')
    }),

    buildingSummaryAttributesView: Footprint.BuildingSummaryAttributesView.extend({
        layout: {width: 230, height: 400, right: 10},
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem')
    })
});
