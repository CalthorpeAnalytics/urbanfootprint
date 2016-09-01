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


sc_require('controllers/layers/visible_attribute_controllers');
/**
 * Manages the full lifecycle of leaflet layers and the MapLayerGroup objects that hold
 * them. It also optimizes adding and removing layers from the map.
 *
 * A note on division of labor. This controller takes layer and visible-attribute data
 * as its input from the model/controller layers, and outputs MapLayerGroup objects as
 * output for the view layer. MapLayerGroup objects should be considered view objects,
 * and should not be manipulated except internally here and in the MapView itself. (In
 * fact, presently MapLayerGroup manipulation is split up arbitrarily between this object
 * and the map view; this could be consolidated in the view or here in the controller
 * if desired.)
 */
Footprint.mapLayerGroupsController = SC.Object.create({
    // The Leaflet map
    map: null,
    mapBinding: SC.Binding.oneWay('Footprint.mapController.content'),

    /**
     * The Footprint.Layer instance of the content which is active
     */
    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    /***
     * The activeLayerGroup based on the activeLayer.
     * @returns {*}
     */
    activeLayerGroup: function() {
        if (!this.get('activeLayer')) {
            return null;
        }
        var layerKey = this._getLayerKeyForLayer(this.get('activeLayer'));
        if (!layerKey) {
            return null;
        }

        var activeLayerGroup = this._mapLayerGroupCache[layerKey];
        return activeLayerGroup;
    }.property('activeLayer').cacheable(),

    /**
     *
     */
    _getLayerKeyForLayer: function(layer) {
        var active_style_key = layer.get('active_style_key'),
            active_style = null;
        if (active_style_key) {
            active_style = layer.getPath('medium.style_attributes')
                .find(function (style_attribute) {
                    return style_attribute.get('key') == active_style_key;
                });
        }

        if (!active_style) {
            return null;
        }

        return Footprint.LayerAttribute.create({
            activeStyle: active_style,
            layer: layer,
        }).get('key');
    },

    /***
     * Refresh the given Layers after some sort of server update to the data they style or
     * after the layer symbology editor is used to assign a new active_style_key.
     * This refreshes the layer by updating the raster URL. The URL doesn't actually change
     * unless the active_style_key was updated, but it forces a refresh nonetheless.
     * @param layerKeys
     */
    refreshLayers: function(layerKeys) {
        layerKeys.forEach(function(layerKey) {
            var layer = F.layersForegroundController.find(function(layer) {
                return layer.get('dbEntityKey') == layerKey;
            });

            if (!layer) {
                return;
            }

            // Resolve the LayerGroup for the give Layer if it has been created.
            var layerStyleKey = layer.get('active_style_key'),
                uniqueKey = Footprint.generateLayerKey(layer),
                user = Footprint.userController.getPath('content.firstObject.attributes'),
                layerGroupKey = layerStyleKey ? layerStyleKey: uniqueKey,
                layerGroup = this._mapLayerGroupCache[layerGroupKey];

            // If not created, just quit. We might not have show this Layer yet, or it's not in the LayerLibrary
            if (!layerGroup) {
                return;
            }
            var raster = layerGroup.get('rasterLayer');
            if (raster) {
                var url = createUrl(layer.get('id'),
                                    layerGroup.getPath('layerAttribute.activeStyle.id'),
                                    user.id, 'raster');
                raster.setUrl(url);
            }
        }, this);
    },

    // The private MapLayerGroup cache, maps layer keys to LayerGroups
    _mapLayerGroupCache: {},

    // A cached list of visible LayerAttribute keys.
    _visibleMapLayerGroupKeysByType: {
        'Footprint.ForegroundMapLayerGroup':[],
        'Footprint.BackgroundMapLayerGroup':[],
    },

    // background and foreground layers behave diffently. background layers have no MapLayerGroups
    // Order determines rendering order. We want background rendered first and controls last
    _layerTypes: ['Footprint.BackgroundMapLayerGroup', 'Footprint.ForegroundMapLayerGroup'],

    // A cache of the full list of Layers in the current scenario. Used to detect
    // and handle layer deletion.
    _layerKeysByType: {
        'Footprint.BackgroundMapLayerGroup':[],
        'Footprint.ForegroundMapLayerGroup':[],
    },

    /***
     * A lookup of the controller that tracks the current Layers for each layer type
     */
    _layersControllersByType: {
        'Footprint.ForegroundMapLayerGroup': Footprint.layersForegroundController,
        'Footprint.BackgroundMapLayerGroup': Footprint.layersBackgroundController,
    },

    /***
     * A lookup of the controller that contains all current LayerAttribute instances for the MapLayerGroup subclass.
     * A LayerAttribute instance is simply a combination of a Footprint.Layer and one of its visible attributes
     */
    _visibleLayerAttributesControllerByType: {
        'Footprint.ForegroundMapLayerGroup': Footprint.visibleLayerAttributesForegroundController,
        'Footprint.BackgroundMapLayerGroup': Footprint.visibleLayerAttributesBackgroundController,
    },

    /***
     * Iterates through currently-showing background layers and foreground visible attributes. Creates, adds,
     * removes and destroys MapLayerGroups as needed.
     *
     * This is called whenever the layersController's content changes or one of its layers is added, edited,
     * or removed.
     *
     * The particulars of this method's optimizations are informed by the very unfortunate fact that map
     * layers can only be appended at the top of the stack, making simple internal rearranging is impossible.
     */
    updateMapLayerGroups: function() {
        var map = this.get('map');
        // Remove no-longer-needed MapLayerGroups, which might happen if we switch Scenarios, delete a layer, etc.
        // This isn't related to visibility. We deal with that below
        this._layerTypes.forEach(function(layerType) {
            var layersController = this._layersControllersByType[layerType];
            if (layersController)
                // Remove layers not in the current Scenario
                this._exitMapLayerGroups(map, layerType, layersController.mapProperty('db_entity').mapProperty('key'));
        }, this);

        // Cache all of our current visible MapLayerGroups by the MapLayerGroup subclass
        var currentVisibleMapLayerGroupKeysByType = {};
        // Cache all of our current visible MapLayerGroups by the MapLayerGroup subclass
        var currentVisibleLayerAttributesByType = {};

        // With deleted layers taken care of, we move on to compiling the current list of
        // should-be-visible MapLayerGroup keys for each layer type.
        this._layerTypes.forEach(function(layerType) {
            var visibleLayerAttributesController = this._visibleLayerAttributesControllerByType[layerType];
            if (visibleLayerAttributesController) {
                //if there is no content exit and wait for content
                if (!visibleLayerAttributesController.get('content')) {
                    return;
                }
                // Set the current visible LayerAttributes from the controller.
                // We'll use this to enter missing visible MapLayerGroups, and exit ones that are now invisible
                currentVisibleLayerAttributesByType[layerType] = visibleLayerAttributesController.get('content');
                // A list of the corresponding keys, used for comparison to the cache
                currentVisibleMapLayerGroupKeysByType[layerType] = currentVisibleLayerAttributesByType[layerType].mapProperty('key');
            }
        }, this);

        // GATEKEEP: No change in visible keys.
        // If none of the layerTypes have any changes, quit now
        if (this._layerTypes.every(function(layerType) {
            return currentVisibleMapLayerGroupKeysByType[layerType].join() ===
                this._visibleMapLayerGroupKeysByType[layerType].join();
        }, this)) {
            return;
        }

        // Remove no-longer-visible layers and then add visible layers for each layerType
        // We also have to remove all layers that are above any new layer or removed layer
        // Since the layers are drawn from bottom to top, the topmost are invalidated by any change below them.
        // Thus a change in one layerType (e.g. background) invalidates all the layers of the layerTypes above it (e.g. foreground and controls)
        var layerTypeIndices = {};
        var invalidatedLayerTypes = [];
        this._layerTypes.forEach(function (layerType) {
            // Cycle through the layers, removing items until we have the longest-possible matching stack.
            layerTypeIndices[layerType] = this._exitMinimumVisibleMapLayerGroups(
                layerType,
                currentVisibleMapLayerGroupKeysByType);
            // Invalidate all layers of dependent types if anything changed
            if (layerTypeIndices[layerType] < currentVisibleMapLayerGroupKeysByType[layerType].length) {
                this._invalidateDependentLayerTypes(layerType);
                invalidatedLayerTypes.push(SC.objectForPropertyPath(layerType).invalidatesLayerTypes);
            }
        }, this);
        // Enter new MapLayerGroups as well as those invalidated by exit
        // We pass the starting index of the layerType in case not all need to be re-added
        // unless the layerType was invalidated because a layerType that it depends on was changed
        this._layerTypes.forEach(function (layerType) {
            this._enterVisibleMapLayerGroups(
                layerType,
                currentVisibleMapLayerGroupKeysByType,
                currentVisibleLayerAttributesByType,
                layerTypeIndices[layerType]);
        }, this);

        // Update the activeLayerGroup property
        this.propertyDidChange('activeLayerGroup');
        // Done!
    },

    /***
    * Exits MapLayerGroups that are no longer visible
    * @param layerType
    * @param currentLayerKeys
    * @private
    */
    _exitMapLayerGroups: function (map, layerType, currentLayerKeys) {
        // Quit if no keys have changed
        if (currentLayerKeys.join() === this._layerKeysByType[layerType].join()) {
            return;
        }

        // Iterate through the stored keys for this layerType
        this._layerKeysByType[layerType].forEach(function (layerKey) {
            // GATEKEEP: still around. Don't remove
            if (!layerKey || currentLayerKeys.contains(layerKey))
                return;
            // Fetch all of the mapLayerGroups for this Footprint.Layer
            // There is one MapLayerGroup per attribute
            var mapLayerGroups = this._mapLayerGroupCache[layerKey];
            // mapLayerGroups is only null if we are unchecking a Layer from the LayerManager
            if (mapLayerGroups) {
                mapLayerGroups.forEach(function (mapLayerGroup) {
                    // Remove the L.LayerGroup from the map
                    mapLayerGroup.removeLayersFromMap(map);
                    // Destroy the Footprint.MapLayerGroup
                    mapLayerGroup.destroy();
                });
                // Clear the MapLayerGroup from the cache
                this._mapLayerGroupCache[layerKey] = null;
                // Also remove it from the visible MapLayerGroup cache
                this._visibleMapLayerGroupKeysByType[layerType].removeObject(layerKey);
            }
        }, this);
        // Update the stored currentLayers
        this._layerKeysByType[layerType] = currentLayerKeys;
    },

    /***
     * Removes the minimum number of layers from visibility in response to a layer addition/removal/move
     * We compare the current layers to the cached ones. As soon as we find a mismatch we remove the layer
     * and all of those thereafter
     */
    _exitMinimumVisibleMapLayerGroups: function (layerType, currentVisibleMapLayerGroupKeysByType) {
        var map = this.get('map'),
            i = 0,
            layerGroupKey;
        while (i < this._visibleMapLayerGroupKeysByType[layerType].length) {
            layerGroupKey = this._visibleMapLayerGroupKeysByType[layerType][i];
            // They match! Check the next one.
            if (layerGroupKey === currentVisibleMapLayerGroupKeysByType[layerType][i]) {
                i++;
            }
            // They don't match. Remove this one.
            else {
                // Remove from the cache
                this._visibleMapLayerGroupKeysByType[layerType].removeAt(i);
                // Remove from the map (leave in the cache)
                this._mapLayerGroupCache[layerGroupKey].removeLayersFromMap(map);
            }
        }
        // Return the index of the this._visibleMapLayerGroupKeysByType[layerType], so we know
        // where to start adding visible layers
        return i;
    },

    /***
     * Invalidates dependent layerTypes of the given layerType. Hopefully Leaflet will make this unnceccessary
     * @param layerType
     * @private
     */
    _invalidateDependentLayerTypes: function(layerType) {
        SC.objectForPropertyPath(layerType).invalidatesLayerTypes.forEach(function(invalidatedLayerType) {
            this._visibleMapLayerGroupKeysByType[invalidatedLayerType].forEach(function (layerKey) {
                this._mapLayerGroupCache[layerKey].removeLayersFromMap(this.get('map'));
            }, this);
            // Clear the layer type's visible MapLayerGroup cache, as it's now useless.
            this._visibleMapLayerGroupKeysByType[invalidatedLayerType].length = 0;
        }, this);
    },

    _enterVisibleMapLayerGroups: function(layerType, visibleMapLayerGroupKeysByType, visibleLayerAttributesByType, layerTypeIndex) {
        // Track visible layers by their layer-attribute key
        var cachedVisibleMapLayerGroupKeys = this._visibleMapLayerGroupKeysByType[layerType];
        // If necessary, add new layers starting at the index of the last removed one.
        var visibleLayerGroupKey = visibleMapLayerGroupKeysByType[layerType];
        if (!visibleLayerGroupKey) {
            return;
        }
        visibleLayerGroupKey.slice(layerTypeIndex).forEach(function(mapLayerGroupKey, i) {
            var mapLayerGroup = this._mapLayerGroupCache[mapLayerGroupKey];
            // If it's not available yet, create it.
            if (!mapLayerGroup) {
                var layerAttribute = visibleLayerAttributesByType[layerType].objectAt(layerTypeIndex+i);
                // Create the MapLayerGroup
                mapLayerGroup = SC.objectForPropertyPath(layerType).create({layerAttribute:layerAttribute});
                // Cache it
                this._mapLayerGroupCache[mapLayerGroupKey] = mapLayerGroup;
            }

            // Added it to the map and visibility cache if needed
            if (!cachedVisibleMapLayerGroupKeys.contains(mapLayerGroupKey)) {
                cachedVisibleMapLayerGroupKeys.push(mapLayerGroupKey);
                // Append it to the map.
                mapLayerGroup.addLayersToMap(this.get('map'));
            }
        }, this);
    },

    /***
     * Clears all layers from the map until the next call to updateMapLayerGroups.
     */
    clearMapLayers: function() {
        var map = Footprint.mapController.get('content');
        this._layerTypes.forEach(function(layerType) {
            this._visibleMapLayerGroupKeysByType[layerType].forEach(function(mapLayerGroupKey) {
                var mapLayerGroup = this._mapLayerGroupCache[mapLayerGroupKey];
                if (mapLayerGroup)
                    mapLayerGroup.removeLayersFromMap(map);
                else
                    logWarning('Expected mapLayerGroup with key %@ in the cache, but it was not found'.fmt(mapLayerGroupKey));
            }, this);
            // Clear the visible MapLayerGroup keys cache
            this._visibleMapLayerGroupKeysByType[layerType].length = 0;
        }, this);
        // Reset the MapLayerGroup cache
        this._mapLayerGroupCache = {};
        // Clear the stored layerKeys
        this._layerTypes.forEach(function(layerType) {
            this._layerKeysByType[layerType] = [];
        }, this);
    },

    /***
     * Reacts to zooming and movement by showing and hiding the raster or vector layers of visible layer groups
     */
    mapLayersNeedUpdateObserver: function() {
        if (!Footprint.mapController.get('mapLayersNeedZoomUpdate')) return;
        var map = Footprint.mapController.get('content');
        this._visibleMapLayerGroupKeysByType['Footprint.ForegroundMapLayerGroup'].forEach(function(layerKey) {
            var mapLayerGroup = this._mapLayerGroupCache[layerKey];
            mapLayerGroup.setVisibilityBasedOnZoom(map);
        }, this);
        Footprint.mapController.set('mapLayersNeedZoomUpdate', NO);
    }.observes('Footprint.mapController.mapLayersNeedZoomUpdate'),

    // When the active layer changes, refresh all the visibile layers'
    // selectionLayers, making sure to only draw the active layer.
    featuresActiveControllerObserver: function() {
        var activeLayerGroup = this.get('activeLayerGroup');
        for (var layerType in this._visibleMapLayerGroupKeysByType) {
            var layerGroupKeys = this._visibleMapLayerGroupKeysByType[layerType];
            layerGroupKeys.forEach(function(layerGroupKey) {
                var layerGroup = this._mapLayerGroupCache[layerGroupKey];
                var isActiveSelectionLayer = (layerGroup == activeLayerGroup);
                this.refreshLayerGroup(layerGroup, isActiveSelectionLayer);
            }, this);
        }

        // This observes() is unusual: if the user selects a new
        // layer, and both the old and new layers have the same value
        // for features_count, we still seem to be getting an observer
        // notification. This is unexpected (since the value itself
        // didn't change) but desired. (since the layer itself changed)
        //
        // If we didn't get this extra notification, we would want to
        // also listen to Footprint.featuresActiveController.content,
        // but that gets briefly set to undefined before
        // features_count is updated. So if we listened to that, we'd
        // get lots of extra notifications.
    }.observes('Footprint.layerSelectionActiveController.features_count'),


    // Redraw the layerGroup by forcing a refresh.
    refreshLayerGroup: function(layerGroup, isActiveSelectionLayer) {
        var selectionLayer = layerGroup.get('selectionLayer');

        // not all layer groups have selection layers.
        if (!selectionLayer) {
            return;
        }

        if (isActiveSelectionLayer) {
            // If we're being passed the active selection layer, then
            // assume that
            // Footprint.layerSelectionActiveController.features_count
            // refers to the early estimate from the server about how
            // many features are present. If there are too many
            // features, then the selectionLayer is likely to crash
            // the browser, so we refuse to draw it. This is a
            // delicate assumption. If this is true we are relying on
            // a warning appearing over the map indicating that there
            // are too many features to render.
            var totalSelectedFeatures = Footprint.layerSelectionActiveController.get('features_count');
            if (totalSelectedFeatures < Footprint.MAX_MAP_VECTOR_FEATURES) {
                layerGroup.showSelection();
            } else {
                layerGroup.hideSelection();
            }
        } else {
            // We're not showing the active layer, so just hide any selection.
            layerGroup.hideSelection();
        }
    },
});
