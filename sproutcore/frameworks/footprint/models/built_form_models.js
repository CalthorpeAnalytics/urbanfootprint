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

sc_require('models/key_mixin');
sc_require('models/name_mixin');
sc_require('models/tags_mixin');
sc_require('models/medium_models');


Footprint.ComponentPercentMixin = {
    component_class: SC.Record.attr(String),
    container_class: SC.Record.attr(String),

    // Walk like a duck
    hasComponentPercents: YES,

    subclassedComponent: function(propKey, value) {
        if (value) {
            this.set('component', value);
        }
        var componentClass = SC.objectForPropertyPath('Footprint.%@'.fmt(this.get('component_class')));
        // For some reason we occasionally request with the abstract version of a ComponentPercent
        // instance. This will save
        if (!componentClass)
            return null;
        if (this.get('store') != undefined) {
            return this.get('store').find(
                componentClass,
                this.readAttribute(this.get('componentField')));
        }
    }.property(),

    subclassedContainer: function(propKey, value) {
        if (value) {
            this.set('component', value);
        }
        var containerClass = SC.objectForPropertyPath('Footprint.%@'.fmt(this.get('container_class')));
        // For some reason we occasionally request with the abstract version of a ComponentPercent
        // instance. This will save
        if (!containerClass)
            return null;
        if (this.get('store') != undefined) {
            return this.get('store').find(
                containerClass,
                this.readAttribute(this.get('containerField')));
        }
    }.property()
};


Footprint.BuildingAttributesMixin = {
    building_attribute_set: SC.Record.toOne("Footprint.BuildingAttributeSet", {isMaster: YES}),
    isUrban: YES
};

Footprint.AgricultureAttributesMixin = {
    agriculture_attribute_set: SC.Record.toOne("Footprint.AgricultureAttributeSet", {isMaster: YES}),
    isAgriculture: YES
};

Footprint.BuiltFormAggregateMixin = {
    mediumStatusObserver: function() {
        if (this.get('status') === SC.Record.READY_CLEAN &&
            this.getPath('medium.status') === SC.Record.READY_DIRTY) {
            this.get('store').writeStatus(this.get('storeKey'), SC.Record.READY_DIRTY);
        }
    }.observes('*medium.status')
};

Footprint.AgricultureAttributeSet = Footprint.Record.extend({
    crop_yield: SC.Record.attr(Number),
    unit_price: SC.Record.attr(Number),
    cost: SC.Record.attr(Number),
    water_consumption: SC.Record.attr(Number),
    labor_input: SC.Record.attr(Number),
    truck_trips: SC.Record.attr(Number),

    // cost breakouts
    seed_cost: SC.Record.attr(Number),
    chemical_cost: SC.Record.attr(Number),
    fertilizer_cost: SC.Record.attr(Number),
    custom_cost: SC.Record.attr(Number),
    contract_cost: SC.Record.attr(Number),
    irrigation_cost: SC.Record.attr(Number),
    labor_cost: SC.Record.attr(Number),
    equipment_cost: SC.Record.attr(Number),
    fuel_cost: SC.Record.attr(Number),
    other_cost: SC.Record.attr(Number),
    feed_cost: SC.Record.attr(Number),
    pasture_cost: SC.Record.attr(Number),

    land_rent_cost: SC.Record.attr(Number),
    other_cash_costs: SC.Record.attr(Number),

    land_cost: SC.Record.attr(Number),
    establishment_cost: SC.Record.attr(Number),
    other_noncash_costs: SC.Record.attr(Number),

    _cloneProperties:function() {
        return [];
    },

    // This instructs the clone operation not to wait for these properties to load
    _nestedProperties: function() {
        return []
    },

    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return [];
    }
});

