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



Footprint.StyleValueSliderInfoView = SC.View.extend(SC.ContentValueSupport, {
    childViews: ['titleView', 'sliderView', 'valueView'],
    layout: {height: 24},
    content: null,
    title: null,
    /**
     * The step between values on the slider
     */
    step: .1,
    /***
     * The minimum slider value
    */
    minimum: 0,
    /***
     * The maximum slider value. Defaults to 1
     */
    maximum: 1,

    titleView: SC.LabelView.design({
        classNames: ['slider-title'],
        layout: { left: 0, width: 70},
        localize: true,
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),
    sliderView: SC.SliderView.design({
        layout: { left: 82, right: 45},
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),
        stepBinding: SC.Binding.oneWay('.parentView.step'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    }),
    valueView: SC.LabelView.design({
        classNames: ['slider-value'],
        layout: { right: 0, width: 35},
        rawValue: null,
        rawValueBinding: SC.Binding.oneWay('.parentView.sliderView.value'),
        step: null,
        stepBinding: SC.Binding.oneWay('.parentView.sliderView.step'),
        displayValue: null,
        displayValueBinding: SC.Binding.oneWay('.parentView.sliderView.displayValue'),
        minimum: null,
        minimumBinding: SC.Binding.oneWay('.parentView.minimum'),
        maximum: null,
        maximumBinding: SC.Binding.oneWay('.parentView.maximum'),
        /***
         * Return the displayValue with a percent if it represents one. Else return the regular value
         */
        value: function() {
            return this.get('minimum')==0 && this.get('maximum')==1 ?
                '%@%'.fmt(this.get('displayValue')) :
                (this.get('rawValue') || 0).toFixed(1)
        }.property('displayValue', 'minimum', 'maximum').cacheable(),

        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled')
    })
});
