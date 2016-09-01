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


/****
  * Mixin to Footprint.Record that handles cloning records
*/
Footprint.RecordCloning = {

    /***
     * Clones this record. Cloning is recursive on any properties listed in _cloneProperties.
     * ToOne or ToMany properties should be listed in _cloneProperties or _copyProperties
     * Primitive attributes need not be listed. They will be copied in copyAttributes
     * cloneRecord must not be called until all deep child attributes are status READY, excepting attributes of
     * child objects that are merely being copied by reference.
     * @param store
     * @param parentClonedRecord: set for recursive calls to identify the parent cloned record. This is used to set isMaster:NO attributes back to the parentRecord
     * @param parentProperty: set for use with areNestedRecords to allow cloning a nested record
     * @param areNestedRecords: true is the record being cloned is a nested record. In this case we use the parentCloneRecord.get(parentProperty) to get the ChildArray
     *  and then create the record via the ChildArray
     * @returns {*} Returns the clonedRecord with a READY_NEW status.
     */
    cloneRecord: function(parentClonedRecord, parentProperty, areNestedRecords) {

        var newRecord = areNestedRecords ?
            parentClonedRecord.get(parentProperty).createNestedRecord(
                this.constructor, {}
            ) :
            this.get('store').createRecord(
                this.constructor,
                {},
                Footprint.Record.generateId()
            );

        // Do a clone setup for the record to set up attributes not copied from the source
        newRecord._cloneSetup(this, parentClonedRecord);

        newRecord._cloneOrCopyChildAttributes(parentClonedRecord, this);

        // Copy the primitive attributes
        this.copyAttributes(newRecord);

        return newRecord;
    },

    _copyMany: function(property, value) {
        // Handle many attributes
        var areNestedRecords = this[property].constructor == SC.ChildrenAttribute;
        if (!areNestedRecords) {
            this.get(property).pushObjects(value)
        }
        else {
            // Copy the attributes of each nested record into the cloned record's ChildArray
            value.forEach(function(item) {
                var attributes = item.attributes();
                // Handle an SC nested record, nested store combo bug where the nestedRecord becomes unregistered
                // by the store
                if (!attributes) {
                    var message = "Could not perform clone due to a bug in the framework. Please close the dialog box and try again.";
                    SC.AlertPane.error({
                        message: 'Framework Error',
                        description: message,
                        buttons: [{
                            title: 'OK'
                        }]
                    });
                    throw Error(message);
                }

                this.get(property).createNestedRecord(
                    item.constructor,
                    item.attributes())
            }, this);
        }
        return value;
    },
    _copyOne: function(property, value) {
        // Handle a toOne attribute
        // We write the attribute to records that are not yet loaded
        // but we don't need to load. An example is the db_entity of feature_behavior,
        // where the db_entity is loaded as a nested record of db_entity_interest (no loger exists)
        // so the non-nested reference of feature_behavior is not yet loaded
        this.writeAttribute(property, value.get('id'));
        return value;
    },
    _cloneMany: function(property, value, parentClonedRecord) {
        var store = this.get('store');
        // Clone each item of the many property normally or with the configured custom function
        var areNestedRecords = this[property].constructor == SC.ChildrenAttribute;
        var clonedItems = value.map(function(item) {
            return this._customCloneProperties()[property] ?
                this._customCloneProperties()[property].apply(item, [this, property, areNestedRecords]) :
                item.cloneRecord(this, property, areNestedRecords)
        }, this).compact();
        if (!areNestedRecords)
            // Only push objects if non-nested. cloneRecord will have added the cloned item to the ChildArray
            clonedItems.forEach(function(clonedItem) {
                // We only need to push if the inverse relationship is not defined on the record definition
                if (!this.get(property).contains(clonedItem))
                    this.get(property).pushObject(clonedItem);
            }, this);
        return clonedItems;
    },
    _cloneOne: function(property, value, parentClonedRecord) {
        var store = this.get('store');
        //TODO handle toOne nested attributes
        var clonedItem = this._customCloneProperties()[property] ?
            this._customCloneProperties()[property].apply(value, [this, property]) :
            value.cloneRecord(this, property);
        this.set(property,clonedItem);
        return clonedItem;
    },

    /***
     * For a clonedRecord copy or clone properties from the sourceRecord
     * @param sourceRecord: Source records whose attributes we're cloning or referencing
     * @param parentClonedRecord: For child attribute records, the parent cloned record
     * @returns {*}
     * @private
     */
    _cloneOrCopyChildAttributes: function(parentClonedRecord, sourceRecord) {
        // Since we'll combine the copyProperties and clounderstandneProperties in our toProperty function below, create
        // a convenient lookup that tells us how to process each by index
        var propertyLookup = $.map(this._copyProperties(), function(property) {
            return {
                property:property,
                type:'copy',
                one:sourceRecord._copyOne,
                many:sourceRecord._copyMany
            };
        }).concat($.map(this._cloneProperties(), function(property) {
            return {
                property:property,
                type:'clone',
                one:sourceRecord._cloneOne,
                many:sourceRecord._cloneMany
            };
        }));
        propertyLookup.forEach(function(propertyInfo) {
            var propertyValue = sourceRecord.get(propertyInfo.property);
            Footprint.CloneOrCopy.create({
                sourceRecord:this,
                parentClonedRecord:parentClonedRecord,
                propertyInfo: propertyInfo,
                propertyValue: propertyValue
            });
        }, this);
    },

    /**
     * Copy any primitive attributes that are not ids and are not returned by _skipProperties(), _copyProperties(), _cloneProperties
     * @param record
     * @returns {*}
     */
    copyAttributes: function(record) {
        var self = this;
        var randomNumber = SC.DateTime.create().toFormattedString('%H_%M_%S');
        $.each(this.attributes() || {}, function(key, value) {
            if (!['id', 'resource_uri'].concat(
                self._skipProperties(),
                self._copyProperties(),
                self._cloneProperties(),
                self._nonTransferableProperties(),
                $.map(self._customCloneProperties(), function(value, key) {return key;})).contains(key))
            {
                record.set(key, self._mapAttributes[key] ? self._mapAttributes[key](record, value, randomNumber) : value);
            }
        });
        return record;
    },

    /***
     * Recursively load all complex attributes and return a flat list. This is used to check/await statuses
     * @param record
     */
    loadAttributes: function(_alreadyFound, propertyPath) {
        _alreadyFound = _alreadyFound || SC.Set.create();
        propertyPath = propertyPath || [];

        if (_alreadyFound.contains(this))
            return;
        else
            _alreadyFound.add(this);

        var record = this;
        // Combine the keys of non-primitive attributes that need cloning and return the corresponding record value
        // Nulls are excluded
        var clonePropertyPairs = SC.Set.create().addEach(
                $.shallowFlatten(
                    this._cloneProperties(),
                    $.map(this._customCloneProperties(), function(value, key) {return key;}))
            ).removeEach(
                // No nead to load nested properties
                this._nestedProperties()
            ).map(function(key) {
                var value = record.get(key);
                return value ? {key:key, value:value} : null;
            }).compact();

        // Fetch separately the copy by reference attributes. We won't recurse on these
        var referencePropertyPairs = [].concat(
            this._copyProperties()
            ).map(function(key) {
                    var value = record.get(key);
                    return value ? {key:key, value:value} : null;
            }).compact().filter(function(propertyValue) {
                return propertyValue.kindOf && propertyValue.kindOf(Footprint.Record);
            });

        // Recurse on each attribute value if it is itself a record or an enumerable of records
        // Use $.map to force a flatten of the inner arrays
        // Prepend this record to the result list.
        // Nulls are excluded
        return (propertyPath.get('length') ? [{key:propertyPath.join("."), value:this}] : []).concat(referencePropertyPairs, $.map(clonePropertyPairs, function(propertyPair) {
            var propertyValue = propertyPair.value;
            var propertyKey = propertyPair.key;
            if (propertyValue.kindOf && propertyValue.kindOf(Footprint.Record)) {
                // Footprint Record instance
                return propertyValue.loadAttributes(_alreadyFound, propertyPath.concat([propertyKey]));
            }
            else if (propertyValue.isEnumerable) {
                // Enumerable
                return jQuery.map(propertyValue.toArray(), function(propertyValueItem, i) {
                    // Possibly Footprint Record instances
                    if (propertyValueItem.kindOf && propertyValueItem.kindOf(Footprint.Record)) {
                        return propertyValueItem.loadAttributes(_alreadyFound, propertyPath.concat([propertyKey, i]));
                    }
                }).compact();
            }
        }).compact())
    }
};

 Footprint.CloneOrCopy = SC.Object.extend({

     clonedRecord:null,
     parentClonedRecord: null,
     propertyInfo:null,
     propertyValue:null,
     property:null,

     clonedChildItems:null,

     init: function() {
         sc_super();
         this.set('property', this.getPath('propertyInfo.property'));
         this.set('clonedChildItems', []);
         this.cloneOrCopyProperty();
     },

     // When the child source attribute record or record array is READY_CLEAN call the many or one function where either copies or clones child property values
     // Clones will be asynchronous so we push items to _cloningChildItems and wait for them to complete
     cloneOrCopyProperty: function() {
         // We need to do this to mark toMany attributes that don't set statuses as complete, namely ChildArray
         if (!this.getPath('propertyValue.status')===SC.Record.READY_CLEAN)
            this.setPath('propertyValue.status', SC.Record.READY_CLEAN);

         var sourceRecord = this.get('sourceRecord');
         var parentClonedRecord = this.get('parentClonedRecord');
         var property = this.get('property');
         var propertyInfo = this.get('propertyInfo');
         var propertyValue = this.get('propertyValue');
         var clonedChildItems = this.get('clonedChildItems');

         if (!propertyValue) {
             return;
         }
         if (sourceRecord[property].kindOf(SC.ManyAttribute) || sourceRecord[property].kindOf(SC.ChildrenAttribute))
             propertyInfo.many.apply(sourceRecord, [property, propertyValue, parentClonedRecord]).forEach(function(clonedItem) {
                 clonedChildItems.push(clonedItem);
             }, this);
         else {
             var clonedItem = propertyInfo.one.apply(sourceRecord, [property, propertyValue, parentClonedRecord]);
             clonedChildItems.push(clonedItem);
         }
     }
 });