Footprint.BuildingAttributeSet = Footprint.Record.extend({
    building_use_percents: SC.Record.toMany('Footprint.BuildingUsePercent', {nested: YES}),
    lot_size_square_feet: SC.Record.attr(Number),
    floors: SC.Record.attr(Number),
    total_far: SC.Record.attr(Number),
    average_parking_space_square_feet: SC.Record.attr(Number),
    surface_parking_spaces: SC.Record.attr(Number),
    above_ground_structured_parking_spaces: SC.Record.attr(Number),
    below_ground_structured_parking_spaces: SC.Record.attr(Number),
    surface_parking_square_feet: SC.Record.attr(Number),
    building_footprint_square_feet: SC.Record.attr(Number),
    hardscape_other_square_feet: SC.Record.attr(Number),
    irrigated_softscape_square_feet: SC.Record.attr(Number),
    nonirrigated_softscape_square_feet: SC.Record.attr(Number),
    irrigated_percent: SC.Record.attr(Number),
    vacancy_rate: SC.Record.attr(Number),
    household_size: SC.Record.attr(Number),
    residential_irrigated_square_feet: SC.Record.attr(Number),
    commercial_irrigated_square_feet: SC.Record.attr(Number),
    gross_net_ratio: SC.Record.attr(Number),
    intersection_density: SC.Record.attr(Number),

    /***
     * Returns the BuildingUsePercent matching the BuildingUseDefinition, if it exists
     * @param buildingUseDefinition
     * @returns A BuildingUsePercent instance, or undefined
     */
    buildingUsePercentOfBuildingUseDefinition: function(buildingUseDefinition) {
        return (this.get('building_use_percents') || []).find(function(buildingUsePercent) {
            return buildingUsePercent.getPath('building_use_definition')==buildingUseDefinition;
        });
    },

    _cloneProperties:function() {
        return ['building_use_percents'];
    },

    // This instructs the clone operation not to wait for these properties to load
    _nestedProperties: function() {
        return ['building_use_percents']
    },

    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return [];
    }
});

Footprint.BuildingUseDefinition = Footprint.Record.extend({
    name: SC.Record.attr(String),
    type: SC.Record.attr(String)
});

Footprint.BuildingUsePercent = Footprint.Record.extend({
    building_attribute_set: SC.Record.toOne("Footprint.BuildingAttributeSet", {isMaster:NO}),
    building_use_definition: SC.Record.toOne("Footprint.BuildingUseDefinition", {isMaster:NO}),
    percent: SC.Record.attr(Number),
    efficiency: SC.Record.attr(Number),
    square_feet_per_unit: SC.Record.attr(Number),
    floor_area_ratio: SC.Record.attr(Number),
    unit_density: SC.Record.attr(Number),
    gross_built_up_area: SC.Record.attr(Number),
    net_built_up_area: SC.Record.attr(Number),
    building_use_definition_name: function() {
        return this.getPath('building_use_definition.name');
    }.property('building_use_definition').cacheable(),

    /***
     * Reports whether or not the BuildingUsePercent is a top-level instance
     */
    isTopLevel: function() {
        return this.get('building_use_definition') && !this.getPath('building_use_definition.category')
    }.property('building_use_definition').cacheable(),

    /***
     * All BuildingUsePercents of the Building, via BuildingAttributeSet
     */
    buildingUsePercents: function() {
        return this.getPath('building_attribute_set.building_use_percents');
    }.property().cacheable(),

    /***
     * Convenience property to resolve the parent BuildingUsePercent for non-top-level instances
     * @returns {*}
     */
    parentBuildingUsePercent: function() {
        if (this.get('isTopLevel'))
            return null;
        // Find the BuildingUsePercent of the parent BuildingUseDefinition, if it exists
        return this.get('building_attribute_set').buildingUsePercentOfBuildingUseDefinition(this.getPath('building_use_definition.category'));
    }.property('isTopLevel', 'building_use_definition').cacheable(),


    _copyProperties: function() {
        return ['building_use_definition'];
    },
    _skipProperties: function() {
        return ['building_attribute_set'];
    },
    _cloneSetup: function(sourceRecord, parentRecord) {
        this.set('building_attribute_set', parentRecord ?
            parentRecord : // set to cloned BuildingAttributeSet--cloning a parent instance (i.e. the BuiltForm)
            sourceRecord.get('building_attribute_set')); // cloning just this instance--set to the source's property
    }
});


