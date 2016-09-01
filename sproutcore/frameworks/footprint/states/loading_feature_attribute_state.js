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

/***
 * Loads a Footprint.FeatureAttribute subclass instance based on the context's
 * Footprint.DbEntity and an attribute of the DbEntity's Feature class
 */
Footprint.LoadingFeatureAttributeState = Footprint.LoadingState.extend({
    didLoadEvent:'didLoadFeatureAttribute',
    didFailEvent:'FeatureAttributeDidFail',
    symbologyType: null,
    setLoadingControllerDirectly: YES,
    clearLoadingControllerContentOnEnter: YES,
    /***
     * Set to YES to attach the loading controller to the remote query. This is useful in that
     * it will update the controller's status to BUSY
     */
   recordArray: function (context) {
        // Look in the store first.
        var store = this.getPath('statechart.store');
        var recordType = context && context.get('recordType') || this.get('recordType');
        var localFeatureAttributes = store.find(SC.Query.create({
            recordType: recordType,
            location: SC.Query.LOCAL,
            conditions: 'db_entity = {db_entity} AND attribute = {attribute}',
            db_entity: context.get('db_entity'),
            attribute: context.get('attribute')
        }));

        if (localFeatureAttributes.get('length') == 1) {
            return [localFeatureAttributes]; // array to match remote case
        }
        return store.find(SC.Query.create({
                recordType: recordType,
                location: SC.Query.REMOTE,
                parameters: {
                    // We use the edit version of the controller since the active DbEntity is pegged
                    // to the main selected layer. We want the DbEntity of the data manager
                    db_entity__id: context.getPath('db_entity.id'),
                    attribute: context.get('attribute')
                }
            })
        );
    },

    resolveRecordType: function() {
        if (this.get('symbologyType')) {
            return this.get('symbologyType') === 'categorical' ? Footprint.FeatureCategoryAttribute : Footprint.FeatureQuantitativeAttribute
        }
    },

    /***
     * On successful go back to the layersAreReadyState
     */
    didLoadFeatureAttribute: function(context) {

        var recordType = this.resolveRecordType();

        if (recordType == Footprint.FeatureCategoryAttribute) {
            this.get('statechart').sendAction('configureCategoricalStyleAttributes', context);
        }
        else if (recordType == Footprint.FeatureQuantitativeAttribute) {
            this.get('statechart').sendAction('configureQuantitativeStyleAttributes', context);
        }
    }
});
