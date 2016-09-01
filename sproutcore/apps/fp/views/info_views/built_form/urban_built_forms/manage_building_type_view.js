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
sc_require('views/info_views/built_form/editable_built_form_top_view');
sc_require('views/info_views/built_form/urban_built_forms/editable_buildings_of_building_type_view');
sc_require('views/info_views/built_form/urban_built_forms/built_form_summary_attributes_view');
sc_require('views/info_views/built_form/urban_built_forms/placetypes_using_building_type_view');
sc_require('views/info_views/built_form/editable_built_forms_select_view');
sc_require('views/info_views/info_pane_crud_buttons_view');
sc_require('views/info_views/built_form/built_form_style_picker_view');
sc_require('views/info_views/built_form/manage_built_form_view');

Footprint.ManageBuildingTypeView= Footprint.ManageBuiltFormView.extend(SC.ActionSupport,{
    classNames: ['footprint-add-building-type-view'],
    layout: {top:27},

    childViews:['editableBuiltFormsSelectView', 'overlayView', 'builtFormTopView', 'editableBuildingsOfBuildingTypeView', 'placetypesUsingBuildingTypeView', 'buildingTypeSummaryAttributesView', 'toggleButtonsView', 'builtFormColorPickerView'],

    recordType: Footprint.BuildingType,
    recordsEditControllerBinding: SC.Binding.oneWay('Footprint.buildingTypesEditController'),

    editableBuiltFormsSelectView: Footprint.EditableBuiltFormsFullListView.extend({
        layout: { left:10, width:330, bottom: 40, top: 0, zIndex: 1},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        selectionBinding: SC.Binding.from('.parentView.selection')
    }),

    overlayView: Footprint.OverlayView.extend({
        layout: { left:10, width:330, bottom: 40, top: 20, zIndex:9999},
        contentBinding: SC.Binding.from('.parentView.content'),
        statusBinding:SC.Binding.oneWay('*content.status')
    }),

    builtFormTopView: Footprint.EditableBuiltFormTopView.extend({
        layout: {left: 330, height:70, top: 0, width: 650},
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        contentBinding: SC.Binding.from('.parentView.selectedItem'),
        title: 'Building Type:'
    }),

    editableBuildingsOfBuildingTypeView: Footprint.EditableBuildingsOfBuildingTypeView.extend({
        layout: {top:70, height: 330, left: 340, right: 270},
        contentBinding: SC.Binding.from('.parentView*selectedItem.primary_component_percents')
    }),

    builtFormColorPickerView: Footprint.BuiltFormStylePickerView.extend({
        layout: { top: 400, bottom: 60, left: 340, right: 280 },
        contentBinding: SC.Binding.from('.parentView*selectedItem')
    }),

    buildingTypeSummaryAttributesView: Footprint.BuiltFormSummaryAttributesView.extend({
        layout: {width: 230, height: 400, right: 10},
        editController: Footprint.buildingTypesEditController,
        componentPercentObserverBinding: SC.Binding.oneWay('Footprint.buildingTypesEditController.updateSummaryAttributes'),
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem'),
        componentType: 'primary_component',
        statusBinding: SC.Binding.oneWay('.parentView*selectedItem.primary_component_percents.status')
    }),

    placetypesUsingBuildingTypeView: Footprint.PlacetypesUsingPlacetypeComponentView.extend({
        layout: {left: 1000, top: 0.7, bottom: 10},
        title: 'Place Types Using Building Type',
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem')
    })
});
