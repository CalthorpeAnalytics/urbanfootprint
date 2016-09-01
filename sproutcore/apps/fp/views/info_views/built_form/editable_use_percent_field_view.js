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

sc_require('views/editable_model_string_view');



Footprint.EditableUsePercentFieldView = SC.View.extend(SC.Control, {
    classNames: ['footprint-editable-use-percent-field-view'],
    childViews: ['nameView', 'sqftUnitView', 'efficiencyView', 'percentView'],
    content: null,

    // Editing of BuiltForms is disabled
    /*
    removeButtonView: Footprint.DeleteButtonView.extend({
        layout: { left: 1, width: 16, top: 1, height: 16},
        action: 'doRemoveRecord',
        contentBinding: SC.Binding.oneWay('.parentView.content')
    }),
    */
    nameView: SC.LabelView.extend({
        layout: {width:190, top: 1, left: 26, height: 19},
        contentBinding: SC.Binding.oneWay('.parentView*content.building_use_definition'),
        contentValueKey: 'name'
    }),
    sqftUnitView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        // Editing of BuiltForms is disabled
        isEditable: NO,
        layout: {width: 60, left:.2, top: 20, height: 16},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'square_feet_per_unit'
    }),
    efficiencyView: SC.View.extend({
        layout: {width: 60, left:.5, top: 20, height: 18},
        childViews:['editablePercentView', 'percentLabel'],
        content: null,
        contentBinding: SC.Binding.from('.parentView.content'),

        editablePercentView: Footprint.EditableFloatFieldItemView.extend({
            classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
            // Editing of BuiltForms is disabled
            isEditable: NO,
            layout: {width: 0.8},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'efficiency',
            isPercent: YES
        }),
        percentLabel: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left:.8, top: 3, bottom: 1},
            textAlign: SC.ALIGN_CENTER,
            value: '%'
        })
    }),
    percentView: SC.View.extend({
        layout: {width: 60, right: 0, top: 20, height: 18},
        childViews:['editablePercentView', 'percentLabel'],
        content: null,
        contentBinding: SC.Binding.from('.parentView.content'),

        editablePercentView: Footprint.EditableFloatFieldItemView.extend({
            classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
            // Editing of BuiltForms is disabled
            isEditable: NO,
            layout: {width: 0.8},
            textAlign: SC.ALIGN_CENTER,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'percent',
            isPercent: YES
        }),
        percentLabel: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 0.8, top: 3, bottom: 1},
            textAlign: SC.ALIGN_CENTER,
            value: '%'
        })
    })
});

Footprint.NonEditableBottomLabelledView = SC.View.extend(SC.ContentDisplay, {
    classNames: ['footprint-bottom-labelled-view'],
    childViews:'nameTitleView contentView'.w(),
    status: null,
    title: null,
    content:null,
    contentValueKey: null,
    layout: null,

    nameTitleView: SC.LabelView.extend({
        classNames: ['footprint-10font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {top:0.6}
    }),
    contentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-noneditable-bottom-labelled-content-view'],
        classNameBindings: ['positiveNegative:is-negative'],
        positiveNegative: function() {
            return this.get('value') < 0
        }.property('value').cacheable(),
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        layout: {height:.5},
        isEditable: NO
    })
});
