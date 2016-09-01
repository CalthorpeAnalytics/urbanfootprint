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


sc_require('views/info_views/built_form/editable_input_field_view');
sc_require('views/info_views/built_form/urban_built_forms/built_form_summary_field_view');

Footprint.CropSummaryFieldView = SC.View.extend({
    classNames: ['footprint-summary-field-view'],
    childViews:'nameTitleView contentView'.w(),
    content: null,
    status: null,
    editController: null,
    summaryProperty: null,
    title: null,
    attributeStatus: null,
    componentSummaryObserver: null,
    titleTextAlignment: SC.ALIGN_CENTER,

    nameTitleView: SC.LabelView.extend({
        textAlignBinding: SC.Binding.oneWay('.parentView.titleTextAlignment'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {width:.65},
        backgroundColor: '#99CCFF'
    }),

    contentView: SC.LabelView.extend({
        classNames: ['footprint-noneditable-bottom-labelled-content-view'],
        classNameBindings: ['positiveNegative:is-negative'],
        positiveNegative: function() {
            return this.get('value') < 0
        }.property('value').cacheable(),
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.oneWay('.parentView.computedValue').transform(function(value) {
            if (value) {
                return value.toFixed(2)}
            else
                return 0
        }),
        layout: {left:.65}
    })
});

Footprint.AgricultureSummaryAttributesView = SC.View.extend({
    classNames: ['footprint-agriculture-summary-attributes-view'],
    childViews:['titleView', 'cropYieldView', 'unitPriceView', 'totalCostView', 'waterConsumptionView',
        'laborInputView', 'truckTripsView' ],
    editController: null,
    componentPercentObserver: null,
    content: null,

    titleView: SC.LabelView.extend({
        layout: {top: 20, left: 10, height:18},
        value: 'Aggregated Attributes'
    }),

    cropYieldView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 50, left: 10, height:18},
        title: 'Crop Yield (tons/acre)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.crop_yield'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'crop_yield')
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.crop_yield');
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    }),

    unitPriceView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 75, left: 10, height:18},
        title: 'Unit Price ($/ton)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.unit_price'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'unit_price');
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.unit_price')
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    }),

    costView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 100, left: 10, height:18},
        title: 'Production costs ($/acre)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.cost'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'cost')
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.cost')
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    }),

    waterConsumptionView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 125, left: 10, height:18},
        title: 'Water Use (ac-ft / acre)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.water_consumption'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'water_consumption')
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.water_consumption')
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    }),

    laborInputView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 150, left: 10, height:18},
        title: 'Labor Input (FTE / acre)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.labor_input'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'labor_input')
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.labor_input')
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    }),

    truckTripsView: Footprint.CropSummaryFieldView.extend({
        layout: {top: 175, left: 10, height:18},
        title: 'Truck Trips (per acre)',
        editControllerBinding: SC.Binding.oneWay('.parentView.editController'),
        componentSummaryObserverBinding: SC.Binding.oneWay('.parentView.componentPercentObserver'),
        summaryPropertyBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.truck_trips'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('*content.status'),
        attributeStatusBinding: SC.Binding.oneWay('*content.agriculture_attribute_set.status'),

        computedValueObserver: function() {

            if (this.get('status' != SC.Record.READY_DIRTY && status != SC.Record.READY_NEW)) {
                return
            }
            if (this.get('content')) {
                updateAgricultureAttribute(this.get('content'), 'truck_trips')
            }
            if (this.get('componentSummaryObserver') == YES) {
                editController.set('updateSummaryAttributes', NO);
            }
        }.observes('content', 'componentSummaryObserver', 'status', 'attributeStatus'),

        computedValue: function() {
            if (this.getPath('content.status') & SC.Record.READY) {
                return this.getPath('content.agriculture_attribute_set.truck_trips')
            }
        }.property('summaryProperty', 'attributeStatus').cacheable()
    })
});



updateAgricultureAttribute = function(content, field) {

    var weighted_density = 0.0;
    var component_percents = content.get('component_percents');
    var cotainer_attribute_set = content.get('agriculture_attribute_set');

    if (component_percents) {
        component_percents.forEach(function(component_percent) {
            if (component_percent.get('percent'))
                var percent = component_percent.get('percent');
            else
                var percent = 0;
            var component = component_percent.getPath('subclassedComponent.agriculture_attribute_set');

            if (component && component.get(field))
                var density = component.get(field);
            else
                var density = 0;

            var percent_density = percent * density;

            weighted_density = weighted_density + percent_density;

        });
        if (weighted_density < 0 || weighted_density > 0 || weighted_density == 0) {
            if (cotainer_attribute_set && cotainer_attribute_set.get('status') & SC.Record.READY) {
                cotainer_attribute_set.setIfChanged(field, weighted_density);
            }
        };
    }
};
