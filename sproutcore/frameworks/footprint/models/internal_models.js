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

// Internal and not instantiated
Footprint.QueryStringDictionary = Footprint.Record.extend({
    filter_string: SC.Record.attr(String),
    aggregates_string: SC.Record.attr(String),
    group_by_string: SC.Record.attr(String)
});
SC.RecordAttribute.registerTransform(Footprint.QueryStringDictionary, {
    to: function(obj, attr, recordType, parentRecord) {
        return SC.Object.create(obj || {});
    },
    from: function(obj) {
        return obj ?
            mapToObject(
                Footprint.QueryStringDictionary.allRecordAttributeProperties(),
                // Make sure the values are not empty strings
                function(prop) { return [prop, !!obj.get(prop) ? obj.get(prop) : null] },
                this) :
            {};
    },
    observesChildren: Footprint.QueryStringDictionary.allRecordAttributeProperties()
});

Footprint.SelectionOptions = Footprint.Record.extend({
    // Indicates whether or not the server-side query should be constrained to the current bounds
    constrain_to_bounds: SC.Record.attr(Boolean),
    constrain_to_query: SC.Record.attr(Boolean)
});
SC.RecordAttribute.registerTransform(Footprint.SelectionOptions, {
    to: function(obj, attr, recordType, parentRecord) {
        return SC.Object.create(obj || {});
    },
    from: function(obj) {
        return obj ? filterKeys(obj, Footprint.SelectionOptions.allRecordAttributeProperties(), 'object') : {};
    },
    observesChildren: Footprint.SelectionOptions.allRecordAttributeProperties()
});

// Internal and not instantiated
Footprint.BoundsDictionary = Footprint.Record.extend({
    coordinates: SC.Record.attr(Array),
    type: SC.Record.attr(String)
});

SC.RecordAttribute.registerTransform(Footprint.BoundsDictionary, {
    to: function(obj, attr, recordType, parentRecord) {
        return SC.Object.create(obj || {});
    },
    from: function(obj) {
        return obj ? filterKeys(obj, Footprint.BoundsDictionary.allRecordAttributeProperties(), 'object') : {};
    },
    observesChildren: Footprint.BoundsDictionary.allRecordAttributeProperties()
});

// Internal, not instantiated
Footprint.GenericObjects = Footprint.Record.extend();
SC.RecordAttribute.registerTransform(Footprint.GenericObjects, {
    to: function(obj, attr, recordType, parentRecord) {
        return (obj || []).map(function(item) { return SC.Object.create(item || {})});
    },
    from: function(obj) {
        // I'm not sure how to extract the original object out of the SC.Object.
        return (obj || []).map(function(item) { return item; });
    },
    observesChildren: Footprint.BoundsDictionary.allRecordAttributeProperties()
});

Footprint.ResultMap = Footprint.Record.extend({
    result_fields: SC.Record.attr(Array)
});
SC.RecordAttribute.registerTransform(Footprint.ResultMap, {
    to: function(obj, attr, recordType, parentRecord) {
        return SC.Object.create(obj || {});
    },
    from: function(obj) {
        return obj ? filterKeys(obj, Footprint.ResultMap.allRecordAttributeProperties(), 'object') : {};
    },
    observesChildren: Footprint.ResultMap.allRecordAttributeProperties()
});

Footprint.SchemaDictionary = Footprint.Record.extend({
});
/***
 * Represents a schema for a certain field of a model field. Schemas are produced by Tastypie and delivered
 * in template classes such as FeatureTemplate
 */
Footprint.Schema = Footprint.Record.extend({
    // For SC's sake, this will be set to the parentRecord unique_id, that of the TemplateFeature
    primary_key: 'unique_id',

    field: SC.Record.attr(String),
    // Whether the value can be blank or not
    blank: SC.Record.attr(Boolean),
    // Optional. The default value of the field.
    'default': SC.Record.attr(String),
    // Optional. Description of the field
    help_text: SC.Record.attr(String),
    // Whether or not the field can be null
    nullable: SC.Record.attr(Boolean),
    // Whether or not the field is readonly
    readonly: SC.Record.attr(Boolean),
    // The type, e.g. string, integer, etc
    type: SC.Record.attr(String),
    // The field type if the field is a toOne or toMany
    related_type: SC.Record.attr(String),
    // Whether or not the values are unique
    unique: SC.Record.attr(Boolean)
});


/***
 * Schemas come in as a dict keyed by the field name and valued by the
 * field's Schema. Transform that to an array of schemas with the field
 * name embedded in Footprint.Schema
 */
SC.RecordAttribute.registerTransform(Footprint.SchemaDictionary, {
    /***
     * Converts the raw data to the record
     * @param obj
     * @param attr
     * @param recordType
     * @param parentRecord
     * @returns {*}
     */
    to: function(obj, attr, recordType, parentRecord) {
        return obj ?
            mapObjectToList(
                obj,
                function(field, schema) {
                    return parentRecord.get('store').createRecord(
                        Footprint.Schema,
                        $.extend({
                            unique_id: parentRecord.get('unique_id'),
                            field: field
                        }, schema)
                    );
                }
            ):
            [];
    },
    /***
     * Converts the record back to rawness
     * @param list
     * @returns {*}
     */
    from: function(list) {
        return mapToSCObject(list, function(schema) {
            return [schema.get('field'), removeKeys(schema.get('attributes'), ['field'])];
        });
    },
    observesChildren: []
});
