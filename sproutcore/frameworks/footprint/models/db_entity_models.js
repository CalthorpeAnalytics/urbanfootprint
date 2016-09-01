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
sc_require('models/deletable_mixin');
sc_require('models/timestamps_mixin');

Footprint.DbEntity = Footprint.Record.extend(
    Footprint.Key,
    Footprint.Name,
    Footprint.Tags,
    Footprint.Deletable,
    Footprint.Timestamps,
    Footprint.Categories, {

    config_entity: SC.Record.toOne("Footprint.ConfigEntity", {
        isMaster:YES
    }),
    query: SC.Record.attr(String),
    schema: SC.Record.attr(String),
    table: SC.Record.attr(String),
    hosts: SC.Record.attr(Array),
    url: SC.Record.attr(String),
    origin_instance: SC.Record.toOne("Footprint.DbEntity"),
    source_db_entity_key: SC.Record.attr(String),
    feature_class_configuration: SC.Record.toOne("Footprint.FeatureClassConfiguration", {nested:YES}),
    feature_behavior: SC.Record.toOne("Footprint.FeatureBehavior", {isMaster:YES, softInverse:'db_entity'}),
    tags: SC.Record.toMany(Footprint.DbEntityTag, {isMaster:YES}),
    // Only used for getting the new Layer of a new DbEntity
    layer: SC.Record.toOne("Footprint.Layer", {isMaster:YES}),

    // This is only used when creating a new DbEntity to associate it back to the provisional
    // template_feature
    template_feature: SC.Record.toOne("Footprint.TemplateFeature"),

    _initialAttributes: {
        name: function (record) {
            return record.get('name') || 'New Record';
        },
        /***
         * SEt the key based on the name plus a timestamp
         * @param record
         */
        key: function (record) {
            return '%@_%@'.fmt(
                (record.get('name') || 'New Record').dasherize().replace(/-/g, '_'),
                SC.DateTime.createTimestamp()
            );
        }
    },

    /***
     * Creates needed child records and references. For now this a reference to the ConfigEntity
     * and an new FeatureBehavior, which defaults to the 'reference' Behavior. We also create
     * a FeatureClassConfiguration here with the generated flag set to true and specify the geography_scope
     * as that of the config_entity
     * @param sourceTemplate: The archetype record or matching structure via an SC.Observable.
     * Used only to pass essential info, such as the ConfigEntity
     * @private
     */
    _createSetup: function(sourceTemplate) {
        sc_super()
        this.set('config_entity', sourceTemplate.get('config_entity'));
        // TODO to server is currently creating the FeatureBehavior. If we get the point that the user
        // can configure the FeatureBehavior on create, then we'll want to re-enable this
        /*
        this.set('feature_behavior', this.get('store').createRecord(
            Footprint.FeatureBehavior, {
                db_entity: this.get('id')
            }, Footprint.Record.generateId()
        ));
        // Sets the back reference to DbEntity and defaults the Behavior to 'reference'
        this.get('feature_behavior')._createSetup(SC.Object.create({}));
         */

        /*
            TODO also created on the server for now
        // Create a simple feature_class_configuration.
        this.set('feature_class_configuration', this.get('store').createRecord(Footprint.FeatureClassConfiguration, {
            generated:YES,
            geography_scope: sourceTemplate.getPath('config_entity.id')
        }, Footprint.Record.generateId()));
        */
    },

    _cloneSetup: function(sourceRecord) {
        this.set('origin_instance', sourceRecord);
    },

    _cloneProperties: function() {
        return ['feature_class_configuration', 'feature_behavior', 'categories', 'tags'];
    },

    _copyProperties: function() {
         return ['config_entity'];
    },

    _customCloneProperties:function() {
        return {'feature_class_configuration': function(clonedParentRecord, parentProperty, areNestedRecords) {
            // For feature_class_configuration, wipe out everything from the source record for now, except the abstract_class_name.
            // In the future we will pass more things through
            var clonedFeatureClassConfiguration = this.cloneRecord(clonedParentRecord, parentProperty, areNestedRecords);
            var keepAttrs = ['abstract_class_name'];
            var attributes = clonedFeatureClassConfiguration.get('attributes');
            for (var key in attributes) {
                if (!keepAttrs.contains(key))
                    delete attributes[key];
            }
            clonedFeatureClassConfiguration.writeAttribute('generated', YES);
            return clonedFeatureClassConfiguration
        }};
    },

    _nestedProperties: function() {
        return ['feature_class_configuration'];
    },

    // Mapping of primitive attributes to other values
    _mapAttributes: {
        name: function(record, name, random) {
            return '%@_%@'.fmt(name, random);
        },
        key: function(record, key, random) {
            return '%@_%@'.fmt(key, random).slice(0,50);
        },
        // The server will have to assign the schema, table, and url--never copy the values from others
        schema: function(schema) {
            return null;
        },
        table: function(table) {
            return null;
        },
        url: function(url) {
            return null;
        }
    },

    _skipProperties: function() {
        return ['origin_instance'];
    },

    _saveAfterProperties: function() {
        // TODO we don't need to save the FeatureBehavior after right now
        // because the server creates a default version for us. Saving the FeatureBehavior
        // after will be useful once we enable DbEntity editing, so that the user can
        // change the Behavior and Intersection type. However it makes no sense to save
        // FeatureBehavior when new since the server is creating one upon saving the DbEntity
        // Eventually we should have the server defer processing on the Intersection type until
        // it gets this from the client, but we're not there yet
        //return ['feature_behavior']
        return []
    },

    _dirtyingProperties: function() {
        return ['feature_behavior'];
    },

    generated: null,
    generatedBinding: SC.Binding.oneWay('*feature_class_configuration.generated').defaultValue(null),
    /***
     * Allow deletes
     * @param record
     */
    isDeletable: function() {
        // For now client-side-created layers and cloned layers are deletable. This will be overhauled
        // when we do user permissions
        return this.getPath('feature_class_configuration.generated') || this.getPath('origin_instance');
    }.property('generated', 'origin_instance').cacheable(),
});

/***
 * Mixin the _tagSubclass
 */
Footprint.DbEntity.mixin({
    _tagSubclass:  'Footprint.DbEntityTag',

    /***
     * Don't show users the name DbEntity
     * @returns {string}
     */
    friendlyName: function() {
        return 'Layers';
    }
});
