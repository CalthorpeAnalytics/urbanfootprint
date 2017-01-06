/*
 * UrbanFootprint v1.5
 * Copyright (C) 2017 Calthorpe Analytics
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
sc_require('properties/plural_property');

Footprint.EditablePopHhEmpAttributeGroupView = SC.View.extend({
    childViews: ['titleView', 'popView', 'hhView', 'empView'],

    backgroundColor: 'lightblue',
    content: null,
    popKey: null,
    hhKey: null,
    empKey: null,
    groupTitle: null,


    titleView: SC.LabelView.extend({
        classNames: "footprint-bold-title-white-view".w(),
        layout: {height: 16},
        textAlign: SC.ALIGN_CENTER,
        backgroundColor: '#3366CC',
        valueBinding: SC.Binding.oneWay('.parentView.groupTitle')
    }),

    popView: Footprint.EditableTextFieldView.extend({
        layout: {left: 5, width: 70, top: 20, height: 40},
        title: 'Population',
        isEditable:YES,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        titleViewLayout: { top: 26, height: 16 },
        editableContentViewLayout: { height: 20 },
        titleClassNames: ['footprint-editable-9font-title-view'],
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.popKey'),
        // The controller calls propertyDidChange on this when updates finish. We use it to update value
        refreshValue: null,
        refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
        value: Footprint.pluralContentValueProperty,
        isNumber: YES
    }),

    hhView: Footprint.EditableTextFieldView.extend({
        layout: {width: 70, top: 20, left: 82, height: 40},
        title: 'Households',
        isEditable:YES,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        titleViewLayout: { top: 26, height: 16 },
        editableContentViewLayout: { height: 20 },
        titleClassNames: ['footprint-editable-9font-title-view'],
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.hhKey'),
        // The controller calls propertyDidChange on this when updates finish. We use it to update value
        refreshValue: null,
        refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
        value: Footprint.pluralContentValueProperty,
        isNumber: YES
    }),

    empView: Footprint.EditableTextFieldView.extend({
        layout: {width: 70, top: 20, right: 5, height: 40},
        title: 'Employees',
        isEditable:YES,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        titleViewLayout: { top: 26, height: 16 },
        editableContentViewLayout: { height: 20 },
        titleClassNames: ['footprint-editable-9font-title-view'],
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.empKey'),
        // The controller calls propertyDidChange on this when updates finish. We use it to update value
        refreshValue: null,
        refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
        value: Footprint.pluralContentValueProperty,
        isNumber: YES
    })
});
