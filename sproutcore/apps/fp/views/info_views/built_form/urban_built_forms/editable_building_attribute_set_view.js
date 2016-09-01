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
sc_require('views/info_views/built_form/urban_built_forms/editable_building_use_type_view');
sc_require('views/info_views/built_form/urban_built_forms/editable_building_use_percent_view');
sc_require('views/info_views/built_form/editable_use_percent_field_view');


Footprint.EditableBuildingAttributeSetView = SC.View.extend({

    classNames: ['footprint-building-input-view'],
    childViews:['nameTitleView', 'websiteView', 'editableBuildingUsePercentView', 'buildingTitleView', 'parcelCompTitleView', 'parkingTitleView',
        'residentialCharacteristicsTitleView', 'lotSizeView', 'buildingStoriesView', 'totalFarView',
        'surfaceParkingSpacesView', 'aboveStructuredParkingView', 'belowStructuredParkingView', 'residentialVacancyView',
        'householdSizeView', 'averageParkingSqftView', 'parcelCompositionView', 'irrigatedPercentView'],

    content: null,
    selectedItem: null,

    nameTitleView: SC.LabelView.extend({
       classNames: ['footprint-bold-title-view'],
       value: 'Building Website',
       fontWeight: 700,
       layout: {left: 25, width: 120, height:20, top: 10}
    }),

    websiteView: Footprint.EditableModelTextView.extend({
        classNames: ['footprint-editable-content-11px-view'],
        valueBinding: SC.Binding.oneWay('.parentView*content.website'),
        layout: {left: 30, width: 280, height:20, top: 30},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    editableBuildingUsePercentView: Footprint.EditableBuildingUsePercentView.extend({
        layout: {left: 380, height: 250, right: 30, top: 15},
        // Bind the list of BuildingUsePercent instances
        contentBinding: SC.Binding.oneWay('.parentView*selectedItem.building_attribute_set.building_use_percents'),
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    buildingTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Parcel/Building',
        layout: {height: 20, width: 100, left:25, top:60}
    }),

    parkingTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Parking',
        layout: {height: 20, width: 70, left:135, top: 60}
    }),

    residentialCharacteristicsTitleView: SC.LabelView.extend({
        classNames: ['footprint-bold-title-view'],
        value: 'Residential',
        layout: {height: 20, width: 100, left:260, top: 110}
    }),

    lotSizeView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 80, left: 30, width: 100, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'lot_size_square_feet',
        title: 'Lot Size (Square Feet)',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),
    buildingStoriesView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 125, left: 30, width: 100, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'floors',
        title: 'Building Stories',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    totalFarView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 165, left: 30, width: 100, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'total_far',
        title: 'Total FAR',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    surfaceParkingSpacesView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 80, left: 140, width: 100, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'surface_parking_spaces',
        title: 'Surface Parking Spaces',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    aboveStructuredParkingView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 125, left: 140, width: 110, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'above_ground_structured_parking_spaces',
        title: 'Structured - Above Ground',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    belowStructuredParkingView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 165, left: 140 , width: 110, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'below_ground_structured_parking_spaces',
        title: 'Structured - Below Ground',
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    residentialVacancyView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 125, left: 265 , width: 110, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'vacancy_rate',
        title: 'Residential Vacancy Rate',
        isPercent: YES,
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    householdSizeView: Footprint.SimpleEditableFieldInfoView.extend({
        layout: {top: 165, left: 265 , width: 110, height:35},
        contentBinding: SC.Binding.from('.parentView.content'),
        contentValueKey: 'household_size',
        title: 'Household Size (avg)',
        isPercent: YES,
        titleViewLayout: {height:.4},
        contentLayout: {top:.4, width: 80},
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),

    averageParkingSqftView: Footprint.SliderInfoView.extend({
        layout: { left: 65, width: 120, height:50, top: 210},
        inputLayout: { right:.3, left:.3, top:0, height: 0.3},
        symbolLayout: { top: 1, left: 0.75, height:0.25 },
        sliderLayout: { left:.1, right:.1, top:.2, height: 0.6 },
        labelLayout: { bottom: 0.05, left: 0.1, right:.1, height:.25 },
        // Editing of BuiltForms is disabled
        isEditable: NO,
        classNames: ['featurer-bar-param2'],
        title: 'SqFt/Parking Space',
        minimum: 0,
        maximum: 660,
        valueSymbol: null,
        step: 1,
        displayValueBinding: SC.Binding.from('.parentView*content.average_parking_space_square_feet'),
        value: function (propKey, value) {
            if (value !== undefined) {
                this.set('displayValue', value);
                return value;
            }
            return this.get('displayValue');
        }.property('displayValue').cacheable()
    }),

    irrigatedPercentView: Footprint.SliderInfoView.extend({
        layout: { left: 190, width: 120, height:50, top: 210},
        inputLayout: { right:.3, left:.3, top:0, height: 0.3},
        symbolLayout: { top: 1, left: 0.75, height:0.25 },
        sliderLayout: { left:.1, right:.1, top:.2, height: 0.6 },
        labelLayout: { bottom: 0.05, left: 0.1, right:.1, height:.25 },
        // Editing of BuiltForms is disabled
        isEditable: NO,
        classNames: ['featurer-bar-param2'],
        valueSymbol: '%',
        title: '% Irrigated',
        minimum: 0,
        maximum: 100,
        step: 1,
        displayValueBinding: SC.Binding.from('.parentView*content.irrigated_percent'),
        value: function (propKey, value) {
            if (value !== undefined) {
                this.set('displayValue', value / 100);
                return value;
            }
            return this.get('displayValue') * 100;
        }.property('displayValue').cacheable()
    }),

    parcelCompositionView: SC.View.extend({
        layout: {top: 260, bottom: 0},
        childViews: ['parcelCharacteristicsTitleView', 'buildingFootprintView', 'parkingSqFtView',
            'otherHardscapeSqFtView', 'irrigatedSqFtView', 'nonIrrigatedSqFtView'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        parcelCharacteristicsTitleView: SC.LabelView.extend({
            classNames: ['footprint-bold-title-view'],
            value: 'Parcel Hardscape/Softscape Square Feet',
            layout: {height: 20, width: 250, left:25}
        }),

        buildingFootprintView: Footprint.EditableBottomInfoView.extend({
            classNames: ['footprint-building-footprint-view'],
            layout: {top: 25, left: 30, width: 100, height: 40},
            // Editing disabled for BuiltForms
            isEditable: NO,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'building_footprint_square_feet',
            title: 'Building Footprint SqFt'
        }),

        parkingSqFtView: Footprint.NonEditableBottomLabelledView.extend({
            classNames: ['footprint-parking-sqft-view'],
            layout: {top: 25, left: 150, width: 100, height: 40},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            statusBinding: SC.Binding.oneWay('.parentView*content.status'),

            computeValueObserver: function () {
                if (this.get('status') != SC.Record.READY_DIRTY) {
                    return
                }
                var average_parking_sqft = parseFloat(this.getPath('content.average_parking_space_square_feet'));
                var surface_parking_spaces = parseFloat(this.getPath('content.surface_parking_spaces'));

                var surface_parking_sqft = parseFloat((average_parking_sqft * surface_parking_spaces).toFixed(1));

                if (surface_parking_sqft < 0 || surface_parking_sqft > 0 || surface_parking_sqft == 0) {
                    this.get('content').setIfChanged(this.get('contentValueKey'), surface_parking_sqft);
                }
            }.observes('*content.average_parking_space_square_feet', '*content.surface_parking_spaces', 'status'),

            contentValueKey: 'surface_parking_square_feet',
            title: 'Surface Parking SqFt'
        }),

        otherHardscapeSqFtView: Footprint.EditableBottomInfoView.extend({
            classNames: ['footprint-other-hardscape-view'],
            layout: {top: 25, left: 270, width: 100, height: 40},
            // Editing disabled for BuiltForms
            isEditable: NO,
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'hardscape_other_square_feet',
            title: 'Other Hardscape SqFt'
        }),

        irrigatedSqFtView: Footprint.NonEditableBottomLabelledView.extend({
            classNames: ['footprint-irrigated-softscape-view'],
            layout: {top: 25, left: 510, width: 100, height: 40},
            statusBinding: SC.Binding.oneWay('.parentView*content.status'),

            computeValueObserver: function () {
                if (this.get('status') != SC.Record.READY_DIRTY) {
                    return
                }

                var building_footprint_square_feet = parseFloat(this.getPath('content.building_footprint_square_feet'));
                var surface_parking_square_feet = parseFloat(this.getPath('content.surface_parking_square_feet'));
                var hardscape_other_square_feet = parseFloat(this.getPath('content.hardscape_other_square_feet'));
                var lot_size_square_feet = parseFloat(this.getPath('content.lot_size_square_feet'));
                var irrigated_percent = parseFloat(this.getPath('content.irrigated_percent'));

                var irrigated_softscape_square_feet = parseFloat(((lot_size_square_feet - (building_footprint_square_feet + surface_parking_square_feet + hardscape_other_square_feet)) * irrigated_percent).toFixed(1));

                if (irrigated_softscape_square_feet < 0 || irrigated_softscape_square_feet > 0 || irrigated_softscape_square_feet == 0) {
                    this.get('content').setIfChanged(this.get('contentValueKey'), irrigated_softscape_square_feet);
                }
            }.observes('*content.building_footprint_square_feet', '*content.surface_parking_square_feet', '*content.hardscape_other_square_feet', '*content.lot_size_square_feet', '*content.irrigated_percent', 'status'),

            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'irrigated_softscape_square_feet',
            title: 'Irrigated SqFt'
        }),

        nonIrrigatedSqFtView: Footprint.NonEditableBottomLabelledView.extend({
            classNames: ['footprint-non-irrigated-softscape-view'],
            layout: {top: 25, left: 390, width: 100, height: 40},
            statusBinding: SC.Binding.oneWay('.parentView*content.status'),

            computeValueObserver: function () {
                if (this.get('status') != SC.Record.READY_DIRTY) {
                    return
                }
                var building_footprint_square_feet = parseFloat(this.getPath('content.building_footprint_square_feet'));
                var surface_parking_square_feet = parseFloat(this.getPath('content.surface_parking_square_feet'));
                var hardscape_other_square_feet = parseFloat(this.getPath('content.hardscape_other_square_feet'));
                var lot_size_square_feet = parseFloat(this.getPath('content.lot_size_square_feet'));
                var irrigated_percent = parseFloat(this.getPath('content.irrigated_percent'));

                var nonirrigated_softscape_square_feet = parseFloat(((lot_size_square_feet - (building_footprint_square_feet + surface_parking_square_feet + hardscape_other_square_feet)) * (1 - irrigated_percent)).toFixed(1));

                if (nonirrigated_softscape_square_feet < 0 || nonirrigated_softscape_square_feet > 0 || nonirrigated_softscape_square_feet == 0) {
                    this.get('content').setIfChanged(this.get('contentValueKey'), nonirrigated_softscape_square_feet);
                }
            }.observes('*content.building_footprint_square_feet', '*content.surface_parking_square_feet', '*content.hardscape_other_square_feet', '*content.lot_size_square_feet', '*content.irrigated_percent', 'status'),

            contentBinding: SC.Binding.oneWay('.parentView.content'),
            contentValueKey: 'nonirrigated_softscape_square_feet',
            title: 'Non-Irrigated Softscape SqFt'
        })
    })
});
