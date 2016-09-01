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

sc_require('controllers/table/table_controllers');
/***
 * Base class for presenting Features and Aggregates of Features
 */
Footprint.FeatureTableController = Footprint.TableController.extend({

    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.content'),

    // Track the active layer selection so we know when the LayerSelection is loading
    // Get the max status of the active and edit controller. That way we know if the active
    // one is loading from the server and we know if the edit one is dirty or saving
    activeLayerSelectionStatus: null,
    // TODO this should be bound outside the class
    activeLayerSelectionStatusBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.status'),
    editLayerSelectionStatus: null,
    editLayerSelectionStatusBinding: SC.Binding.oneWay('*layerSelection.status'),
    layerSelectionStatus: function() {
        return Math.max(this.get('activeLayerSelectionStatus') || 0, this.get('editLayerSelectionStatus') || 0);
    }.property('activeLayerSelectionStatus', 'editLayerSelectionStatus').cacheable(),

    /***
     * The fields of the query result
     */
    resultFields: null,

    /***,
     * Mapping of field names to table columns titles
     */
    resultFieldsTitleLookup: null,

    // Creates a mapping for non-primitive attributes
    // The mapping will map attribute foo to attribute __labels.foo
    // The Feature record will always supply a __labels version for any non-primitive attribute
    mapProperties: function() {
        return mapToSCObject(
            this.get('resultFields') || [],
            function(field) {
                return [
                    field,
                    '__labels.%@'.fmt(field)
                ];
            }
        );
    }.property('resultFields').cacheable()

});

/***
 * Regulates the non-summary Feature table. Because the Footprint.featuresActiveController
 * uses a SparseArray, we must make sure that requests for certain indexes result in an
 * identical request to the featuresActiveController so that it requests those features from the database
 */
Footprint.featureTableController = Footprint.FeatureTableController.create({
    contentBinding: SC.Binding.oneWay('Footprint.featuresActiveController.content'),
    recordTypeBinding: SC.Binding.oneWay('Footprint.featuresActiveController.recordType'),
    editContentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),
    allowsMultipleSelection: YES,
    selectAll: NO,

    selectionBinding: SC.Binding.from('Footprint.featuresActiveController.selection'),
    // This status is not the same as content.status. It's a special status
    // we've added to track the SparseArray loading.
    // The status needs to update immediately so we use an observer instead of a binding
    status: SC.Record.EMPTY,
    statusObserver: function() {
        this.set('status', Footprint.featuresActiveController.get('status') || SC.Record.EMPTY);
    }.observes('Footprint.featuresActiveController.status'),

    // Tell the state chart when the number of sparse array items change
    loadedCountObserver: function() {
        // Invoke later so formattedContent is done updating
        this.invokeLater(function() {
            Footprint.statechart.sendEvent('featuresSparseArrayDidLoadMore');
        });
    }.observes('.loadedCount'),

    resultFieldsBinding: SC.Binding.oneWay('*layerSelection.result_map.result_fields'),
    resultFieldsTitleLookupBinding: SC.Binding.oneWay('*layerSelection.result_map.title_lookup')
});

/***
 * Stores features summary info. There is one instance per group-by combination
 * These records currently comes from the LayerSelection object.
 */
Footprint.featureAggregatesTableController = Footprint.FeatureTableController.create({
    contentBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.summary_results'),
    statusObserver: function() {
        this.set('status', Footprint.featuresActiveController.get('status') || SC.Record.EMPTY);
    }.observes('Footprint.layerSelectionActiveController.status'),

    resultFieldsBinding: SC.Binding.oneWay('*layerSelection.summary_fields'),
    resultFieldsTitleLookupBinding: SC.Binding.oneWay('*layerSelection.summary_field_title_lookup')
});