Footprint.BuiltForm = Footprint.Record.extend(
    Footprint.Name,
    Footprint.Key,
    Footprint.Tags, {

    medium: SC.Record.toOne("Footprint.LayerStyle", {}),
    media: SC.Record.toMany("Footprint.Medium", {}),
    // flat_building_densities is readonly
    flat_building_densities: SC.Record.toOne("Footprint.FlatBuiltForm", {isMaster: NO}),

    // The examples used by the visualizer
    examples: SC.Record.toMany("Footprint.BuiltFormExample"),
    origin_instance: SC.Record.toOne('Footprint.BuiltForm', { isMaster: YES}),
    built_form_sets: SC.Record.toMany("Footprint.BuiltFormSet", { isMaster: NO }), // no inverse set on purpose, leave independent
    // Unique class key prefix. Override
    keyPrefix:null,

    // Used to turn off BuiltForm post-save presentation when the ComponentPercents need to kick it off instead
    no_post_save_publishing: SC.Record.attr(Boolean),

    // Save all of these records before the main record. The BuiltForm references them, not the other way around
    _saveBeforeProperties: function() {
        return ['medium', 'examples', 'media']
    },

    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return ['medium', 'examples', 'media'];
    },

    // These are copied by reference to the cloned BuiltForm
    _copyProperties: function () {
        return ['tags', 'built_form_sets']
    },

    _skipProperties: function() {
        return ['origin_instance'];
    },

    // Set the origin Built Form
    _cloneSetup: function(sourceRecord) {
        this.set('origin_instance', sourceRecord);
    },

    _mapAttributes: {
        key: function (record, key, random) {
            return record.get('origin_instance') ?
                '%@_%@'.fmt(key, random) :
                '%@'.fmt(random);
        },
        name: function (record, name, random) {
            return record.get('origin_instance') ?
                '%@ %@'.fmt(name, random) :
                '%@'.fmt(random);
        }
    },

    /***
     * The StyleAttributes of the BuiltForm's medium_context, which is a Footprint.LayerStyle
     * There is normally just one representing the id attribute
     */
    styleAttributes: null,
    styleAttributesBinding: SC.Binding.oneWay('*medium.style_attributes').defaultValue(null),

    /***
     * The styleAttribute of the id. This is the only thing we style for BuiltForms
     */
    idStyleAttribute: function() {
        if (!this.get('styleAttributes'))
            return null;
        return this.get('styleAttributes').filterProperty('attribute', 'id')[0]
    }.property('styleAttributes').cacheable(),

    /***
     * The style is always that of the only style_value_context.
     * A BuiltForm's LayerStyle only has one StyleValueContext for the id attribute * which matches its own id
     */
    idStyle: function() {
        return this.getPath('idStyleAttribute.style_value_contexts.firstObject.style');
    }.property('idStyleAttribute').cacheable(),
});

SC.mixin(Footprint.BuiltForm, {
    friendlyName: function() {
        return 'Built Forms';
    }
});

Footprint.BuiltFormSet = Footprint.Record.extend(

    Footprint.Key,
    Footprint.Name, {

        built_forms: SC.Record.toMany("Footprint.BuiltForm", {
            isMaster: YES
        }),

        _copyProperties: function () {
            return 'built_forms'.w();
        },
        _mapAttributes: {
            key: function (record, key, random) {
                return record.get('origin_instance') ?
                    key + 'New' :
                    'New %@'.fmt(random);
            },
            name: function (record, name) {
                return record.get('origin_instance') ?
                    name + 'New' :
                    'New %@'.fmt(random);
            }
        },

        treeItemIsExpanded: YES,
        treeItemChildren: function () {
            return this.get("built_forms");
        }.property()
    });

Footprint.FlatBuiltForm = Footprint.Record.extend({
    // FlatBuildForm uses the built_form_id as its pk. It lacks its own.
    primaryKey: 'built_form_id',
    key: SC.Record.attr(Number),
    intersection_density: SC.Record.attr(Number),
    built_form_type: SC.Record.attr(String),
    gross_net_ratio: SC.Record.attr(Number),
    dwelling_unit_density: SC.Record.attr(Number),
    household_density: SC.Record.attr(Number),
    population_density: SC.Record.attr(Number),
    employment_density: SC.Record.attr(Number),
    single_family_large_lot_density: SC.Record.attr(Number),
    single_family_small_lot_density: SC.Record.attr(Number),
    attached_single_family_density: SC.Record.attr(Number),
    multifamily_2_to_4_density: SC.Record.attr(Number),
    multifamily_5_plus_density: SC.Record.attr(Number),
    armed_forces_density: SC.Record.attr(Number),
    office_density: SC.Record.attr(Number),
    retail_density: SC.Record.attr(Number),
    industrial_density: SC.Record.attr(Number),
    residential_density: SC.Record.attr(Number),
    agricultural_density: SC.Record.attr(Number),
    combined_pop_emp_density: SC.Record.attr(Number),
    retail_services_density: SC.Record.attr(Number)
});


