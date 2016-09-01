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
  * A lightweight controller for basic map functionality.
  * @type {Class}
  */
Footprint.mapController = SC.ObjectController.create({

    // The leaflet map object.
    content:null,

    // The leaflet compass object. This must be removed and reappended any time layers
    // are added to the map.
    compass: null,

    layerSelection: null,
    layerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.content'),
    layerSelectionExtent: null,
    layerSelectionExtentBinding: SC.Binding.oneWay('*layerSelection.selection_extent'),
    layerSelectionCoordinates: null,
    layerSelectionCoordinatesBinding: SC.Binding.oneWay('*layerSelectionExtent.coordinates'),
    // TODO new to Leaflet functionality. Couldn't get working with Polymaps
    highlightedFeatures: null,
    highlightedFeaturesBinding: SC.Binding.oneWay('Footprint.featuresActiveController.selection'),
    /***
     * The Footprint.LayerSelection instance of the content which is active
     */
    activeLayerSelection: null,
    activeLayerSelectionBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.content'),

    /***
     * The Footprint.ActiveLayerGroup instance (not an SC.Record) that groups the raster, vector, layer selection
     * vector, etc) together
     */
    activeLayerGroup: null,
    activeLayerGroupBinding: SC.Binding.oneWay('Footprint.mapLayerGroupsController.activeLayerGroup'),

    /***
     * The paint tool currently in use by ther user
     */
    activePaintTool: null,
    activePaintToolBinding: SC.Binding.oneWay('Footprint.mapToolsController.activeSelectorTool'),


    resetExtentToSelection: function () {
        this.setMapExtent(this.get('layerSelectionBounds'));
    },


    exportMapToImage: function () {
        var curMap = this.get('content');
        var dimensions = curMap.getSize();
        // there's a bug with leaflet-image markers in SC/UF that causes error
        // so suspend drawing before generating map
        var activeToolKey = Footprint.mapToolsController.get('activeToolKey');
        Footprint.mapToolsController.selectToolByKey('doExportMap');

        SC.AlertPane.info({
            message: 'Map Export in Progress',
            description: 'The current map is being exported as a jpg and will be downloaded to your browser momentarily.'
        });

        //document.getElementById(curMap._container.id).style.cursor = "wait";
        leafletImage(curMap, this._doImageDownload);

        // Restore
        Footprint.mapToolsController.selectToolByKey(activeToolKey);
    },

    _doImageDownload: function (err, canvas) {
        // var dataURL = canvas.toDataURL('image/png');
        //document.getElementById(this.get('content')._container.id).style.cursor = "";
        var dataURL = canvas.toDataURL('image/jpeg',0.5);
        var tmpAElement = document.createElement('A');
        tmpAElement.href = dataURL;

        // make nice date time stamp string for file saving
        var d = new Date();
        var dstr = d.toDateString().substr(4).replace(/ /g, '_');
        var tstr = d.toTimeString().substr(0, 8).replace(/:/g, '_');
        var dtStamp = dstr + '_' + tstr;

        tmpAElement.download = 'UF_Map_' + dtStamp + '.jpg';
        tmpAElement.click();
    },

    /***
     * TODO new to Leaflet. See above
     * Returns the highlighted features current extent.
     */
    highlightedFeaturesBounds: function() {
        if (this.get('layerSelection'))
            // Get tiles of the current zoom level
            return $.flatMap(this.get('highlightedFeatures'), function(highlightedFeature) {
                return this._polygonBoundingBox(this.mapLayerFeature(highlightedFeature).data.geometry);
            });
    }.property('.highlightedFeatures').cacheable(),


    /***
     * Sets the extent of the map
     * @param extent
     */
    setMapExtent: function(extent) {
        var latLngBounds = L.latLngBounds(extent);
        this.get('content').fitBounds(latLngBounds);
    },

    /***
     * Reset the extent to that of the active Project
    */
    resetExtentToProject: function(){
        this.setMapExtent(this.get('projectExtent'));
    },

    // Statechart call this to force reset of highlighted features
    resetExtentToHighlightedFeatures: function(){
        this.setMapExtent(this.get('highlightedFeaturesBounds'));
    },

    mapLayersNeedZoomUpdate:NO,
    refreshMapLayerZoomVisibility: function() {
        this.set('mapLayersNeedZoomUpdate', YES);
    },

    // Indicates that the map can be created
    readyToCreateMap: NO,
    // Indicates that map layers are ready for creation
    readyToCreateMapLayers:NO,

    isReady:function() {
        return this.get('readyToCreateMap') && this.get('readyToCreateMapLayers');
    }.property('readyToCreateMap', 'readyToCreateMapLayers').cacheable(),

    /***
     * Sets the center of the map
     * @param lat_lon_dict
    */
    center: function(lat_lon_dict) {
        //this.get('map').center(lat_lon_dict);
    },

    /***
     * The zoom range of the map
     */
    mapZoomRange: function() {
        return [8, 18];
    }.property().cacheable(),

    /***
     * The initial zoom level of the map
     * TODO this should be based on the content bounds in the future
     */
    mapInitialZoom: function() {
        return 16;
    }.property().cacheable(),

    project: null,
    // Needs default null so that it is never undefined, which messes up the binding
    projectBinding: SC.Binding.oneWay('Footprint.projectActiveController.content').defaultValue(null),

    // projectBounds will probably never change independent of the project, but just in case
    projectBounds: null,
    projectBoundsBinding: SC.Binding.oneWay('*project.bounds'),
    projectExtent: function() {
        if (this.get('project'))
            return this._polygonBoundingBox(this.getPath('projectBounds'));
    }.property('projectBounds').cacheable(),

    /***
     * Returns the layerSelection's current extent. This is a single polygon.
     */
    layerSelectionBounds: function() {
        if (this.get('layerSelection'))
            return this._polygonBoundingBox(this.get('layerSelectionExtent'));
    }.property('layerSelectionCoordinates').cacheable(),

    // TODO unused
    _polygonCenter: function(coordinates) {
        var pairs = [];
        for (var i=0; i<coordinates.length-2; i+=2) { // -2 to skip redundant polygon point
            pairs.push({lon:coordinates[i], lat:coordinates[i+1]})    ;
        }
        var avgLat = $.accumulate(pairs, function(pair, previous) { return pair.lat + previous;})/pairs.length;
        var avgLon = $.accumulate(pairs, function(pair, previous) { return pair.lon + previous;})/pairs.length;
        return {lat:avgLat, lon:avgLon};
    },

    /***
     * Finds the bounding box for all the shapes in the given bounds
     * @param bounds GeoJson-formatted SC.Object with a type property, which is either 'polygon' or 'multipolygon', and
     *  a coordinates property, which is a single item array containing an array of points for 'polygon',
     *  or a multiple item array containing multiple arrays of points for 'multipolygon'.
     * @returns {Array}
     * @private
     */
    _polygonBoundingBox: function(bounds) {
        var coordinatesSets = null;
        switch(bounds.get('type')) {
        case 'Polygon':
            coordinatesSets = bounds.get('coordinates');
            break;
        case 'MultiPolygon':
            coordinatesSets = bounds.getPath('coordinates.firstObject');
            break;
        case 'Point':
            coordinatesSets = [[bounds.getPath('coordinates')]];
            break;
        }
        var longitudes = $.flatMap(coordinatesSets, function(coordinateSet) {
            return coordinateSet.map(function(coordinate) {
                return coordinate[0];
            });
        });
        longitudes.sort(function(a, b) { return a - b; });
        var latitudes = $.flatMap(coordinatesSets, function(coordinateSet) {
            return coordinateSet.map(function(coordinate) {
                return coordinate[1];
            });
        });
        latitudes.sort(function(a, b) { return a - b; });

        return [{lat:latitudes[0], lon:longitudes[0]},
            {lat:latitudes[latitudes.length - 1], lon:longitudes[longitudes.length - 1]}];
    },
});

