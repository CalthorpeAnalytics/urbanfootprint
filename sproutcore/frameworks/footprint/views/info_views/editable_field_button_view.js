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


Footprint.EditableFieldButtonView = SC.View.extend({
    layout: {height: 20, width: 100},
    childViews: ['valueView', 'buttonsView'],
    value: null,
    minimum: null,
    maximum: null,
    valueStep: null,
    validator: null,
    valueLayout: {left: 5, height: 20, right:14},
    buttonsLayout: {height: 20, width: 14, right:0},

    valueView: SC.TextFieldView.extend({
        classNames: ['footprint-11font-title-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.valueLayout'),
        valueBinding: SC.Binding.from('.parentView.value'),
        validatorBinding: SC.Binding.oneWay('.parentView.validator'),
    }),

    buttonsView: SC.View.extend({
        childViews: ['topButtonView', 'bottomButtonView'],
        layoutBinding:  SC.Binding.oneWay('.parentView.buttonsLayout'),
        valueStep: null,
        valueStepBinding: SC.Binding.oneWay('.parentView.valueStep'),
        value: null,
        valueBinding: '.parentView.valueView.value',
        minimum: null,
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximum: null,
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),

        topButtonView: SC.ImageButtonView.extend({
            layout: {height: 10},
            action: 'addValueStep',
            image: 'add-value-icon'
        }),

        bottomButtonView: SC.ImageButtonView.extend({
            layout: {top: 10},
            action: 'subtractValueStep',
            image: 'subtract-value-icon'
        }),

        addValueStep: function() {
            var max = this.get('maximum') || 0;
            var val = this.get('value') || 0;
            var valueStep = this.get('valueStep') || 0;
            this.set('value', val + valueStep <= max ? val + valueStep : max)
        },

        subtractValueStep: function() {
            var min = this.get('minimum') || 0;
            var val = this.get('value') || 0;
            var valueStep = this.get('valueStep') || 0;
            this.set('value', val - valueStep >= min ? val - valueStep : min)
        }
    })
});
