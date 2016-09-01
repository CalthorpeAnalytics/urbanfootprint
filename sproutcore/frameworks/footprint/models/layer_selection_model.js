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


sc_require('models/internal_models');

/***
 * Represents the sub selection of a Footprint.Layer (which is currently modeled as Footprint.PresentationMedium)
 * instance's Feature instances.
 * @type {*}
 */
Footprint.LayerSelection = Footprint.Record.extend(Footprint.Name, {

    // We can't track attribute changes because query_strings
    disable_attribute_change_tracking: YES,
    // The unique id for the record is its combination of user id and layer id
    primaryKey: 'unique_id',
    // This is the Django id. We need to send this id back to the server when saving
    id: SC.Record.attr(Number),

    layer:SC.Record.toOne("Footprint.Layer", {
        isMaster:YES,
        key: 'selection_layer'
    }),

    user:SC.Record.toOne("Footprint.User", {
        isMaster:YES
    }),

    // These are generic features. We only use them in conjunction with the layer to resolve the full Feature.
    features_count: SC.Record.attr(Number),
    // The result fields of the query
    result_map: SC.Record.attr('Footprint.ResultMap', {nested:YES}),
    // The summary results, and array of dicts that the API converts to SC.Objects on load
    summary_results: SC.Record.toMany('Footprint.GenericObjects', {nested:YES}),
    // The summary fields of the summary query
    summary_fields: SC.Record.attr(Array),
    // The pretty version of those fields to display as column titles
    // TODO how do I model these?
    //summary_field_title_lookup: SC.Record.attr(Object),
    // Bounds are set to a geojson geometry to update the selection
    // BoundsDictionary is just a marker used to transform the json to an SC.Object
    bounds:SC.Record.attr('Footprint.BoundsDictionary', {nested:YES}),

    boundsAsString: function() {
        // This does lat,lon | lat,lon rounded to four digits.
        // Assumes a single polygon in multi-polygons, hence the firstObject.firstObject
        lonLats = this.getPath('bounds.coordinates.firstObject.firstObject');
        return lonLats ? lonLats.map(
            function(lonLat) {
                return lonLat.map(function(l) {return SC.Math.round(l,4)}).join(',');
            }).join('|') : null;
    }.property('bounds').cacheable(),
    // Options for selecting, including booleans 'constrain_to_bounds' and 'constrain_to_query'
    selection_options: SC.Record.attr('Footprint.SelectionOptions', {nested:YES}),
    // A dictionary of the raw query strings
    // This includes 'filter_string', 'aggregates_string', and 'group_by_string'
    // QueryStringDictionary is just a marker used to transform the json to an SC.Object
    query_strings: SC.Record.attr('Footprint.QueryStringDictionary', {nested:YES}),
    // Holds the parsed filter token tree
    filter:SC.Record.attr(Object),
    // Holds the list of join DbEntityKeys
    joins:SC.Record.attr(Array),
    // Holds the list of aggregate token trees
    aggregates:SC.Record.attr(Object),
    // Holds the list of group by terms as parsed token tress
    group_bys:SC.Record.attr(Object),
    // The extent of the currently selection features
    selection_extent:SC.Record.attr('Footprint.BoundsDictionary', {nested:YES}),

    // Defines an undo manager for the Feature records of the label. This allows a separate undoManager per layer
    featureUndoManager:null,
    // Defines an undo manager for this instance
    undoManager: null,

    destroy:function() {
        sc_super();
        if (this.get('featureUndoManager'))
            this.get('featureUndoManager').destroy();
    },

    /***
     * Restore the user generated attributes
     * @param attributes: object of raw attributes
     */
    restore: function(attributes) {
        ['query_strings', 'joins'].map(function(attr) {
            this.set(attr, attributes[attr]);
        }, this);
    }
});

Footprint.LayerSelection.mixin({
    processDataHash: function(dataHash, record) {
        // Strip out the the features. We never want to send these.
        dataHash = $.extend({}, dataHash);
        delete dataHash.features;
        delete dataHash.summary_results;
        delete dataHash.summary_fields;
        delete dataHash.query_sql;
        delete dataHash.summary_query_sql;

        dataHash.query_strings = {};
        dataHash.query_strings.filter_string = record.getPath("query_strings.filter_string");
        dataHash.query_strings.aggregates_string = record.getPath("query_strings.aggregates_string");
        dataHash.query_strings.group_by_string = record.getPath("query_strings.group_by_string");
        return dataHash;
    }
});
