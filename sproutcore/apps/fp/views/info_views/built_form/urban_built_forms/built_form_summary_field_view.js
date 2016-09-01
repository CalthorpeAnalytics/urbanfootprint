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


Footprint.BuiltFormSummaryFieldView = SC.View.extend({
    classNames: ['footprint-summary-field-view'],
    childViews:'nameTitleView contentView'.w(),
    content: null,
    status: null,
    layout: null,
    allContent: null,
    flatBuiltFormStatus: null,
    titleTextAlignment: null,
    computedValue: null,
    componentType: null,
    componentSummaryObserver: null,
    editController: null,

    nameTitleView: SC.LabelView.extend({
        textAlignBinding: SC.Binding.oneWay('.parentView.titleTextAlignment'),
        valueBinding: SC.Binding.oneWay('.parentView.value'),
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
        valueBinding: SC.Binding.oneWay('.parentView.computedValue'),
        layout: {left:.65}
    })
});


updateFlatBuildings = function(content) {

    var lot_sqft = parseFloat(content.getPath('building_attribute_set.lot_size_square_feet'));
    var total_far = parseFloat(content.getPath('building_attribute_set.total_far'));
    var building_uses = content.getPath('building_attribute_set.building_use_percents');
    var flat_density = content.get('flat_building_densities');

    var hh_size = parseFloat(content.getPath('building_attribute_set.household_size'));
    var vacancy_rate = parseFloat(1 - content.getPath('building_attribute_set.vacancy_rate'));

    if (flat_density.get('status') & SC.Record.READY) {
        ['single_family_large_lot_density', 'single_family_small_lot_density', 'attached_single_family_density',
            'multifamily_2_to_4_density', 'multifamily_5_plus_density', 'retail_services_density', 'restaurant_density',
            'arts_entertainment_density', 'accommodation_density', 'other_services_density', 'office_services_density',
            'public_admin_density', 'education_services_density', 'medical_services_density', 'manufacturing_density',
            'transport_warehouse_density', 'wholesale_density', 'construction_utilities_density', 'agriculture_density',
            'extraction_density', 'military_density'
        ].forEach(function (use) {
                flat_density.setIfChanged(use, 0)
            });

        if (building_uses.length() > 0) {
            building_uses.forEach(function (use) {
                var building_use_percent = use.get('percent');
                var efficiency = use.get('efficiency');
                var sqft_unit = use.get('square_feet_per_unit');

                if (use.getPath('building_use_definition.name') == 'Detached Single Family') {

                    var density = parseFloat((43560.0 / (building_use_percent * lot_sqft)));

                    if (density < 7.9) {
                        flat_density.setIfChanged('single_family_large_lot_density', density);
                    }
                    else {
                        flat_density.setIfChanged('single_family_small_lot_density', density)
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Attached Single Family') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('attached_single_family_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Multifamily 2 To 4') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('multifamily_2_to_4_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Multifamily 5 Plus') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('multifamily_5_plus_density', density);
                    }
                }

                var du_density =
                    flat_density.get('single_family_large_lot_density') +
                    flat_density.get('single_family_small_lot_density') +
                    flat_density.get('attached_single_family_density') +
                    flat_density.get('multifamily_2_to_4_density') +
                    flat_density.get('multifamily_5_plus_density');

                flat_density.setIfChanged('dwelling_unit_density', du_density);

                var hh_density =
                    vacancy_rate * parseFloat(flat_density.get('dwelling_unit_density'));
                flat_density.setIfChanged('household_density', hh_density);

                var pop_density =
                    hh_size * parseFloat(flat_density.get('household_density'));
                flat_density.setIfChanged('population_density', pop_density);

                if (use.getPath('building_use_definition.name') == 'Retail Services') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('retail_services_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Restaurant') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('restaurant_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Arts Entertainment') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('arts_entertainment_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Accommodation') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('accommodation_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Other Services') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('other_services_density', density);
                    }
                }

                var ret_density =
                    flat_density.get('retail_services_density') +
                    flat_density.get('restaurant_density') +
                    flat_density.get('arts_entertainment_density') +
                    flat_density.get('accommodation_density') +
                    flat_density.get('other_services_density');

                flat_density.setIfChanged('retail_density', ret_density);

                if (use.getPath('building_use_definition.name') == 'Office Services') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('office_services_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Medical Services') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('medical_services_density', density);
                    }
                }

                var off_density =
                    flat_density.get('office_services_density') +
                    flat_density.get('medical_services_density');

                flat_density.setIfChanged('office_density', off_density);


                if (use.getPath('building_use_definition.name') == 'Public Admin') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('public_admin_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Education Services') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('education_services_density', density);
                    }
                }

                var pub_density =
                    flat_density.get('public_admin_density') +
                    flat_density.get('education_services_density');

                flat_density.setIfChanged('public_density', pub_density);


                if (use.getPath('building_use_definition.name') == 'Manufacturing') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('manufacturing_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Wholesale') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('wholesale_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Transport Warehouse') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('transport_warehouse_density', density);
                    }
                }

                if (use.getPath('building_use_definition.name') == 'Construction Utilities') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('construction_utilities_density', density);
                    }
                }

                var ind_density =
                    flat_density.get('manufacturing_density') +
                    flat_density.get('wholesale_density') +
                    flat_density.get('transport_warehouse_density') +
                    flat_density.get('construction_utilities_density');

                flat_density.setIfChanged('industrial_density', ind_density);

                if (use.getPath('building_use_definition.name') == 'Agriculture') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('agriculture_density', density);
                    }
                }
                if (use.getPath('building_use_definition.name') == 'Extraction') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('extraction_density', density);
                    }
                }

                var ag_density =
                    flat_density.get('agriculture_density') +
                    flat_density.get('extraction_density');

                flat_density.setIfChanged('agriculatural_density', ag_density);

                if (use.getPath('building_use_definition.name') == 'Military') {
                    var density = parseFloat(((building_use_percent * total_far * efficiency * lot_sqft) / sqft_unit) * (43560.0 / lot_sqft));
                    if (density < 0 || density > 0 || density == 0) {
                        flat_density.setIfChanged('military_density', density);
                    }
                }
            })
        }
    }
};

updateFlatBuiltForm = function(content, field, compontent_type) {

    var weighted_density = 0.0;
    var component_percents = content.get('component_percents');
    var flatBuiltForm = content.get('flat_building_densities');
    if (!(flatBuiltForm && (flatBuiltForm.get('status') & SC.Record.READY)))
        return;

    if (component_percents) {
        component_percents.forEach(function(component_percent) {
            var percent = component_percent.get('percent') ?
                component_percent.get('percent') :
                0;

            var component = component_percent.get('subclassedComponent');
            if (!component) {
                logWarning("component_percent has no component. This is due to a transition between Built Form controllers, but needs fixing");
            }
            else {
                var flat_building_densities = component.get('flat_building_densities');
                var density = flat_building_densities && flat_building_densities.get(field) ?
                    flat_building_densities.get(field) :
                    0;
                var percent_density = percent * density;
                weighted_density = weighted_density + percent_density;
            }
        });

        if (weighted_density < 0 || weighted_density > 0 || weighted_density == 0) {
            flatBuiltForm.setIfChanged(field, weighted_density);
        }
    }
};
