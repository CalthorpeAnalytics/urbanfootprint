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


Footprint.buildingParcelAreaChartView = SC.View.design(SC.ContentDisplay, {
    classNames : ['buildingParcelChart'],

    displayProperties: ['content', 'selectedItem', 'status', 'buildingFootprint', 'parkingSpace', 'otherHardscape', 'nonIrrigated', 'irrigated', 'lotSqft'],
    content: null,
    selectedItem: null,
    status: null,
    statusBinding: SC.Binding.oneWay('*selectedItem.status'),

    buildingFootprint: null,
    parkingSpace: null,
    otherHardscape: null,
    nonIrrigated: null,
    irrigated: null,
    lotSqft: null,

    buildingFootprintBinding: SC.Binding.oneWay('*content.building_footprint_square_feet'),
    parkingSpaceBinding: SC.Binding.oneWay('*content.surface_parking_square_feet'),
    otherHardscapeBinding: SC.Binding.oneWay('*content.hardscape_other_square_feet'),
    nonIrrigatedBinding: SC.Binding.oneWay('*content.nonirrigated_softscape_square_feet'),
    irrigatedBinding: SC.Binding.oneWay('*content.irrigated_softscape_square_feet'),
    lotSqftBinding: SC.Binding.oneWay('*content.lot_size_square_feet'),

    update: function(context) {
        if (this.getPath('selectedItem.status') & SC.Record.READY) {

            this._buildingParcelUseCategories = [];

            var building_footprint = parseFloat(this.getPath('content.building_footprint_square_feet')) || 0;
            var surface_parking = parseFloat(this.getPath('content.surface_parking_square_feet')) || 0;
            var other_hardscape = parseFloat(this.getPath('content.hardscape_other_square_feet')) || 0;
            var non_irrigated = parseFloat(this.getPath('content.nonirrigated_softscape_square_feet')) || 0;
            var irrigated = parseFloat(this.getPath('content.irrigated_softscape_square_feet'))  || 0;
            var lot_sqft = parseFloat(this.getPath('content.lot_size_square_feet')) || 0.0001;

            var building_footprint_pct = building_footprint / lot_sqft;
            var surface_parking_pct = surface_parking / lot_sqft;
            var other_hardscape_pct = other_hardscape / lot_sqft;
            var non_irrigated_pct = non_irrigated / lot_sqft;
            var irrigated_pct = irrigated / lot_sqft;

            var dataManager = d3.building.dataManager();
            //dataManager contains the helper function "createDataObject"
            //dataObjects represent the pieces of the pie chart, and contain "category" and "percentage" attributes

            // for each of the landUse categories within the flat built form,
            // gets percentage data from API
            // creates data object with "category" and "percentage" attributes,
            // adds to array of landUseCategories

            this._buildingParcelUseCategories.push(
                dataManager.createDataObject("Building Footprint", building_footprint_pct),
                dataManager.createDataObject("Surface Parking", surface_parking_pct),
                dataManager.createDataObject("Other Hardscape", other_hardscape_pct),
                dataManager.createDataObject("Non-Irrigated Softscape", non_irrigated_pct),
                dataManager.createDataObject("Irrigated Softscape", irrigated_pct)
            );

            // d3.building.donutChart is a function that takes a div bound with data as an argument
            // we select the div that will hold the chart (using the context); bind the data (this._landUseCategories),
            // and then call the donutChartMaker function
            d3.selectAll(context).datum(this._buildingParcelUseCategories)
                .call(d3.building.buildingDonutChart());
        }
    }
});



Footprint.builtFormCompositionAreaChartView = SC.View.design(SC.ContentDisplay, {
    classNames : ['buildingParcelChart'],

    displayProperties: ['selectedItem', 'status', 'buildingUses', 'buildingUsesStatus'],
    content: null,
    selectedItem: null,

    status: null,
    statusBinding: SC.Binding.oneWay('*selectedItem.building_attribute_set.status'),

    buildingUses: null,
    buildingUsesBinding: SC.Binding.oneWay('*selectedItem.building_attribute_set.building_use_percents'),

    buildingUsesStatus: null,
    buildingUsesStatusBinding: SC.Binding.oneWay('*buildingUses.status'),


    update: function(context) {
        if (this.get('status') & SC.Record.READY) {
            this._buildingUseCategories = [];

            var building_use_percents = this.getPath('selectedItem.building_attribute_set.building_use_percents');
            var single_family_pct = 0;
            var attached_single_family_pct = 0;
            var multifamily_pct = 0;
            var retail_pct = 0;
            var office_pct = 0;
            var public_pct = 0;
            var industrial_pct = 0;
            var agricultural_pct = 0;
            var military_pct = 0;

            building_use_percents.forEach(function(use){
                if (use.getPath('building_use_definition.name') == 'Detached Single Family') {
                    single_family_pct = single_family_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.name') == 'Attached Single Family') {
                    attached_single_family_pct = attached_single_family_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.name') == 'Multifamily 2 To 4' ||
                    use.getPath('building_use_definition.name') == 'Multifamily 5 Plus') {
                    multifamily_pct = multifamily_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Retail') {
                    retail_pct = retail_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Office') {
                    office_pct = office_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Public') {
                    public_pct = public_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Industrial') {
                    industrial_pct = industrial_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Agriculture') {
                    agricultural_pct = agricultural_pct + use.get('percent')
                }

                if (use.getPath('building_use_definition.type') == 'Military') {
                    military_pct = military_pct + use.get('percent')
                }

            });

            var dataManager = d3.buildingUses.dataManager();
            //dataManager contains the helper function "createDataObject"
            //dataObjects represent the pieces of the pie chart, and contain "category" and "percentage" attributes

            // for each of the landUse categories within the flat built form,
            // gets percentage data from API
            // creates data object with "category" and "percentage" attributes,
            // adds to array of landUseCategories

            this._buildingUseCategories.push(
                dataManager.createDataObject("Single Family", single_family_pct),
                dataManager.createDataObject("Townhome", attached_single_family_pct),
                dataManager.createDataObject("Multifamily", multifamily_pct),
                dataManager.createDataObject("Retail", retail_pct),
                dataManager.createDataObject("Office", office_pct),
                dataManager.createDataObject("Public", public_pct),
                dataManager.createDataObject("Industrial", industrial_pct),
                dataManager.createDataObject("Agriculture", agricultural_pct),
                dataManager.createDataObject("Military", military_pct)
            );

            // d3.building.donutChart is a function that takes a div bound with data as an argument
            // we select the div that will hold the chart (using the context); bind the data (this._landUseCategories),
            // and then call the donutChartMaker function
            d3.selectAll(context).datum(this._buildingUseCategories)
                .call(d3.buildingUses.buildingUseDonutChart());
        }
    }
});
