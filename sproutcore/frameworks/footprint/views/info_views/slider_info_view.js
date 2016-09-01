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



Footprint.SliderInfoView = SC.View.extend({
    childViews: 'titleView symbolView labelView sliderView'.w(),
    classNames: ['slider-item'],
    valueSymbol: '%',
    title: 'Title',
    minimum: 0,
    maximum: 1,
    step: .01,
    value:null,
    displayValue: null,
    inputLayout: null,
    symbolLayout: null,
    sliderLayout: null,
    labelLayout: null,
    isEditable: YES,

    titleView: SC.LabelView.design({
        classNames: ['slider-item-title'],
        layoutBinding: SC.Binding.from('.parentView.labelLayout'),
        localize: true,
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    symbolView: SC.LabelView.design({
        classNames: ['slider-item-symbol-label'],
        layoutBinding: SC.Binding.from('.parentView.symbolLayout'),
        valueBinding: SC.Binding.from('.parentView.valueSymbol')
    }),

    labelView: Footprint.EditableModelStringView.design({
        classNames: ['slider-item-value-label', 'footprint-editable-content-11px-view'],
        layoutBinding: SC.Binding.from('.parentView.inputLayout'),
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.from('.parentView.value'),
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable')
    }),

    sliderView: SC.SliderView.design({
        classNames: ['slider-item-slider'],
        layoutBinding: SC.Binding.from('.parentView.sliderLayout'),
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),
        stepBinding: SC.Binding.oneWay('.parentView.step'),
        valueBinding: SC.Binding.from('.parentView.value'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEditable')
    })
})
