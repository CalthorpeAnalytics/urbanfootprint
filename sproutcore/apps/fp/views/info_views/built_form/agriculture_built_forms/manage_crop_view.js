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
sc_require('views/info_views/built_form/agriculture_built_forms/editable_agriculture_attribute_set_view');
sc_require('views/info_views/built_form/editable_built_form_top_view');
sc_require('views/info_views/built_form/editable_built_forms_select_view');
sc_require('views/info_views/built_form/manage_built_form_view');
sc_require('views/action_views/normalize_percents_button_view');

/***
 * The pane used to edit the settings of a new or existing BuiltForm and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the BuiltForm if a DbEntity is being created here
 * @type {*}
 */
Footprint.ManageCropView = Footprint.ManageBuiltFormView.extend({
    classNames: ['footprint-add-crop-view'],
    layout: {top:27},

    childViews: [
        'editableBuiltFormsSelectView',
        'overlayView',
        'builtFormTopView',
        'editableAgricultureAttributesView',
        'toggleButtonsView'
    ],

    recordType: Footprint.Crop,
    recordsEditControllerBinding: SC.Binding.oneWay('Footprint.cropsEditController'),

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
        layout: {left: 340, height:70, top: 0, width: 650},
        recordTypeBinding: SC.Binding.oneWay('.parentView.recordType'),
        contentBinding: SC.Binding.oneWay('.parentView.selectedItem'),
        title: 'Crop Name:'
    }),
    // TODO not binding correctly with nested store
    editableAgricultureAttributesView: Footprint.EditableAgricultureAttributeSetView.extend({
        layout: {left: 340, bottom:40, top: 70, width: 800},
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem.agriculture_attribute_set'),
        allContentBinding: SC.Binding.oneWay('.parentView.selectedItem')
    })
});
