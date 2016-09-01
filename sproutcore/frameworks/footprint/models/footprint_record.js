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


sc_require('models/footprint_record_cloning');

Footprint.Status = Footprint.Status || {};
Footprint.Record = SC.Record.extend(Footprint.RecordCloning, {

    init: function() {
        sc_super();
        this._dirtyingProperties().forEach(function(property) {
            this.addObserver('*%@.status'.fmt(property), this, 'propertyShouldDirtyMainRecord' )
        }, this);
    },
    /***
     * When a dirtyingProperty becomes dirty, we make the main record dirty too if it was clean
     */
    propertyShouldDirtyMainRecord: function() {
        if (this.get('status') === SC.Record.READY_CLEAN) {
            this.get('store').writeStatus(this.get('storeKey'), SC.Record.READY_DIRTY);
        }
    },

    primaryKey: 'id',

    // Used a pseudo-status property to track that cloning of new record's child items are complete
    // Each cloned child item will receive this READY_NEW_CLONED status for its _status property
    _status: null,

    // Optional undo/redo management of the record on the client
    undoManager: null,

    // Used to track progress of saving the record on the server. The value is between 0 and 1.
    // This only applies to records like ConfigEntity which do postSave processing on the server
    // When post-processing begins, their progress is set to 0, so saveInProgress will return true
    // until post-processing events bring the value back to 1.
    progress: function(propKey, value) {
        if (typeof(value) !== 'undefined') {
            Footprint.Record.progress.set(this.get('storeKey'), value);
        }
        return Footprint.Record.progress.get(this.get('storeKey'));
    }.property(),

    // Caching this isn't reliable. I don't know why
    saveInProgress: function() {
        return this.get('progress') != null && this.get('progress') >= 0 && this.get('progress') < 1;
    }.property("progress"),

    properties: function() {
        return this.get('attributes') ?
            $.map(this.get('attributes'), function(value, key) {return key;}) :
            [];
    }.property('attributes'),

    //TODO local backup of record for editing. We might place this with a call to the server in the future.
    //http://www.veebsbraindump.com/2010/10/sproutcore-crud-tutorial-using-sc-tableview/
    /**
     * Return an object containing a backup of the properties
     * @returns SC.Object object containing properties to backup
     */
    backupProperties: function() {
        var self = this;
        return $.mapObjectToObject(
            this.get('attributes'),
            function(key, value) {
                return [key, self.get(key)];
            },
            function() {return SC.Object.create(); }
        );
    },

    /***
     * Sets (reverts) a records attributes to those given in the context
     * set is used so that observers are notified, thus the context must have full record values, not just ids
     * @param recordOrDataHash: A record or object that is iterated over to set the matching attribute values of the record
     * @param omitAttributes: Skip any attribtues specified in this array
     */
    replaceDataHash: function(recordOrDataHash, omitAttributes) {
        var store = this.get('store');
        var storeKey = this.get('storeKey');
        var dataHash = SC.clone(recordOrDataHash.kindOf ?
            store.readDataHash(recordOrDataHash.get('storeKey')) :
            recordOrDataHash);
        // Make sure the server id is set. The server expects the id to be in the dataHash
        dataHash['id'] = this.get('id');
        store.writeDataHash(storeKey, removeKeys(dataHash, omitAttributes || []));
    },
    /***
     * Used to copy the attribute values of a record, for use in updateRecordAttributes.
     * Related records are resolved, rather than just fetching ids.
     */
    cloneAttributes: function() {
        var self = this;
        return $.mapObjectToObject(this.getPath('attributes'), function(attribute, value) {
            return [attribute, self.get(attribute)];
        });
    },

    autonomousStore: null,
    autonomousStoreBinding: SC.Binding.oneWay('Footprint.store.autonomousStore'),

    /***
     * Returns a version of the record from the universal nested store if this record is of the main store
     * @param store
     * @returns {*|SC.Cookie|SC.Record|{}|Object|SC.CSSStyleSheet}
     */
    nestedStoreVersion: function() {
        return Footprint.store.get('autonomousStore').find(this.constructor, this.get(this.get('primaryKey')));
    }.property('autonomousStore').cacheable(),
    /***
     * Returns the version of the record from the main store if this record is of the nested store
     */
    mainStoreVersion: function() {
        return Footprint.store.find(this.constructor, this.get(this.get('primaryKey')));
    }.property('autonomousStore').cacheable(),

    // Properties not to copy or clone--typically properties that the server should take care of copying from the source
    _skipProperties:function() {return ''.w();},
    // Properties for cloneRecord to copy
    _copyProperties:function() {return ''.w();},
    // Properties for cloneRecord to clone (recursive cloneRecord)
    // Order doesn't matter unless a _customCloneProperties function makes use of a newly cloned sibling item
    _cloneProperties:function() {return ''.w();},
    // Use in conjunction with cloneProperties to prevent nested properties from being loaded prior to cloning (they are already loaded!)
    _nestedProperties:function() {return ''.w();},
    // Properties that need a custom function to clone them.
    // For toOne attributes the function receives as arguments the cloned record as this and the source record as an argument
    // For toMany attributes the function is called for each cloned record as this and the source record as an argument
    // The function must return a clone of the source record property value
    _customCloneProperties:function() { return {}; },

    // Child attributes to save before saving this record
    _saveBeforeProperties: function() { return [] },
    // Child attributes to save after saving this record
    _saveAfterProperties: function() { return [] },

    /***
     * The properties listed should dirty the main record when they become dirty.
     * This is needed for non-nested properties when the main record needs to be marked dirty as a result
     * of their update
     * @private
     */
    _dirtyingProperties: function() { return [] },

    /***
     * Mapping of primitive attributes to other values, Each key/value takes the form:
     * key: function(cloneRecord, original record value, random number) { return key+random;}
     * where key is the attribute to map and original record value is the corresponding attribute value of the source record.
     * random provides a short timestamp for things that should be unique or replaced by the user
    **/
    _mapAttributes: { },
    /***
     * Like map attributes but for initialization. No original record value is passed in, so the key/values take the form :
     * key: function(cloneRecord, random number) { return "New'+random;}
     */
    _initialAttributes: { },

    // Properties that should never be transfered from one instance to another when updating the values of one instance to those (or the clones) of another
    _nonTransferableProperties: function() { return 'id resource_uri'.w(); },

    // Special actions for setting up a create from "scratch"
    // The sourceRecord is used to prime the pump--to give the instance essential attributes like parent references
    _createSetup: function(sourceRecord) {
        // Initialize preconfigured primitive attributes
        var self = this;
        var randomNumber = SC.DateTime.create().toFormattedString('%H_%M_%S');
        $.each(this._initialAttributes || {}, function(key, func) {
            self.set(key, func(self, randomNumber))
        });
    },
    // Special actions to take when setting up a record for cloning
    // that don't involve cloning particular attributes
    // For example, a clone might set its origin_instance to the source_record (this should just be standard)
    _cloneSetup: function(sourceRecord) {

    },
    /***
     * Sets the record's deleted property to YES. Override to do the same for nested records
     * TODO nested records should just be listed as nestedRecords so the crud state knows how
     * to create and delete all nested records
     * @private
     */
    _deleteSetup: function() {
        this.set('deleted', YES)
    },

    attributeKeys: function() {
        return $.map(this.attributes(), function(v,k) { return k;});
    },
    /***
     * Some recordTypes, namely Layer, need to delegate to a more fundamental record for CRUD updates
     * @returns: Normally returns this.
     * @private
     */
    _recordForCrudUpdates: function() {
        return this;
    },

    /**
      Major override to mark 'parent' records with what property is dirtying them
     */
    propagateToAggregates: function() {
        var storeKey   = this.get('storeKey'),
            recordType = SC.Store.recordTypeFor(storeKey),
            aggregates = recordType.__sc_aggregate_keys,
            idx, len, key, prop, val, recs;

        // if recordType aggregates are not set up yet, make sure to
        // create the cache first
        if (!aggregates) {
            aggregates = [];
            for (key in this) {
                prop = this[key];
                if (prop  &&  prop.isRecordAttribute  &&  prop.aggregate === YES) {
                    aggregates.push(key);
                }
            }
            recordType.__sc_aggregate_keys = aggregates;
        }

        // now loop through all aggregate properties and mark their related
        // record objects as dirty
        var K          = SC.Record,
            dirty      = K.DIRTY,
            readyNew   = K.READY_NEW,
            destroyed  = K.DESTROYED,
            readyClean = K.READY_CLEAN,
            iter;

        /**
         @private

         If the child is dirty, then make sure the parent gets a dirty
         status.  (If the child is created or destroyed, there's no need,
         because the parent will dirty itself when it modifies that
         relationship.)

         @param {SC.Record} record to propagate to
         */
        iter =  function(rec, index) { // ABL add index to resolve aggregate
            var childStatus, parentStore, parentStoreKey, parentStatus;

            /***
             * Resolve the attribute that points from the parent (rec) to the child
             * by searching for the attribute is the right instance type and contains
             * the child instance. This will always return an attribute unless the child or
             * parent are new, meaning that the two-way relationship hasn't been set yet
             * @returns {*}
             */
            function resolveChildAttributeKey() {
                var childId = this.get('id');
                var child = this;
                return rec.constructor.allRecordAttributeProperties(function (recordAttribute, key) {
                    // Evaluate the recordAttribute id and type to find our match
                    // If so check of an instance match. This should safely identify the attribute that caused this
                    // aggregate update
                    return recordAttribute['isMaster'] && !recordAttribute['isNested'] &&
                        child.instanceOf(resolveObjectForPropertyPath(recordAttribute.type)) &&
                        arrayOrItemToArray(rec.readAttribute(key)).contains(childId) &&
                        arrayOrItemToArray(rec.get(key)).contains(child);
                }).get('firstObject');
            }

            parentStore    = rec.get('store');
            parentStoreKey = rec.get('storeKey');
            if (rec) {
                childStatus = this.get('status');
                var previous = (rec.readAttribute('_updatedAttributes') || []);
                // Find the attribute that relates the parent to the child
                // This will be null if the parent or child are new and the two way relationship
                // hasn't yet been set up
                var recordAttributeKey = resolveChildAttributeKey.apply(this);
                if (recordAttributeKey && rec.constructor.prototype[recordAttributeKey].nested)
                    throw "We should never be here for nested attributes";
                if ((childStatus & dirty)  ||
                    (childStatus == readyNew)  ||  (childStatus & destroyed)) {

                    if (recordAttributeKey) {
                        // If we're dealing with new records
                        // Tell the parent that its child attribute has been updated. We have to do
                        // this here because recordDidChange will not pick up the change to the parent's
                        // child attribute when the child status becomes dirty
                        var updated = SC.Set.create((rec.readAttribute('_updatedAttributes') || []).concat([recordAttributeKey])).toArray();
                        if (0 != SC.compare(previous, updated)) {
                            rec.writeAttribute(
                                '_updatedAttributes',
                                updated
                            );
                        }
                    }

                    // Since the parent can cache 'status', and we might be called before
                    // it has been invalidated, we'll read the status directly rather than
                    // trusting the cache.
                    parentStatus = parentStore.peekStatus(parentStoreKey);
                    if (parentStatus === readyClean) {
                        rec.get('store').recordDidChange(rec.constructor, null, rec.get('storeKey'), null, YES);
                    }
                }
                // ABL: If the record has become clean, we remove the attribute from the parent's _updatedAttributes
                else if (childStatus == readyClean) {
                    /***
                     * The child is now clean, so remove the attribute from the parent's _updatedAttributes attribute
                     */
                    if (recordAttributeKey) {
                        var updated = previous.copy().removeObject(recordAttributeKey);
                        if (0 != SC.compare(previous, updated)) {
                            // ABL update _updatedAttributes and announce that the record has changed
                            // This might make the record clean if it was previously dirty but now has no _updatedAttribtues
                            rec.writeAttribute('_updatedAttributes', updated);
                            rec.get('store').recordDidChange(rec.constructor, null, rec.get('storeKey'), null, NO);
                        }
                    }
                }
            }
        };

        for(idx=0,len=aggregates.length;idx<len;++idx) {
            key = aggregates[idx];
            val = this.get(key);
            recs = SC.kindOf(val, SC.ManyArray) ? val : [val];
            recs.forEach(iter, this);
        }
    },

    /***
     * Default toString dumps the record attributes, or failing that the id.
     * It never dumps inverse record attributes to prevent infinite loops
     * @returns {*}
     */
    dump: function() {
        return "%@:\n%@".fmt(
            sc_super(),
            this.toStringAttributes(
                this.get('attributes') ?
                    this.constructor.allRecordAttributeProperties(function(recordAttribute) {
                        return !recordAttribute.get('inverse')
                    }) : ['id']
            )
        );
    }
});

