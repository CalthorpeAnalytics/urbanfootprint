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

Footprint.Feature = Footprint.Record.extend({
    // The unique id for the record is its combination of DbEntity id and id
    primaryKey: 'the_unique_id',
    geometry: SC.Record.attr(Object),
    created: SC.Record.attr(SC.DateTime),
    updated: SC.Record.attr(SC.DateTime),
    config_entity: SC.Record.toOne(Footprint.ConfigEntity),
    db_entity: SC.Record.toOne(Footprint.DbEntity),
    // The non-unique id globally, but unique to the Feature table
    id: SC.Record.attr(Number),
    approval_status: SC.Record.attr(String)
});

Footprint.Feature.mixin({

    /***
     * As far as the API is concerned, all Feature subclasses should be updated and fetched as plain Feature classes
     * A layer__id parameter will always accompany them to clarify their type to the server
     * @returns {*|RangeObserver|Class|void|Feature}
     */
    apiRecordType: function() {
        return Footprint.Feature;
    },

    infoPane: function() {
        return 'Footprint.FeatureInfoPane';
    }
});

// TODO Remove All Feature subclasses. This information should come from
// Tastypie's /schema call, which returns all the details we need
// about the subclass to construct a Sproutcore class

Footprint.CensusTract = Footprint.Feature.extend({
    tract: SC.Record.attr(Number)
});

Footprint.CensusBlockgroup = Footprint.Feature.extend({
    blockgroup: SC.Record.attr(Number),
    census_tract: SC.Record.toOne("Footprint.CensusTract", {
        isMaster: YES,
        nested: YES
    })
});

Footprint.CensusBlock = Footprint.Feature.extend({
    block: SC.Record.attr(Number),
    census_blockgroup: SC.Record.toOne("Footprint.CensusBlockgroup", {
        isMaster: YES,
        nested: YES
    })
});

Footprint.Geography = Footprint.Record.extend({
    source_id: SC.Record.attr(Number)
});

Footprint.FeatureVersion = Footprint.Record.extend({
    // Tell the datasource to pass the id as a param, not as a path
    _id_as_param:  YES
});

/***
 * Used to load the template Feature for a DbEntity. The distinct class lets the API resolve the url to template_feature
 */
Footprint.TemplateFeature = Footprint.Feature.extend({
    /**
     * A dictionary of Footprint.Schema instances, keyed by field name
     */
    schemas: SC.Record.attr('Footprint.SchemaDictionary', { nested: true }),
    /**
     * When a TemplateFeature represents a newly uploaded feature table, rather
     * than existing DbEntity, it has a FileDataset, which contains the id
     * of the uploaded file. Progress reports aren't modeled on the server. They
     * are based on UploadDatasetTasks though, so we can use the upload id to resolve
     * the uploaded file on the server.
     */
    file_dataset: SC.Record.toOne('Footprint.FileDataset', { nested: true })
});

/***
 * Used to load the template Feature for a DbEntity. The distinct class lets the API resolve the url to feature_attribute
 */
Footprint.FeatureCategoryAttribute = Footprint.Feature.extend({
    minimum: SC.Record.attr(Number),
    maximum: SC.Record.attr(Number),
    unique_values: SC.Record.attr(Array)
});

Footprint.FeatureQuantitativeAttribute = Footprint.Feature.extend({
    minimum: SC.Record.attr(Number),
    maximum: SC.Record.attr(Number),
    unique_values: SC.Record.attr(Array)
});

Footprint.FeatureCategoryAttribute.mixin({
    /***
     * Override the Feature class
     * @returns {*}
     */
    apiRecordType: function() {
        return Footprint.FeatureCategoryAttribute;
    }
});

Footprint.FeatureQuantitativeAttribute.mixin({
    /***
     * Override the Feature class
     * @returns {*}
     */
    apiRecordType: function() {
        return Footprint.FeatureQuantitativeAttribute;
    }
});

Footprint.TemplateFeature.mixin({
    /***
     * Override the Feature class
     * @returns {*}
     */
    apiRecordType: function() {
        return Footprint.TemplateFeature;
    }
});
