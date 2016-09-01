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


sc_require('models/config_entity_selections_mixin');
sc_require('models/geographic_bounds_mixin');
sc_require('models/name_mixin');
sc_require('models/key_mixin');
sc_require('models/deletable_mixin');
sc_require('models/categories_mixin');
sc_require('models/backup_properties_mixin');
sc_require('models/analysis_module_model');

/***
 * Creates a special equality operator $ to evaluate if two records have the same id to get around the query
 * language's uncanny inability to handle inheritance
 */
SC.Query.registerQueryExtension(
    '$', {
        reservedWord: true,
        leftType: 'PRIMITIVE',
        rightType: 'PRIMITIVE',
        evalType: 'BOOLEAN',

        /** @ignore */
        evaluate: function (r, w) {
            var left = this.leftSide.evaluate(r, w);
            var right = this.rightSide.evaluate(r, w);
            return left && right && left.get('id') == right.get('id')
        }});

Footprint.ConfigEntity = Footprint.Record.extend(
    Footprint.ConfigEntitySelections,
    Footprint.GeographicBounds,
    Footprint.Name,
    Footprint.Key,
    Footprint.Deletable,
    Footprint.Categories,
    Footprint.BackupProperties, {

    isPolymorphic: YES,

    parent_config_entity: SC.Record.toOne('Footprint.ConfigEntity', { isMaster: YES}),
    origin_instance: SC.Record.toOne('Footprint.ConfigEntity', { isMaster: YES}),
    media: SC.Record.toMany('Footprint.Medium', { nested: NO}),

    presentations: SC.Record.toOne("Footprint.PresentationTypes", {
        nested:YES
    }),

    behavior: SC.Record.toOne("Footprint.Behavior", {
        nested:NO
    }),

    creator: SC.Record.toOne("Footprint.User", {
        nested:YES
    }),
    updater: SC.Record.toOne("Footprint.User", {
        nested: YES
    }),

    policy_sets: SC.Record.toMany("Footprint.PolicySet"),

    built_form_sets: SC.Record.toMany("Footprint.BuiltFormSet"),

    db_entities: SC.Record.toMany("Footprint.DbEntity"),

    groups: SC.Record.toMany('Footprint.Group', {isMaster: NO, inverse: 'config_entity'}),

    // When cloning, reference these properties--don't clone them
    _copyProperties: function () {
        return ['parent_config_entity'];
    },
    // When cloning, clone these properties, creating new records for each
    _cloneProperties: function () {
        // This is done on the server for now
        return [];
    },
    _skipProperties: function() {
        // Skip most everything from now and let the server handle it
        return [
            'policy_sets',
            'built_form_sets',
            'categories',
            'db_entities',
            'presentations',
            'selections',
            'scope',
            'schema'];
    },

    // Distinguish the key and name in the cloned item
    // The key is synced to the name in key_mixin.js
    _mapAttributes: {
        name: function (record, name, random) {
            // Since we expect our random to be in this format hh_mm_ss,
            // remove an existing random from the name if we are cloning from a clone
            // and the user didn't make the name something nice.
            // This random string format is set in footprint_record_cloning.copyAttributes
            var regexedName = name.replace(/ \d{2}_\d{2}_\d{2}$/, '');
            return '%@ %@'.fmt(regexedName, random);
        }
    },
    _initialAttributes: {
        name: function (record, random) {
            return '%@'.fmt(random);
        }
    },

    // Even a newly created ConfigEntity needs a parent
    _createSetup: function(sourceRecord) {
        sc_super()
        this.set('parent_config_entity', sourceRecord.get('parent_config_entity'));
    },
    // Set the origin config_entity
    _cloneSetup: function(sourceRecord) {
        this.set('origin_instance', sourceRecord);
    },

    _nonTransferableProperties: function () {
        return ['origin_instance'];
    },

    _saveAfterProperties: function() {
        return [];
    },

    /**
     * record type of the child ConfigEntities
     */
    childRecordType: null,
    /*
     * Find the children based on childRecordType
     * The $ makes it match on id in case the class types differ
     */
    children: function () {
        if (!this.get('childRecordType'))
            return [];

        return this.get('store').find(SC.Query.local(
            SC.objectForPropertyPath(this.get('childRecordType')), {
                conditions: 'parent_config_entity $ {configEntity} AND deleted=NO',
                configEntity: this,
                orderBy: 'name'
            }
        ))
    }.property().cacheable(),

    /***
     * Performs the given function on this and all children, and optionally recursively
     * Returns the result of func flattened if needed
     */
    forSelfAndChildren: function(func, recurse) {
        // Do the function on this ConfigEntity
        var results = [func(this)];
        // Do it on each child
        this.get('children').forEach(function(child) {
           results.pushObjects(child.forSelfAndChildren(func, recurse));
        });
        return results
    },

    /***
     * All ConfigEntities including
     */
    ancestors: function() {
       return [this].concat(this.getPath('parent_config_entity.ancestors') || [])
    }.property().cacheable(),

    // Defines an undo manager for the children records of this ConfigEntity. This allows CRUD operations on
    // all of its children to be buffered for undo/redo actions. Thus a user might edit one child, create
    // another, remove another, etc, and it would all be in a single undo buffer. This also allows bulk operations
    // to be in the buffer, such as changing the Category values of several children at once.
    childrenUndoManager:null,

    // Undo manager for the individual instance,
    undoManager: null,

    writeStatus: function() {
        sc_super()
    },
    /***
     * A readable name of the ConfigEntity class.
     * TODO localize
     * @returns {*|String}
    */
    classTitle: function() {
        return this.get('constructor').toString().split('.')[1].titleize();
    }
});

Footprint.GlobalConfig = Footprint.ConfigEntity.extend({
    childRecordType: 'Footprint.Region'
});

Footprint.Region = Footprint.ConfigEntity.extend({
    childRecordType: 'Footprint.Project',

    // The Region's parent_config_entity may be the GlobalConfig singleton or the another Region.
    // Use a computed relationship to determine the record type.
    parent_config_entity: SC.Record.toOne(function () {
        return this.readAttribute('parent_config_entity') ==
            this.store.find(
                SC.Query.local(Footprint.GlobalConfig))
            .toArray()[0].get('id') ?
                Footprint.GlobalConfig :
                Footprint.Region;
    }),
    // Override to support Regions adn Projects as children
    children: function () {
        return this.get('store').find(SC.Query.local(
            [Footprint.Region, SC.objectForPropertyPath(this.get('childRecordType'))], {
                conditions: 'parent_config_entity $ {configEntity} AND deleted=NO',
                configEntity: this,
                orderBy: 'name'
            }
        ))
    }.property().cacheable(),
});

Footprint.Project = Footprint.ConfigEntity.extend({
    init: function() {
        sc_super();
        // Since Projects will usually make use of the childrenUndoManager, create it on init.
        if (!this.get('childrenUndoManager'))
            this.childrenUndoManager = SC.UndoManager.create();
    },

    childRecordType: 'Footprint.Scenario',
    base_year: SC.Record.attr(Number),
    // Override ConfigEntity's definition so that the API knows to look up a Region
    parent_config_entity: SC.Record.toOne('Footprint.Region', { isMaster: YES }),
    // The parent_config_entity is always a Region, so we can provide this synonym property
    region: function () {
        return this.get('parent_config_entity');
    }.property('parent_config_entity')
});
