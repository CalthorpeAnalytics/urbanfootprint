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


sc_require('views/info_views/editable_text_field_view');
sc_require('views/info_views/attribute_editing/editable_attribute_group_field_views');
sc_require('views/info_views/attribute_editing/editable_layer_info_view');


Footprint.CityBoundaryEditorView = SC.View.extend({
    classNames: ['footprint-jurisdiction-boundary-editor-view'],
    childViews: ['basic12DemographicsView', 'basic20DemographicsView', 'basic35DemographicsView',
        'basic40DemographicsView', 'commentView'],

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),

    basic12DemographicsView: Footprint.EditablePopHhEmpAttributeGroupView.extend({
        childViews: ['titleView', 'popView', 'hhView', 'empView'],
        layout: {height: 65, left: 10, right: 30, top: 20},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        popKey: 'pop12',
        hhKey: 'hh12',
        empKey: 'emp12',
        groupTitle: '2012'
    }),

    basic20DemographicsView: Footprint.EditablePopHhEmpAttributeGroupView.extend({
        childViews: ['titleView', 'popView', 'hhView', 'empView'],
        layout: {height: 65, left: 10, right: 30, top: 100},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        popKey: 'pop20',
        hhKey: 'hh20',
        empKey: 'emp20',
        groupTitle: 2020
    }),

    basic35DemographicsView: Footprint.EditablePopHhEmpAttributeGroupView.extend({
        childViews: ['titleView', 'popView', 'hhView', 'empView'],
        layout: {height: 65, left: 10, right: 30, top: 180},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        popKey: 'pop35',
        hhKey: 'hh35',
        empKey: 'emp35',
        groupTitle: 2035
    }),

    basic40DemographicsView: Footprint.EditablePopHhEmpAttributeGroupView.extend({
        childViews: ['titleView', 'popView', 'hhView', 'empView'],
        layout: {height: 65, left: 10, right: 30, top: 260},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        popKey: 'pop40',
        hhKey: 'hh40',
        empKey: 'emp40',
        groupTitle: 2040
    }),

    commentView: Footprint.EditableTextFieldView.extend({
        layout: {left: 10, right: 30, height: 100, top: 340},
        title: 'Comments',
        titleClassNames: ['footprint-bold-title-white-view'],
        titleBackgroundColor: '#3366CC',
        titleViewLayout: { height: 17, top: 0 },
        isTextArea: YES,
        isEditable:YES,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        editableContentViewLayout: { top: 17, bottom: 0 },
        contentValueKey: 'comment',
        // The controller calls propertyDidChange on this when updates finish. We use it to update value
        refreshValue: null,
        refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
        value: Footprint.pluralContentValueProperty
    })
});
