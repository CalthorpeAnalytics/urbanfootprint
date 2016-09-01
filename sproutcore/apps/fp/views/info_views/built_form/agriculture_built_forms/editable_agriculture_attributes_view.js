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
sc_require('views/info_views/built_form/placetype_components_using_primary_component_view');


Footprint.EditableFieldMediumTitleView = SC.View.extend(SC.Control, {
    classNames: ['footprint-editable-view'],
    childViews: 'nameTitleView contentView'.w(),
    title: null,
    content: null,
    contentValueKey: null,
    layout: null,
    isPercent: NO,
    titleLayout: null,
    contentLayout: null,
    isEditable: YES,

    nameTitleView: SC.LabelView.extend({
        classNames: ['footprint-editable-title-view-medium'],
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        layout: {height: 0.4}
    }),
    contentView: Footprint.EditableFloatFieldItemView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isPercentBinding: SC.Binding.oneWay('.parentView.isPercent'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
        layout: {top: .4, width: 80}
    })
});

Footprint.EditableAgricultureAttributeSetView = SC.View.extend({
    classNames: ['footprint-crop-input-view'],
    childViews: [
        'agricultureTitleView',
        'cropYieldView',
        'unitPriceView',
        'waterConsumptionView',
        'laborInputView',
        'truckTripsView',
        'costTitleView',
        'seedCostView',
        'chemicalCostView',
        'fertilizerCostView',
        'customCostView',
        'contractCostView',
        'irrigationCostView',
        'laborCostView',
        'equipmentCostView',
        'fuelCostView',
        'otherCostView',
        'feedCostView',
        'pastureCostView',
        'totalOperatingCostsView', // Sum of above
        'landRentCostView',
        'otherCashCostsView',
        'totalCashCostsView', // Sum of last three
        'landCostView',
        'establishmentCostView',
        'otherNoncashCostsView',
        'totalNoncashCostsView', // Sum of last three
        'totalCostView', // Sum of totalCashCostsView and totalNoncashCostsView
        'placetypeComponentsUsingPrimaryComponentView'],

    content: null,
    allContent: null,
    // Stores subtotals and the total cost
    totalContent: SC.Object.create({
        total_operating_costs: 0,
        total_cash_costs: 0,
        total_cost: 0
    }),


    agricultureTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Agriculture Attributes',
        layout: {height: 20, width: 180, left:25, top:8}
    }),

    cropYieldView: Footprint.EditableFieldMediumTitleView.extend({
        layout: {top: 30, left: 30, width: 260, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'crop_yield',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Crop yield (units) per acre',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    unitPriceView: Footprint.EditableFieldMediumTitleView.extend({
        layout: {top: 80, left: 30, width: 260, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'unit_price',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Market price of one crop unit',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    waterConsumptionView: Footprint.EditableFieldMediumTitleView.extend({
        layout: {top: 130, left: 30, width: 260, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'water_consumption',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Water consumption per acre',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    laborInputView: Footprint.EditableFieldMediumTitleView.extend({
        layout: {top: 180, left: 30, width: 260, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'labor_input',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Labor input per acre',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}

    }),

    truckTripsView: Footprint.EditableFieldMediumTitleView.extend({
        layout: {top: 230, left: 30, width: 260, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'truck_trips',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Truck trips per acre of crop',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    costTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Production Costs ($ / Acre)',
        layout: {height: 20, width: 180, left:300, top:8}
    }),

    seedCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 30, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'seed_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Seed',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    chemicalCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 50, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'chemical_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Chemical',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    fertilizerCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 70, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'fertilizer_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Fertilizer',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    customCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 90, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'custom_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Custom',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    contractCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 110, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'contract_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Contract',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    irrigationCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 130, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'irrigation_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Irrigation',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    laborCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 150, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'labor_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Labor',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    equipmentCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 170, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'equipment_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Equipment',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    fuelCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 190, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'fuel_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Fuel',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    otherCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 210, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'other_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Other',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    feedCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 230, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'feed_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Feed',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    pastureCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 250, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'pasture_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Pasture',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    totalOperatingCostsView: Footprint.BuiltFormSummaryFieldView.extend({
        layout: {top: 270, left: 300, width: 180, height: 20},
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('*content.status'),
        value: 'Total Operating Costs',
        titleTextAlignment: SC.ALIGN_CENTER,
        totalContent: null,
        totalContentBinding: SC.Binding.oneWay('.parentView.totalContent'),
        totalContentKey: 'total_operating_costs',

        seedCostProperty: null,
        chemicalCostProperty: null,
        fertilizerCostProperty: null,
        customCostProperty: null,
        contractCostProperty: null,
        irrigationCostProperty: null,
        laborCostProperty: null,
        equipmentCostProperty: null,
        fuelCostProperty: null,
        otherCostProperty: null,

        seedCostPropertyBinding: SC.Binding.oneWay('*content.seed_cost'),
        chemicalCostPropertyBinding: SC.Binding.oneWay('*content.chemical_cost'),
        fertilizerCostPropertyBinding: SC.Binding.oneWay('*content.fertilizer_cost'),
        customCostPropertyBinding: SC.Binding.oneWay('*content.custom_cost'),
        contractCostPropertyBinding: SC.Binding.oneWay('*content.contract_cost'),
        irrigationCostPropertyBinding: SC.Binding.oneWay('*content.irrigation_cost'),
        laborCostPropertyBinding: SC.Binding.oneWay('*content.labor_cost'),
        equipmentCostPropertyBinding: SC.Binding.oneWay('*content.equipment_cost'),
        fuelCostPropertyBinding: SC.Binding.oneWay('*content.fuel_cost'),
        otherCostPropertyBinding: SC.Binding.oneWay('*content.other_cost'),
        feedCostPropertyBinding: SC.Binding.oneWay('*content.feed_cost'),
        pastureCostPropertyBinding: SC.Binding.oneWay('*content.pasture_cost'),

        computedValue: function() {
            if (this.get('contentStatus') & SC.Record.READY) {
                return (
                    parseFloat(this.getPath('content.seed_cost')) +
                    parseFloat(this.getPath('content.chemical_cost')) +
                    parseFloat(this.getPath('content.fertilizer_cost')) +
                    parseFloat(this.getPath('content.custom_cost')) +
                    parseFloat(this.getPath('content.contract_cost')) +
                    parseFloat(this.getPath('content.irrigation_cost')) +
                    parseFloat(this.getPath('content.labor_cost')) +
                    parseFloat(this.getPath('content.equipment_cost')) +
                    parseFloat(this.getPath('content.fuel_cost')) +
                    parseFloat(this.getPath('content.other_cost')) +
                    parseFloat(this.getPath('content.feed_cost')) +
                    parseFloat(this.getPath('content.pasture_cost'))
                ).toFixed(2)
            }
        }.property('contentStatus', 'seedCostProperty','chemicalCostProperty','fertilizerCostProperty','customCostProperty','contractCostProperty',
                'irrigationCostProperty','laborCostProperty','equipmentCostProperty','fuelCostProperty','otherCostProperty',
                'feedCostProperty','pastureCostProperty').cacheable(),

        computedValueObserver: function() {
            var totalContent = this.get('totalContent');
            var computedValue = this.get('computedValue');
            totalContent.setIfChanged(this.get('totalContentKey'), computedValue);
        }.observes('computedValue', 'content', 'status')
    }),

    landRentCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 300, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'land_rent_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Land Rent',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    otherCashCostsView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 320, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'other_cash_costs',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Other Cash Costs',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    totalCashCostsView: Footprint.BuiltFormSummaryFieldView.extend({
        layout: {top: 350, left: 300, width: 180, height: 20},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('*content.status'),
        // This isn't an actual attribute of the record. It's a derived value
        value: 'Total Cash Costs',
        titleTextAlignment: SC.ALIGN_CENTER,
        totalContent: null,
        totalContentBinding: SC.Binding.oneWay('.parentView.totalContent'),
        totalContentKey: 'total_cash_costs',

        totalOperatingCostsProperty: null,
        landRendCostProperty: null,
        otherCashCostsProperty: null,

        totalOperatingCostsPropertyBinding: SC.Binding.oneWay('*totalContent.total_operating_costs'),
        landRentCostPropertyBinding: SC.Binding.oneWay('*content.land_rent_cost'),
        otherCashCostsPropertyBinding: SC.Binding.oneWay('*content.other_cash_costs'),

        computedValue: function() {
            if (this.get('contentStatus') & SC.Record.READY) {
                return (
                    parseFloat(this.getPath('totalOperatingCostsProperty')) +
                    parseFloat(this.getPath('otherCashCostsProperty'))
                ).toFixed(2)
            }
        }.property('contentStatus', 'totalOperatingCostsProperty', 'landRentCostProperty', 'otherCashCostsProperty').cacheable(),

        computedValueObserver: function() {
            var totalContent = this.get('totalContent');
            var computedValue = this.get('computedValue');
            totalContent.setIfChanged(this.get('totalContentKey'), computedValue);
        }.observes('computedValue', 'content', 'status')
    }),

    landCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 390, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'land_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Land Mortgage',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    establishmentCostView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 410, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'establishment_cost',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Establishment',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    otherNoncashCostsView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 430, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'other_noncash_costs',
        // Editing of BuiltForms is disabled
        isEditable: NO,
        title: 'Other Non-Cash Costs',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7}
    }),

    totalNoncashCostsView: Footprint.BuiltFormSummaryFieldView.extend({
        layout: {top: 450, left: 300, width: 180, height:19},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('*content.status'),

        landCostProperty: null,
        establishmentCostProperty: null,
        otherNoncashCostsProperty: null,

        landCostPropertyBinding: SC.Binding.oneWay('*content.land_cost'),
        establishmentCostPropertyBinding: SC.Binding.oneWay('*content.establishment_cost'),
        otherNoncashCostsPropertyBinding: SC.Binding.oneWay('*content.other_noncash_costs'),

        value: 'Total Non-Cash Costs',
        titleViewLayout: {left:.01, width:.7},
        contentLayout: {left: .7},

        totalContent: null,
        totalContentBinding: SC.Binding.oneWay('.parentView.totalContent'),
        totalContentKey: 'total_noncash_costs',

        computedValue: function() {
            if (this.get('contentStatus') & SC.Record.READY) {
                return (
                    parseFloat(this.getPath('landCostProperty')) +
                    parseFloat(this.getPath('establishmentCostProperty')) +
                    parseFloat(this.getPath('otherNoncashCostsProperty'))
                ).toFixed(2)
            }
        }.property('contentStatus', 'landCostProperty', 'establishmentCostProperty','otherNoncashCostsProperty').cacheable(),

        computedValueObserver: function() {
            var totalContent = this.get('totalContent');
            var computedValue = this.get('computedValue');
            totalContent.setIfChanged(this.get('totalContentKey'), computedValue);
        }.observes('computedValue', 'content', 'status')
    }),

    totalCostView: Footprint.BuiltFormSummaryFieldView.extend({
        layout: {top: 490, left: 300, width: 180, height: 20},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentStatus: null,
        contentStatusBinding: SC.Binding.oneWay('*content.status'),
        value: 'Total Cost',
        titleTextAlignment: SC.ALIGN_CENTER,
        totalContent: null,
        totalContentBinding: SC.Binding.oneWay('.parentView.totalContent'),
        totalContentKey: 'total_cost',

        totalOperatingCostsProperty: null,
        totalNoncashCostsProperty: null,
        totalCashCostsProperty: null,

        totalNoncashCostsPropertyBinding: SC.Binding.oneWay('*totalContent.total_noncash_costs'),
        totalCashCostsPropertyBinding: SC.Binding.oneWay('*totalContent.total_cash_costs'),

        computedValue: function() {
            if (this.get('contentStatus') & SC.Record.READY) {
                return (
                    parseFloat(this.getPath('totalNoncashCostsProperty')) +
                    parseFloat(this.getPath('totalCashCostsProperty'))
                ).toFixed(2)
            }
        }.property('contentStatus', 'totalNoncashCostsProperty','totalCashCostsProperty').cacheable(),

        computedValueObserver: function() {
            var totalContent = this.get('totalContent');
            var computedValue = this.get('computedValue');
            totalContent.setIfChanged(this.get('totalContentKey'), computedValue);
        }.observes('computedValue', 'content', 'status')
    }),

    placetypeComponentsUsingPrimaryComponentView: Footprint.PlacetypeComponentsUsingPrimaryComponentView.extend({
        title: "CropTypes using Crop",
        layout: {left: 500, top:10, width: 260, height: 180},
        contentBinding: SC.Binding.oneWay('.parentView.allContent')
    })
});