Footprint.PrimaryComponent = Footprint.BuiltForm.extend({
    // The PlaceTypeComponents that use the PrimaryComponent, modeled in PrimaryComponentPercents that reference
    // the percent relationship between each PlaceTypeComponent and this PrimaryComponent
    // This is not Editable
    primary_component_percent_set: SC.Record.toMany('Footprint.PrimaryComponentPercent', {
        isMaster: NO,
        nested: YES}),
    hasContainerComponentPercents: YES,
    // Generic alias
    container_component_percents: function() {
        return this.get('primary_component_percent_set');
    }.property('primary_component_percent_set').cacheable(),

    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return sc_super().concat(['primary_component_percent_set']);
    }
});

//Footprint.PrimaryComponent.isPolymorphic = YES

Footprint.PrimaryComponentPercent = Footprint.Record.extend(Footprint.ComponentPercentMixin, {
    // TODO using subclasses
    primary_component: SC.Record.toOne("Footprint.PrimaryComponent", {softInverse:'primary_component_percent_set'}),
    componentField: 'primary_component',

    placetype_component: SC.Record.toOne("Footprint.PlacetypeComponent", {softInverse:'primary_component_percents'}),
    containerField: 'placetype_component',

    percent: SC.Record.attr(Number),

    _copyProperties: function() {
        return sc_super() || [];
    },
    _skipProperties: function() {
        return (sc_super() || []).concat(['primary_component', 'placetype_component']);
    },
    _cloneSetup: function(sourceRecord, parentRecord) {
        // If we are cloning an entire PlacetypeComponent, not just the PrimaryComponentPercent
        // set the placetype_component to the parentRecord, which is the cloned PlacetypeComponent
        // Otherwise copy the sourceRecord's property
        this.set('placetype_component', parentRecord ? parentRecord : sourceRecord.get('subclassedContainer'));
        this.set('primary_component', sourceRecord.get('subclassedComponent'));
    }
});

Footprint.PlacetypeComponentCategory = Footprint.Record.extend({
    name: SC.Record.attr(String),
    description: SC.Record.attr(String)
});

Footprint.PlacetypeComponent = Footprint.BuiltForm.extend(F.BuiltFormAggregateMixin, {
    // The PrimaryComponents contained in the PlacetypeComponent by percent mix.
    // This is Editable
    primary_component_percents: SC.Record.toMany('Footprint.PrimaryComponentPercent', {
        nested: YES,
        softInverse:'placetype_component'
    }),
    component_percents: function(propKey, value) {
        if (value) {
            this.set('primary_component_percents', value)
        }
        return this.get('primary_component_percents')
    }.property('primary_component_percents').cacheable(),

    // The PlaceTypes that use the PlacetypeComponent, modeled in PlacetypeComponentPercents that reference
    // the percent relationship between each Placetype and this PlacetypeComponent
    // This is not Editable
    placetype_component_percent_set: SC.Record.toMany('Footprint.PlacetypeComponentPercent', {
        nested: YES,
        isMaster: NO
    }),
    hasContainerComponentPercents: YES,
    // Generic alias
    container_component_percents: function() {
        return this.get('placetype_component_percent_set');
    }.property('placetype_component_percent_set').cacheable(),

    component_category: SC.Record.toOne('Footprint.PlacetypeComponentCategory'),

    _cloneProperties: function () {
        return (sc_super() || []).concat(['primary_component_percents']);
    },
    _nestedProperties: function () {
        return (sc_super() || []).concat(['primary_component_percents']);
    },
    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return (sc_super() || []).concat(['placetype_component_percent_set', 'component_category']);
    }
});
//Footprint.PlacetypeComponent.isPolymorphic = YES

Footprint.PlacetypeComponentPercent = Footprint.Record.extend(Footprint.ComponentPercentMixin, {

    placetype_component: SC.Record.toOne("Footprint.PlacetypeComponent", {
        softInverse:'placetype_component_percent_set'
    }),
    componentField: 'placetype_component',

    placetype: SC.Record.toOne("Footprint.Placetype", {
        softInverse:'placetype_component_percents'
    }),
    containerField: 'placetype',

    percent: SC.Record.attr(Number),

    _copyProperties: function() {
        return sc_super() | [];
    },
    _skipProperties: function() {
        return ['placetype', 'placetype_component'];
    },
    _cloneSetup: function(sourceRecord, parentRecord) {
        // If we are cloning an entire Placetype, not just the PlacetypeComponentPercent
        // set the placetype to the parentRecord, which is the cloned Placetype.
        // Otherwise copy the sourceRecord's property
        this.set('placetype', parentRecord ? parentRecord : sourceRecord.get('subclassedContainer'));
        this.set('placetype_component', sourceRecord.get('subclassedComponent'));
    }
});


