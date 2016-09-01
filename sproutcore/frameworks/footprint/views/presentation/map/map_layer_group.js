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
 * A configuration of the leaflet layer for a particular Footprint.Layer instance
 * @type {*}
 */
Footprint.MapLayerGroup = SC.Object.extend({
    /**
     * Required. The Footprint.LayerAttribute instance upon with this MapLayerGroup is based
     */
    layerAttribute: null,


    /***
     * The vector map layer
     */
    vector: null,

    /***
     * The raster map layer
     */
    rasterLayer: null,

    /***
     * The Leaflet FeatureGroup instance
     */
    _featureGroup: null,

    createFromLayerAttribute: function(layerAttribute) {
        throw 'Must implement in subclass';
    },

    /***
     * Adds this group's map layers to the map.
     */
    addLayersToMap: function(map) {
        this._featureGroup = L.featureGroup([this.get('rasterLayer')]);
        this._featureGroup.addTo(map);
    },

    /***
     * Removes this group's map layers from the map.
     */
    removeLayersFromMap: function(map) {
        var activePaintTool = Footprint.mapToolsController.get('activePaintTool');
        if (activePaintTool) {
            var drawingFeatureGroup = activePaintTool.getPath('mapTools.selectionFeatureGroup');
            drawingFeatureGroup.clearLayers();
        }

        Footprint.mapToolsController.clearActiveTool();

        map.removeLayer(this._featureGroup);
    },

    /***
     * Sets visibility of each mapLayerGroupLayer based on overall visibility and zoom level. If
     * zoom is below the threshold, we use the raster layer; otherwise, we use the vector layer.
     */
    setVisibilityBasedOnZoom: function(map) {
        var layer = this.get('rasterLayer');
        if (layer && !this._featureGroup.hasLayer(layer)) {
            this._featureGroup.addLayer(layer);
        }
    },
});
SC.mixin(Footprint.MapLayerGroup, {
    /**
     * Indicates which other subclasses the subclass invalidates when the latter's layers need to be rerendered.
     * For example, if a BackgroundMapLayerGroup needs to invalidate ForegroupMapLayerGroup
     */
    invalidatesLayerTypes: [],
});

/***
 * Represents the map layers of a Footprint.Layer that is a background layer
 * These are all remote raster images, as of now. They can define attributes
 * that are used as parameters of the map provide (e.g. transit and traffic options with Google Maps)
 */
Footprint.BackgroundMapLayerGroup = Footprint.MapLayerGroup.extend({
    init: function() {
        var dbEntity = this.getPath('layerAttribute.layer.db_entity');
        if (dbEntity) {
            this.set('rasterLayer', L.tileLayer(dbEntity.get('url')));
        }
    },
});

SC.mixin(Footprint.BackgroundMapLayerGroup, {
    // Invalidate everything above when we need to redraw any background layers
    invalidatesLayerTypes: ['Footprint.ForegroundMapLayerGroup'],
});

/***
 * Represents the map layers of a Footprint.Layer that is a foreground
 * layer.  This MapLayerGroup contains a map layer for raster images
 * and a map layer for selection vectors. These layers always have at
 * least one styled attribute, the default being 'wkb_geometry' to
 * simply by the geometry of the features
 */