/***
 * A table for the single Feature that the user identifies on the map from the selected
 * Features. If the Feature is in the store (it has been lazily loaded, it displays immediately).
 * Otherwise we send an action to the statechart to immediate load the feature and we show a status
 * overlay whilst we wait
 */
Footprint.featurePopupTableController = Footprint.FeatureTableController.create({
    featureTablePopupPane: null,
    featureTablePopupId: null,
    features: null,
    featuresBinding: SC.Binding.oneWay('Footprint.featuresActiveController.content'),
    editContentBinding: SC.Binding.oneWay('.content'),
    featuresStatus: null,
    featuresStatusBinding: SC.Binding.oneWay('Footprint.featuresActiveController.status'),
    dbEntity: null,
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityActiveController.content'),
    recordTypeBinding: SC.Binding.oneWay('Footprint.featuresActiveController.recordType'),
    allowsMultipleSelection: YES,

    selectionBinding: SC.Binding.from('Footprint.featuresActiveController.selection'),

    resultFieldsBinding: SC.Binding.oneWay('*layerSelection.result_map.result_fields'),
    resultFieldsTitleLookupBinding: SC.Binding.oneWay('*layerSelection.result_map.title_lookup'),

    /***
     * Returns a local query of Footprint.Feature. This will find any feature that
     * is currently in Footprint.featuresActiveController.
     *
     * TODO We currently don't unload Features from previous queries, but we probably
     * should in case the feature's attributes are updated elsewhere. So this could
     * find a Feature that was previously loaded in another selection even if it's not yet
     * in the SparseArray
     */
    selectionObserver: function() {
        if (!this.get('featureTablePopupId') ||
            !(this.get('featuresStatus') & SC.Record.READY)) {

            // Nothing is selected.
            this.set('content', null);
            return;
        }

        // The id we get from leaflet is just the Feature id. The full unique id
        // must include the Features' DbEntity id
        var uniqueId = Footprint.makeEntityFeatureId(
            this.getPath('dbEntity.id'), this.get('featureTablePopupId'));
        // Use a query here instead of the this.features so we maintain an SC.RecordArray result
        // Use the first Feature instance to get the recordType, a subclass of Feature
        // We needs to use BEGINS_WITH because the_unique_id of the feature will be modified for join queries
        // join queries append _(joined_feature_id) for the joined Feature
        var featureRecords = Footprint.store.find(SC.Query.local(
            this.getPath('features.firstObject.constructor'),  {
                conditions: 'the_unique_id BEGINS_WITH {featureId}',
                featureId: uniqueId
            }
        ));

        if (!featureRecords.get('length')) {
            // load up the results from the server. This state knows
            // about will the feature id(s) from
            // Footprint.featurePopupTableController
            Footprint.statechart.sendAction('doLoadPopupFeature');
        } else {
            this.set('content', featureRecords);
        }
    }.observes('featureTablePopupId','features','featuresStatus').cacheable()
});
