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
sc_require('views/info_views/built_form/agriculture_built_forms/editable_buildings_of_building_type_view');
sc_require('views/info_views/built_form/agriculture_built_forms/built_form_summary_attributes_view');
sc_require('views/info_views/built_form/placetypes_using_placetype_component_view');
sc_require('views/info_views/built_form/editable_built_forms_select_view');
sc_require('views/info_views/info_pane_crud_buttons_view');
sc_require('views/info_views/built_form/built_form_style_picker_view');
sc_require('views/info_views/built_form/manage_built_form_view');

Footprint.ManageCropTypeView= Footprint.ManageBuiltFormView.extend(SC.ActionSupport,{
    classNames: ['footprint-add-building-type-view'],
    layout: {top:27},

    childViews:[
        'editableBuiltFormsSelectView',
        'overlayView',
        'builtFormTopView',
        'editableCropsOfCropTypeView',
        'landscapeTypesUsingCropTypeView',
        'cropTypeSummaryAttributesView',
        'toggleButtonsView',
        'builtFormColorPickerView'
    ],

    recordType: Footprint.CropType,
    recordsEditControllerBinding: SC.Binding.oneWay('Footprint.cropTypesEditController'),

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
        contentBinding: SC.Binding.oneWay('.parentView.selectedItem'),
        title: 'CropType:'
    }),

    editableCropsOfCropTypeView: Footprint.EditableCropsOfCropTypeView.extend({
        title:"Crops in CropType",
        layout: {top:70, height: 225, left: 340, right: 280},
        contentBinding: SC.Binding.from('.parentView*selectedItem.primary_component_percents')
    }),

    builtFormColorPickerView: Footprint.BuiltFormStylePickerView.extend({
        layout: { top: 310, bottom: 60, left: 340, right: 280 },
        contentBinding: SC.Binding.from('.parentView*selectedItem')
    }),

    cropTypeSummaryAttributesView: Footprint.AgricultureSummaryAttributesView.extend({
        layout: {left: 970, width: 260, height: 0.6},
        editController: Footprint.cropTypesEditController,
        componentPercentObserverBinding: SC.Binding.oneWay('Footprint.cropTypesEditController.updateSummaryAttributes'),
        contentBinding: SC.Binding.oneWay('.parentView.selectedItem')
    }),

    landscapeTypesUsingCropTypeView: Footprint.PlacetypesUsingPlacetypeComponentView.extend({
        title: "LandcapeTypes Using CropType",
        layout: {left: 970, top: 0.55, bottom: 50, width: 260},
        contentBinding: SC.Binding.oneWay('.parentView.selectedItem')
    })
});
