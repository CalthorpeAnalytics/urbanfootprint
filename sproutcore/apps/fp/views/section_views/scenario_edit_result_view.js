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


sc_require('views/info_views/built_form/editable_bottom_info_view');
sc_require('views/info_views/non_editable_result_bottom_info_view');

Footprint.ScenarioEditResultView = SC.View.extend({

    classNames: ['footprint-scenario-edit-result-view', 'footprint-map-overlay-section'],
    childViews: ['overlayView', 'contentView'],

    activeLayer: null,

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),

    layerName: null,
    layerNameBinding: SC.Binding.oneWay('Footprint.layerActiveController.name'),

    editSectionIsVisible: null,
    activeScenario: null,

    overlayView: Footprint.OverlayView.extend({
        contentBinding: SC.Binding.oneWay('.parentView.activeLayer'),
        statusBinding:SC.Binding.oneWay('*content.status')
    }),

    contentView: SC.ContainerView.extend({
        classNames: 'footprint-edit-section-content-view'.w(),
        layout: {top: 5},

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        activeLayer: null,
        activeLayerBinding: SC.Binding.oneWay('.parentView.activeLayer'),

        verticalAlign: SC.ALIGN_BOTTOM,

        childViews: ['developableAcresView', 'empDensityView',
            'retailView', 'officeView', 'publicView', 'industrialView', 'duDensityView', 'singleFamilyView',
            'attachedSingleFamilyView', 'multiFamilyView'],
        developableAcresView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Acres Developable',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {right: .01, width:.11, bottom: 0.2, top: 0},
            isSeaGreen: YES,
            isWhiteFont: YES,
            isGreyBlue: NO,
            colorIsVisible: NO,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var acres = 0;
                        this.get('allFeatures').forEach(function (feature) {
                            acres = parseFloat(acres) + parseFloat(feature.get('acres_developable'))
                        });
                        return acres.toFixed(2)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer').cacheable()
        }),

        empDensityView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Employees',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .4, width:.1, bottom: 0.2, top: 0},
            isDarkPurple: YES,
            isWhiteFont: YES,
            isGreyBlue: NO,
            colorIsVisible: NO,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var unmodifiedClientSideEmployment = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.employment_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            unmodifiedClientSideEmployment = parseFloat(unmodifiedClientSideEmployment) +
                                (parseFloat(feature.get('acres_developable')) * density * parseFloat(dev_pct) *
                                    parseFloat(gross_net_pct)) + ((1 - dev_pct) * feature.get('emp'))
                        });
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) +
                                ((1 - dev_pct) * feature.get('emp'))
                        });
                        Footprint.endStateDefaultsController.set('unmodifiedClientSideEmployment', unmodifiedClientSideEmployment);
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable(),

            userDefinedPropertyObserver: function() {
                if (this.get('userDefinedProperty') && this.get('densityPercent') != previousDensityPct)
                    Footprint.endStateDefaultsController.set('userDefinedProperty', NO);
                }.observes('grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet'),


            contentView: Footprint.EditableModelStringView.extend({
                classNames: ['footprint-editable-field-content-view', 'footprint-editable-content-view'],
                layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
                isEditable: YES,
                displayValue: null,
                displayValueBinding: '.parentView.value',
                textAlign: SC.ALIGN_CENTER,
                builtFormSelection: null,
                builtFormSelectionBinding: SC.Binding.oneWay('.parentView.builtFormSelection'),
                isEnabled: NO,
//                isEnabled: function(){
//                    if(parseFloat(this.getPath('builtFormSelection.flat_building_densities.employment_density')) == 0) {
//                        return NO
//                    }
//                    return YES
//                }.property('displayValue'),

                value: function (propKey, value) {
                    var userDefinedProperty = Footprint.endStateDefaultsController.get('userDefinedProperty');
                    var densityPct = Footprint.endStateDefaultsController.getPath('content.update.density_pct');
                    var previousDensityPct = Footprint.endStateDefaultsController.get('previousDensityPct')
                    if (value && !isNaN(value)) {
                        var newDensityPercent = value / parseFloat(Footprint.endStateDefaultsController.get('unmodifiedClientSideEmployment'));
                        Footprint.endStateDefaultsController.set('previousDensityPct', densityPct);
                        Footprint.endStateDefaultsController.setPath('content.update.density_pct', newDensityPercent);
                        Footprint.endStateDefaultsController.set('userDefinedProperty', YES);

                    }
                    else if (this.get('displayValue') && !isNaN(this.get('displayValue'))) {
                        Footprint.endStateDefaultsController.set('previousDensityPct', densityPct);
                        return parseFloat(this.get('displayValue'));
                    }
                }.property('displayValue').cacheable()
            })
        }),

        retailView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Retail',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .51, width:.1, bottom: 0.15, top: 0.15},
            isRed: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.retail_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('emp_ret'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        officeView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Office',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .595, width:.1, bottom: 0.15, top: 0.15},
            isRose: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.office_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('emp_off'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        publicView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Public',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .68, width:.1, bottom: 0.15, top: 0.15},
            isBlue: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.public_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('emp_pub'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        industrialView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Industrial',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .765, width:.1, bottom: 0.15, top: 0.15},
            isLightPurple: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.industrial_density')) +
                            parseFloat(this.getPath('builtFormSelection.flat_building_densities.agricultural_density')) +
                            parseFloat(this.getPath('builtFormSelection.flat_building_densities.military_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * (feature.get('emp_ind') + feature.get('emp_ag') + feature.get('emp_military')))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        duDensityView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Dwelling Units',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .01, width:.1, bottom: 0.2, top: 0},
            isUmber: YES,
            isGreyBlue: NO,
            isWhiteFont: YES,
            colorIsVisible: NO,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var unmodifiedClientSideDwellingUnits = 0;
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.dwelling_unit_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }

                        this.get('allFeatures').forEach(function (feature) {
                            unmodifiedClientSideDwellingUnits = parseFloat(unmodifiedClientSideDwellingUnits) +
                                (parseFloat(feature.get('acres_developable')) * density * parseFloat(dev_pct) *
                                    parseFloat(gross_net_pct)) + ((1 - dev_pct) * feature.get('du'))
                        });
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('du'))
                        });
                        Footprint.endStateDefaultsController.set('unmodifiedClientSideDwellingUnits', unmodifiedClientSideDwellingUnits);

                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable(),

            userDefinedPropertyObserver: function() {
                if (this.get('userDefinedProperty'))
                    Footprint.endStateDefaultsController.set('userDefinedProperty', NO);
                }.observes('grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet'),

            contentView: Footprint.EditableModelStringView.extend({
                classNames: ['footprint-editable-field-content-view', 'footprint-editable-content-view'],
                layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
                isEditable: YES,
                displayValue: null,
                displayValueBinding: '.parentView.value',
                textAlign: SC.ALIGN_CENTER,
                builtFormSelection: null,
                builtFormSelectionBinding: SC.Binding.oneWay('.parentView.builtFormSelection'),

                isEnabled: NO,
//                isEnabled: function(){
//                    if(this.getPath('builtFormSelection.flat_building_densities.dwelling_unit_density')== 0) {
//                        return NO
//                    }
//                    return YES
//                }.property('displayValue'),

                value: function (propKey, value) {
                    var userDefinedProperty = Footprint.endStateDefaultsController.get('userDefinedProperty');
                    var densityPct = Footprint.endStateDefaultsController.getPath('content.update.density_pct');
                    if (value && !isNaN(value)) {
                        var newDensityPercent = value / parseFloat(Footprint.endStateDefaultsController.get('unmodifiedClientSideDwellingUnits'));
                        Footprint.endStateDefaultsController.set('previousDensityPct', densityPct);
                        Footprint.endStateDefaultsController.setPath('content.update.density_pct', newDensityPercent);
                        Footprint.endStateDefaultsController.set('userDefinedProperty', YES);
                    }
                    else if (this.get('displayValue') && !isNaN(this.get('displayValue'))) {
                        return parseFloat(this.get('displayValue'));
                    }
                }.property('displayValue').cacheable()
            })
        }),


        singleFamilyView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Single Family',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .12, width:.1, bottom: 0.15, top: 0.15},
            isYellow: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.single_family_large_lot_density')) + parseFloat(this.getPath('builtFormSelection.flat_building_densities.single_family_small_lot_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('du_detsf'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        attachedSingleFamilyView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Attached SF',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .205, width:.1, bottom: 0.15, top: 0.15},
            isDarkOrange: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.attached_single_family_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('du_attsf'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        }),

        multiFamilyView: Footprint.NonEditableResultBottomInfoView.extend({
            title: 'Multifamily',
            titleViewLayout: {top:.5, bottom:.1},
            contentLayout: {right:.1, left:.1, height:.4},
            layout: {left: .29, width:.1, bottom: 0.15, top: 0.15},
            isOrangeBrown: YES,
            value: function () {
                if (this.get('allFeatures')) {
                    if (this.getPath('activeLayer.dbEntityKey') == 'scenario_end_state') {
                        var value = 0;
                        var density = parseFloat(this.getPath('builtFormSelection.flat_building_densities.multifamily_2_to_4_density')) + parseFloat(this.getPath('builtFormSelection.flat_building_densities.multifamily_5_plus_density'));
                        var dev_pct = this.getPath('developmentPercent');
                        var gross_net_pct = this.getPath('grossNetPercent');
                        var density_pct = this.getPath('densityPercent');
                        if (this.get('isClearBase') == YES) {
                            dev_pct = 1
                        }
                        this.get('allFeatures').forEach(function (feature) {
                            value = parseFloat(value) + (parseFloat(feature.get('acres_developable') * density *
                                parseFloat(dev_pct) * parseFloat(density_pct) * parseFloat(gross_net_pct))) + ((1 - dev_pct)
                                * feature.get('du_mf'))
                        });
                        if (value < 1 && value > 0) {
                            return value.toFixed(2)
                        }
                        return value.toFixed(0)
                    }
                }
            }.property('allFeatures', 'allFeaturesStatus', 'activeLayer', 'grossNetPercent', 'developmentPercent',
                'isClearBase', 'builtFormSelection', 'densityPercent', 'builtFormStatus', 'builtFormSet').cacheable()
        })
    })
});