Footprint.ForegroundMapLayerGroup = Footprint.MapLayerGroup.extend({

    /***
     * The user selection layer
     */
    selectionLayer: null,

    init: function() {
        var activeStyle = this.getPath('layerAttribute.activeStyle');
        if (!activeStyle) {
            activeStyle = this.getPath('layerAttribute.layer.medium.style_attributes.firstObject');
        }

        var layerAttribute = this.getPath('layerAttribute');
        if (!layerAttribute) {
            console.trace('Missing layerAttribute in ', this);
        }

        if (layerAttribute) {
            var layerId = layerAttribute.getPath('layer.id');
            var userId = Footprint.userController.getPath('firstObject.id');

            var rasterUrl = createUrl(layerId, activeStyle.get('id'), userId, 'raster');
            var selectionUrl = createUrl(layerId, activeStyle.get('id'), userId, 'selection');

            this.set('rasterLayer', this._createRasterLayer(rasterUrl));
            this.set('selectionLayer', this._createSelectionLayer(selectionUrl));
        }
    },

    _createRasterLayer: function (rasterUrl) {
        return L.tileLayer(rasterUrl, { random: Math.random() });
    },

    // It is possible for a single mouse down event to hit multiple layers. Leaflet doesn't have an easy
    // way to get a single 'click' event and get all the layers in one go, so instead we accumulate them in
    // this._clickedFeatures and then call _accumulatedClick when all the clicks are done.
    // TODO: generalize accumulated/debounced event handling into sproutcore_utils.js
    _layerClickTimer: null,
    _clickedFeatures: null,
    _accumulatedClick: function() {
        // This fires when all the outstanding layer clicks are done.
        var featureInfos = this._clickedFeatureInfos;
        this._layerClickTimer = null;
        this._clickedFeatures = null;

        // TODO: Support all clicked features.
        var newPaneLayout = featureInfos[0].layout;
        var feature = featureInfos[0].feature;


        Footprint.featurePopupTableController.setPath('featureTablePopupPane.layout', newPaneLayout);
        var featureId = feature.properties['id'];
        Footprint.featurePopupTableController.set('featureTablePopupId', featureId);
        Footprint.featurePopupTableController.get('featureTablePopupPane').append();
    },
    _createSelectionLayer: function (selectionUrl) {

        var layer = new L.TileLayer.GeoJSON(selectionUrl, {
            transparent: true,
            clipTiles: true,
            tileSize: 8192,  // setting this arbitrarily large so leaflet handles the entire map as one tile
            unique: function (feature) {
                return feature.id;
            },
        }, {
            style: this.constructor.selectionStyle,
            // Called each time a new layer is created for a feature in the GeoJSON.
            onEachFeature: function (feature, layer) {
                if (!(layer instanceof L.Point)) {
                    layer.on('click', Footprint.nativeEventHandler(function () {
                        if (Footprint.mapToolsController.get('activeToolKey') != 'identify') {
                            return;
                        }

                        // TODO generalize this (see comment above for _accumulatedClick)
                        if (!this._layerClickTimer) {
                            this._clickedFeatureInfos = [];
                            this._layerClickTimer = SC.Timer.schedule({
                                action: this._accumulatedClick.bind(this),
                                interval: 100,
                            });
                        }
                        this._clickedFeatureInfos.push({
                            feature: feature,
                            layout: {
                                top: L.DomEvent._getEvent().clientY - 40,
                                left: L.DomEvent._getEvent().clientX + 100,
                                width: 400,
                                height: 500,
                            },
                        });
                    }.bind(this)));
                    // The hover over styling
                    layer.on('mouseover', Footprint.nativeEventHandler(function () {
                        layer.setStyle(this.constructor.hoverStyle);
                    }, this));
                    layer.on('mouseout', Footprint.nativeEventHandler(function () {
                        layer.setStyle(this.constructor.selectionStyle);
                    }, this));
                }
            }.bind(this),
        });
        var tileLoaded = layer._tileLoaded;
        layer._tileLoaded = function(tile, tilePoint) {
            tileLoaded.call(layer, tile, tilePoint);
            // Just call once per runloop
            Footprint.mapController.invokeOnce('tileDidLoad');
        };
        return layer;
    },

    showSelection: function() {
        this._featureGroup.addLayer(this.selectionLayer);
        // this will re-request selection tiles from TileStache
        this.selectionLayer.redraw();
    },

    hideSelection: function() {
        this._featureGroup.removeLayer(this.selectionLayer);
    },

});

function createUrl (layer_id, attr_id, user_id, type) {
    if (type == 'raster') {
        return '//%@/tiles/layer:%@,attr_id:%@,type:%@/{z}/{x}/{y}.png?%@'.fmt(
            [window.location.hostname, window.location.port].compact().join(':'),
            layer_id,
            attr_id,
            type,
            Math.random()
        );
    } else if (type == 'selection') {
        return '//%@/footprint/vectors/layer:%@,attr_id:%@,type:%@.geojson?user_id=%@'.fmt(
            [window.location.hostname, window.location.port].compact().join(':'),
            layer_id,
            attr_id,
            type,
            user_id
        );
    }
}

SC.mixin(Footprint.ForegroundMapLayerGroup, {
    /**
     * Indicates which other subclasses the subclass invalidates when the latter's layers need to be rerendered.
     * For example, if a BackgroundMapLayerGroup needs to invalidate ForegroupMapLayerGroup
     */
    invalidatesLayerTypes: [],

    // The style of Leaflet vectors of the selection set
    selectionStyle: {
        clickable: true,
        color: 'cyan',
        weight: 4.0,
        opacity: 0.8,
        fillOpacity: 0,
    },
    // The style of Leaflet vectors when hovered over
    hoverStyle:  {
        color: 'yellow',
        weight: 5,
    },
    // The style give the vectors when one or more are selected in the Feature table
    tableSelectionStyle:  {
        color: '#FB05FF',
        weight: 5,
    }
});
