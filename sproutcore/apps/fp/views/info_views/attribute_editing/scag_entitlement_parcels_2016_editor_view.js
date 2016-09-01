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

sc_require('views/info_views/select_info_view');
sc_require('views/info_views/editable_text_field_view');

Footprint.EntitlementParcels2016EditorView = SC.View.extend({
    classNames: ['footprint-entitlement-editor-view'],
    childViews: ['scrollView'],

    scrollView: SC.ScrollView.extend({
        classNames: ['footprint-map-overlay-editor'],
        verticalOverlay: true,
        autoHidesVerticalScroller: false,

        contentView: SC.View.extend({
            layout: {left: 0, right: 0, top:0, height: 612},

            childViews: ['tractNumberView', 'devAgreementView', 'addressView', 'dateApprovalView', 'dateStartView', 'multiParcelsView',
                'projTypeView', 'popView', 'sfUnitView', 'mfUnitView', 'empView', 'empTypeView', 'empSquareFeetView',
                'projPhaseView','timeLimitationView', 'commentView'],

            activeLayer: null,
            activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

            content: null,
            contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),

            tractNumberView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 112, top: 20, height: 40},
                title: 'Tract Number',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'tract_no',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            devAgreementView: Footprint.EditableTextFieldView.extend({
                layout: {left: 132, right: 30, top: 20, height: 40},
                title: 'Dev Agreement No.',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'dev_agmt',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            addressView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, right: 30, top: 80, height: 40},
                title: 'Address',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'address',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            dateApprovalView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 112, top: 140, height: 40},
                title: 'Approval Date',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'date_appro',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),


            dateStartView: Footprint.EditableTextFieldView.extend({
                layout: {left: 132, right: 30, top: 140, height: 40},
                title: 'Start Date',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'date_start',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            multiParcelsView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 112, top: 200, height: 40},
                title: 'Multiple Parcels',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'multi_par',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            projTypeView: Footprint.EditableTextFieldView.extend({
                layout: {left: 132, right: 30, top: 200, height: 40},
                title: 'Project Type',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'proj_type',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            popView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 70, top: 260, height: 40},
                title: 'Population',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'pop',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),


            sfUnitView: Footprint.EditableTextFieldView.extend({
                layout: {left: 87, width: 70, top: 260, height: 40},
                title: 'SF Unit #',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'du_sf',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),


            mfUnitView: Footprint.EditableTextFieldView.extend({
                layout: {left: 164, right: 30, top: 260, height: 40},
                title: 'MF Unit #',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'du_mf',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            empView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 70, top: 320, height: 40},
                title: 'Employment',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'emp',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            empTypeView: Footprint.EditableTextFieldView.extend({
                layout: {left: 87, width: 70, top: 320, height: 40},
                title: 'Emp Type',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'emp_type',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            empSquareFeetView: Footprint.EditableTextFieldView.extend({
                layout: {left: 164, right: 30, top: 320, height: 40},
                title: 'Emp Sq Feet',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'emp_sqft',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            projPhaseView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, width: 112, top: 380, height: 40},
                title: 'Project Phase',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'proj_phase',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            timeLimitationView: Footprint.EditableTextFieldView.extend({
                layout: {left: 132, right: 30, top: 380, height: 40},
                title: 'Time Limitation',
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                titleViewLayout: { height: 16 },
                editableContentViewLayout: { top: 17 },
                titleClassNames: ['footprint-bold-title-white-view'],
                contentValueKey: 'time_limit',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
                backgroundColor: '#3366CC',
            }),

            commentView: Footprint.EditableTextFieldView.extend({
                layout: {left: 10, right: 30, height: 100, top: 440},
                title: 'Notes',
                titleClassNames: ['footprint-bold-title-white-view'],
                titleBackgroundColor: '#3366CC',
                titleViewLayout: { height: 17, top: 0 },
                isTextArea: YES,
                isEditable:YES,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                editableContentViewLayout: { top: 17, bottom: 0 },
                contentValueKey: 'notes',
                // The controller calls propertyDidChange on this when updates finish. We use it to update value
                refreshValue: null,
                refreshValueBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsDidUpdate'),
                value: Footprint.pluralContentValueProperty,
            }),
        }),
    }),
});