/***
 * Override this to limit the class name used by the subclasses to a base class name, or to use a custom name
 * @returns {string}
 */
SC.mixin(Footprint.Record, {

    generateId: function() {
        return -Math.random(Math.floor(Math.random() * 99999999));
    },

    /***
     * Return a baseclass for certain record types
     * @param recordType
     * @returns {*}
     */
    apiRecordType: function() {
        return this;
    },

    /**
     * Map the name to somthing else for certain record types, if apiRecordType doesn't take care of it
     * @returns {null}
     */
    apiClassName: function() {
        return null;
    },

    /***
     * Override with a friendly name to send to the UI
     * @returns {*}
     */
    friendlyName: function() {
        return null;
    },

    infoPane: function() {
        return null;
    },

    /***
     * Returns the attribute keys of this model class
     * Optionally pass a filter function that expects the RecordAttribute and its key (property name)
     * @returns {*}
     */
    allRecordAttributeProperties: function(filter) {
        filter = filter || function(recordAttribute) { return YES; };
        var prototype = this.prototype;

        var self = this;
        var filteredProperties = $.map(prototype, function (value, key) {
            // value.kindOf(SC.Binding) ensures agains SC.Bindings, which delegate kindOf to the bound value
            // or something weird
            return value && value.kindOf && (value.kindOf(SC.RecordAttribute) && !value.kindOf(SC.Binding)) &&
                filter.apply(self, [value, key]) ?
                key :
                null;
        }).compact();
        var parentRecordType = prototype.__proto__;
        return parentRecordType.allRecordAttributeProperties ?
            filteredProperties.concat(parentRecordType.allRecordAttributeProperties(filter)) :
            filteredProperties;
    },


    /***
     * Custom processes of a record's raw dataHash prior to saving
     * @param dataHash
     */
    processDataHash: function(dataHash, record) {
        return dataHash;
    },

    progress: SC.Object.create(),

    // All states that indicate some stage of editing
    EDITING_STATES: [SC.Record.READY_NEW, SC.Record.READY_DIRTY, SC.Record.BUSY_COMMITTING, SC.Record.BUSY_CREATING]
});


Footprint.ChildRecord = Footprint.Record.extend({
});

Footprint.ChildRecord = Footprint.Record.extend({
});
