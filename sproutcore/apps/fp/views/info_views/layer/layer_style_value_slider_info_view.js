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

sc_require('views/info_views/editable_field_button_view');


Footprint.LayerStyleValueSliderInfoView = SC.View.extend(SC.ContentValueSupport, {
    childViews: ['titleView', 'sliderView', 'valueView'],
    layout: {height: 20},
    content: null,
    title: null,
    /**
     * The step between values on the slider
     */
    step: 1,
    /***
     * The minimum slider value
    */
    minimum: 0,
    /***
     * The maximum slider value. Defaults to 1
     */
    maximum: 1,

    titleView: SC.LabelView.design({
        classNames: ['layer-slider-title'],
        layout: { left: 0, width: 15},
        localize: true,
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    sliderView: SC.SliderView.design({
        layout: { left: 25, right: 65},
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),
        stepBinding: SC.Binding.oneWay('.parentView.step'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        controlSize: SC.SMALL_CONTROL_SIZE
    }),

    valueView: Footprint.EditableFieldButtonView.design({
        layout: { right: 0, width: 55},
        valueBinding: SC.Binding.from('.parentView.sliderView.value'),
        valueStepBinding: SC.Binding.oneWay('.parentView.sliderView.step'),
        minimum: null,
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximum: null,
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),
        validator: function() {
            return SC.Validator.Number.create({places:0});
        }.property().cacheable()
    })
});