Footprint.Placetype = Footprint.BuiltForm.extend(F.BuiltFormAggregateMixin, {
    // The PlacetypeComponents contained in the Placetype by percent mix
    placetype_component_percents: SC.Record.toMany('Footprint.PlacetypeComponentPercent', {
        nested:YES,
        softInverse:'placetype'
    }),
    component_percents: function(propKey, value) {
        if (value) {
            this.set('placetype_component_percents', value)
        }
        return this.get('placetype_component_percents')
    }.property('placetype_component_percents').cacheable(),

    _cloneProperties: function () {
        return (sc_super() || []).concat(['placetype_component_percents']);
    },
    _nestedProperties: function () {
        return (sc_super() || []).concat(['placetype_component_percents']);
    }
});

//Footprint.Placetype.isPolymorphic = YES;

Footprint.BuiltFormExample = F.Record.extend({
    url_aerial: SC.Record.attr(String),
    url_street: SC.Record.attr(String),
    content: SC.Record.attr(Object),
    /**
     * Since keys need to be unique when cloning, we generate unique key
     */
    _mapAttributes: {
        key:function(record, key, random) {
            return '%@__%@'.fmt(key, random);
        }
    }
});

Footprint.Building = Footprint.PrimaryComponent.extend(F.BuildingAttributesMixin,{
    keyPrefix: 'b__',
    buildingAttributeSetStatusObserver: function() {
        if (this.get('status') === SC.Record.READY_CLEAN &&
            this.getPath('building_attribute_set.status') === SC.Record.READY_DIRTY) {
            this.get('store').writeStatus(this.get('storeKey'), SC.Record.READY_DIRTY);
        }
    }.observes('*building_attribute_set.status'),

    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set', 'flat_building_densities']);
    },
    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return (sc_super() || []).concat(['flat_building_densities']);
    }
});

Footprint.BuildingType = Footprint.PlacetypeComponent.extend(F.BuildingAttributesMixin,
    {keyPrefix: 'bt__',
    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set', 'flat_building_densities']);
    },
    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return (sc_super() || []).concat(['flat_building_densities']);
    }
});

Footprint.UrbanPlacetype = Footprint.Placetype.extend(F.BuildingAttributesMixin, {
    keyPrefix: 'pt__',
    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['building_attribute_set', 'flat_building_densities']);
    },
    _copyProperties: function() {
        // Copy read-only property. It won't be saved but makes cloning look nicer
        return (sc_super() || []).concat(['flat_building_densities']);
    }
});


Footprint.Crop = Footprint.PrimaryComponent.extend(F.AgricultureAttributesMixin, {
    keyPrefix: 'c__',

    agricultureAttributeSetStatusObserver: function() {
        if (this.get('status') === SC.Record.READY_CLEAN &&
            this.getPath('agriculture_attribute_set.status') === SC.Record.READY_DIRTY) {
            this.get('store').writeStatus(this.get('storeKey'), SC.Record.READY_DIRTY);
        }
    }.observes('*agriculture_attribute_set.status'),

    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    }
});

Footprint.CropType = Footprint.PlacetypeComponent.extend(F.AgricultureAttributesMixin, {
    keyPrefix: 'ct__',
    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    }

});

Footprint.LandscapeType = Footprint.Placetype.extend(F.AgricultureAttributesMixin, {
    keyPrefix: 'lt__',
    _saveBeforeProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    },
    // These are all be unique to the cloned BuiltForm
    _cloneProperties: function () {
        return (sc_super() || []).concat(['agriculture_attribute_set']);
    }

});

//
//
//
//Footprint.ScagLandUseDefinition = Footprint.Record.extend({
//    land_use_description: SC.Record.attr(String),
//    land_use_type: SC.Record.attr(String),
//    land_use: SC.Record.attr(Number)
//});
//
//
//Footprint.ScagLandUse = Footprint.Record..extent({
//    land_use_definition:SC. Record.toOne("Footprint.ScagLandUseDefinition", {isMaster: YES})
//})
