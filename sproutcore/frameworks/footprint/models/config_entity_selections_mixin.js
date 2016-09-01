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


sc_require('models/footprint_record');

Footprint.ConfigEntitySelections = {
    selections:SC.Record.toOne('Footprint.ConfigEntitySelection', { nested:true, isMaster: YES }),

    /**
     * This only is needed for db_entities right now, because they keyed
     * In cases where the user changes an item's key, where the item is potentially part of a selection dictionary, updates the specified selection dictionary to make sure that every unique key is represented and that non-existent keys are removed.
     * @param property: Access the base items with this.get(property)
     * @param keyItemPath: Default 'key'. The path to the key for each item
     * @param keyUpdate a dictionary of key changes from new to old, if available. This can reveal that 'foo' was updated to 'bar', thus allowing the selection for 'foo' to move to 'bar'
     */
    updateSelections: function(property, keyItemPath, keyUpdate) {
        // TODO Not used. Selections need to be saved at a user scope, not a ConfigEntity scope.
        // Get all items
        var self = this;
        var items = this.get(property);
        keyItemPath = keyItemPath || 'key';
        var itemsByKey = $.mapToCollectionsObject(
            items.toArray(),
            function(item) {
                return [item.getPath(keyItemPath)];
            },
            function(item) { return item;});
        var selectionObject = this.get('selections').get(property);
        // Remove selections whose key has disappeared.
        var clonedSelectionObject = $.extend({}, selectionObject);
        $.each(selectionObject, function(key, items) {
            if (!itemsByKey[key]) {
                delete selectionObject[key];
            }
        });
        // Make selection for any new keys, using keyUpdate if provided
        $.map(itemsByKey, function(items, key) {
            if (!selectionObject[key]) {
                var oldKey = keyUpdate[key];
                // Assign the object from the old key if available, otherwise assign the first item having the matching key
                selectionObject[key] = (oldKey && clonedSelectionObject[oldKey]) || itemsByKey[key][0]
            }
        })
    }
};

/***
 *
 * Represents a dictionary (object) keyed by DbEntity key and valued by DbEntity.
 * This is used to store the DbEntities that are selected for each key.
 * The custom transform defined below takes care of transforming the incoming dictionary from the datasources
 * to a dictionary with the same keys that Footprint.DbEntity records as the values
 * @type {*}
 */

Footprint.DbEntityDictionary = Footprint.Record.extend({
    _internal:YES,
    /**
     * Used by the Footprint.Datasource to learn the type of the dictionary items, which are all DbEntities. Normally the DataSource inquires with the RecordAttribute for the type
     * @param key
     */
    resolveAttributeType: function(key) {
       return Footprint.DbEntity;
    }
});
SC.RecordAttribute.registerTransform(Footprint.DbEntityDictionary, {
    /** @private - convert the object into a DbEntityDictionary instance with DbEntity values */
    to: function(obj, attr, recordType, parentRecord) {
        var store = parentRecord.get('store');
        return $.mapObjectToObject(
            // Incoming json object. This is a dictionary of DbEntity ids, keyed by its DbEntity key
            obj || {},
            // Map each key and id to the key and the resolved DbEntity
            function(key, id) {
                return [key, store.find(Footprint.DbEntity, id)];
            },
            // This is the output object, which we need to be a DbEntityDictionary. This will contain an attribute for each mapped key, whose value is naturally the DbEntity
            function() { return Footprint.store.createRecord(Footprint.DbEntityDictionary); }
        );
    },



    /** @private - convert an object to the raw form **/
    from: function(dbEntityDictionary) {
        return $.mapObjectToObject(
            // The DbEntity object created in the to function above.
            dbEntityDictionary || {},
            // Map each attribute name and DbEntity value to a key-value pair where the value is simply the DbEntity id
            function(key, dbEntity) {
                // Filter by kind so that we don't try to map internal SC attributes
                return isSCObjectOfKind(dbEntity, Footprint.DbEntity) ?
                    [key, dbEntity.get('id')]:
                    null;
            }
        );
    },
    /***
     * Override Footprint.Record to copy the keys without cloning the values. Make the values null and set later.
     * @param record
     */
    copyAttributes: function(record) {
        $.each(this, function(key, value) {
            record.set(key, null);
        });
        return record;
    }

    // TODO it might be possible to use this instead of updateSelections above
    //observersChildren: []
});

Footprint.ConfigEntitySelection = Footprint.ChildRecord.extend({
    _internal: YES,

    // A list of selected or default DbEntities for every unique Key
    db_entities: SC.Record.toOne(Footprint.DbEntityDictionary, {isMaster:YES}),

    _cloneProperties: function() { return 'db_entities'.w(); },

    /***
     * Returns YES if the given DbEntity is the one selected for its key according to the ConfigEntitySelection.db_entities dictionary
     * @param dbEntity The DbEntity to test
     * @return {Boolean}
     */
    isSelectedDbEntityForKey: function(dbEntity) {
       return this.get('db_entities')[dbEntity.get('key')]==dbEntity;
    },

    sets: SC.Record.toOne('Footprint.ConfigEntitySelectionSet', { nested:true, isMaster:YES})
});

Footprint.ConfigEntitySelectionSet = Footprint.ChildRecord.extend({
    // Points to the single selected or default built_form_set
    built_form_sets: SC.Record.toOne("Footprint.BuiltFormSet", {
        isMaster:YES
    }),
    // Points to the single selected or default policy_set
    policy_sets: SC.Record.toOne("Footprint.PolicySet", {
        isMaster:YES
    })
});
