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


Footprint.PresentationMedium = Footprint.Record.extend({
    isPolymorphic: YES,
    deleted: SC.Record.attr(Boolean),

    medium: SC.Record.toOne('Footprint.Medium', {
        nested: YES,
    }),

    name: SC.Record.attr(String),

    // This is what is actually owned by the PresentationMedium
    // DbEntity is a property of presentation.config_entity
    db_entity: SC.Record.toOne('Footprint.DbEntity'),

    creator: SC.Record.toOne('Footprint.User', {
        nested:YES,
    }),
    updater: SC.Record.toOne('Footprint.User', {
        nested: YES,
    }),

    dbEntityKey: function() {
        return this.getPath('db_entity.key');
    }.property('db_entity', 'dbEntityStatus').cacheable(),

    dbEntityStatus: null,
    dbEntityStatusBinding: SC.Binding.oneWay('*db_entity.status').defaultValue(null),

    /***
     * This is overrriden in Layer to be a Footprint.LayerStyle
     * Result might do something similiar once we start styling Results
     */
    configuration: SC.Record.attr(Object),

    // Indicates if the instance is visible by default (such as a layer's visibility on a map)
    visible: SC.Record.attr(Boolean, {defaultValue: NO}),
    // Unused for now
    solo: SC.Record.attr(Boolean, {defaultValue: NO}),
    // Indicates that the layer is visible in the application.
    // This differs from visible which indicates visible value from the server
    // Whe we start saving visibility per user, this attribute will be saved to the user's settings
    applicationVisible: null,
    visibleObserver: function() {
        this.setIfChanged('applicationVisible', this.get('visible'));
    }.observes('.visible'),

    visibility: function (propKey, value) {
        if (value === undefined) {
            return this.get('solo') ? Footprint.SOLO : (this.get('applicationVisible') ? Footprint.VISIBLE : Footprint.HIDDEN);
        } else {
            if ([Footprint.VISIBLE, Footprint.HIDDEN].contains(value)) {
                // Only change the value of the visible property if VISIBLE or HIDDEN are chosen
                // This allows us to maintain the visible property value while the item is soloing
                // TODO We don't update the actual visible property because we don't want to dirty the record
                this.set('applicationVisible', value == Footprint.VISIBLE);
            }
            this.set('solo', value == Footprint.SOLO);
        }
    }.property('applicationVisible', 'solo').cacheable(),

    sortPriority: function (key, value) {
        // Getter.
        if (value === undefined) {
            return this.getPath('configuration.sort_priority') || null;
        } else {
        // Setter.
            var configuration = this.get('configuration');
            if (configuration) {
                configuration.sort_priority = value;
                this.notifyPropertyChange('configuration');
            }
            return value;
        }
    }.property('configuration'),

    /**
     * Convenience method to fetch a Category value of the DbEntity by key
     * It is assumed that only one value is in the collection for the given key
     * @param key
     */
    categoryValue: function(key) {
        if (!(this.getPath('db_entity.status') & SC.Record.READY))
            return null;
        return this.getPath('db_entity.categories').filterProperty('key', key).getPath('firstObject.value') || null;
    },

    categoryRecord: function(key) {
        if (!(this.getPath('db_entity.status') & SC.Record.READY))
            return null;
        return this.getPath('db_entity.categories').filterProperty('key', key).get('firstObject') || null;
    },

    _copyProperties: function () {
        return ['presentation'];
    },
    _cloneProperties: function () {
        // medium is nested so needs clone but saves with the main record
        return ['medium'];
    },
    _nestedProperties: function() {
        return ['medium'] ;
    },
    _saveBeforeProperties: function () {
        return [];
    },

    _mapAttributes: {
        name: function (record, name, random) {
            return '%@_%@'.fmt(name, random);
        },
    },
    _initialAttributes: {
        name: function (record, random) {
            return 'New %@'.fmt(random);
        },
    },

    // Setup for brand new instances
    // sourceRecord is the architype in the case of new instance
    // we have to have a presentation and medium structure based on a peer record
    _createSetup: function(sourceRecord) {
        sc_super();

        this.set('presentation', sourceRecord.get('presentation'));

        // This will be replaced by the server, but is required, so copy and null out
        // TODO cloneRecord should support a param to do a structural clone without copying primitive values
        this.set('medium', sourceRecord.get('medium').cloneRecord());

        // TODO these will be created by the server for now.
        // When we start doing a style editor these will need ot be exposed
        //this.set('configuration', sourceRecord.get('configuration'));
        //this.set('medium_configuration', sourceRecord.get('medium_configuration'));
        this.set('dbEntityKey', this.getPath('db_entity.key'));
    },


    _deleteSetup: function() {
        sc_super();
        // Set nested records to be deleted as well
        this.setPath('medium.deleted', YES);
    },

    featureRecordType: function() {
        var dbEntityKey = this.get('dbEntityKey');
        if (!dbEntityKey) {
            // This is a huge hack: sometimes, the dbEntity hasn't
            // finished loading, but all we really need is the
            // dbEntityKey. We can usually infer this from the
            // active_style_key, which is in the form
            // <db_entity_key>__default.
            var activeStyleKey = this.get('active_style_key');
            if (activeStyleKey && activeStyleKey.endsWith('__default')) {
                dbEntityKey = activeStyleKey.slice(0, -9);
            }
        }
        if (dbEntityKey) {
            // Try to get the Feature subclass of the DbEntityKey or default to Feature
            return Footprint.featuresActiveController.getPath(
                'dbEntityKeyToFeatureRecordType.%@'.fmt(this.get('dbEntityKey'))) ||
                Footprint.Feature;
        }
    }.property('dbEntityKey', 'dbEntityKeyToFeatureRecordType').cacheable(),
    dbEntityKeyToFeatureRecordType: null,
    dbEntityKeyToFeatureRecordTypeBinding: SC.Binding.oneWay('Footprint.featuresActiveController.dbEntityKeyToFeatureRecordType').defaultValue(null),

    undoManager: null,

    isDeletable: function() {
        return this.getPath('db_entity.isDeletable');
    }.property('db_entity').cacheable(),
});
