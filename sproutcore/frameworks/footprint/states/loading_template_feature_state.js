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

/**
*
* Loads a template version of a Feature class instance in order to get meta data about available fields
*/
Footprint.LoadingTemplateFeatureState = Footprint.LoadingState.extend({
    didLoadEvent:'didLoadTemplateFeatures',
    didFailEvent:'templateFeatureDidFail',
    setLoadingControllerDirectly: YES,
    recordType: Footprint.TemplateFeature,

    /***
     * records that have of TemplateFeature to load. These are DbEntities
     * by default but could also be FileDataset
     * @param context. An SC.Observable whose content contains DbEntities
     * @returns {*}
     */
    records: function(context) {
        var store = Footprint.store; // Need the unnested store
        return arrayIfSingular(context.get('content')).map(function(instance) {
            return store.find(instance.constructor, instance.get('id'));
        });
    },

    /***
     * Queries for TemplateFeatures that are already in the store.
     * @param records
     * @returns {{conditions: string, records: *}}
     */
    localQueryDict: function(records) {
        return {
            conditions: '{records} CONTAINS db_entity',
            records: records
        }
    },

    /***
     * The parameters to fetch one TemplateFeature
     * @param record
     * @returns
     */
    remoteQueryDict: function(record) {
        return {db_entity__id: record.get('id')}
    },

    /***
     * Returns the records whose TemplateFeatures aren't yet loaded
     * @param records
     * @param localTemplateFeatures
     * @returns {*}
     */
    nonLocalRecords: function(records, localTemplateFeatures) {
        return records.filter(function(dbEntity) {
            return !localTemplateFeatures.mapProperty('db_entity').contains(dbEntity)
        })
    },

    /***
     * Fetch the TemplateFeature from the store or remotely.
     * By default we get the TemplateFeatures of the DbEntities in context.content
     * But instead we can use FileSources to get TemplateFeatures
     * of newly uploaded Feature tables (See Footprint.LoadingNewTemplateFeatureState)
     */
    recordArray: function(context) {
        var store = Footprint.store;

        // Get the main store version of each DbEntity or FileDataset.
        // We want to search for existing TemplateFeatures in the main store
        var records = this.records(context);

        // Look in the store first.
        var localTemplateFeatures = store.find(SC.Query.create(
            merge({
                recordType: Footprint.TemplateFeature,
                location: SC.Query.LOCAL
            }, this.localQueryDict(records)))
        );

        if (localTemplateFeatures.get('length') == records.get('length')) {
            return context.get('content').isEnumerable ?
                [localTemplateFeatures] : // array of queries to match the remote case
                localTemplateFeatures;
        }
        else {
            // If we haven't fetched any of the template features yet, get them now
            var ret = this.nonLocalRecords(records, localTemplateFeatures).map(function(record) {
                return Footprint.store.find(SC.Query.create({
                    recordType: Footprint.TemplateFeature,
                    location: SC.Query.REMOTE,
                    parameters:  this.remoteQueryDict(record)
                }));
            }, this);
            // If we have multiple results return them all and we'll check individual query statuses
            // using checkRecordStatuses==YES, otherwise just return the single query result
            return context.get('content').isEnumerable ?
                ret:
                ret.get('firstObject')
        }
    },

    /***
     * On successful got to the templateFeatureIsReadyState
     */
    didLoadTemplateFeatures: function() {
        this.gotoState('templateFeatureIsReadyState', this._context);
        return YES;
    },

    /***
     * Hang out here after the template Feature loads. We don't want to restart DbEntitiesAreReadyState
     */
    templateFeatureIsReadyState: SC.State
});
