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


// NOTE that this is a temporary construct to allow the mapGroupsLayerController to do its thing
// based on future plans. Eventually, visible attributes will presumably be their own records. To
// maintain downstream compatibility, those records must expose the visible attribute's name on
// 'name' and its parent layer at 'layer'.

/***
 * A simple class to store the combination of a Footprint.Layer and one of its visible attributes
 * @type {*|RangeObserver|Class|void}
 */
Footprint.LayerAttribute = SC.Object.extend({
    /**
     * The currently selected and active layer style of the layer
     */
    activeStyle: null,
    /**
     * The Footprint.Layer
     */
    layer: null,
    layerStatus: SC.Binding.oneWay('*layer.status'),

    configEntityKey:function() {
        return this.getPath('layer.db_entity.config_entity.key');
    }.property('layer', 'layerStatus').cacheable(),

    dbEntityKey: SC.Binding.oneWay('*layer.db_entity.key'),
    /***
     * The unique key for the scenario, layer and attribute. This is thus unique across the whole application.
     */

    key: function () {
        var uniqueKey = Footprint.generateLayerKey(this.get('layer'));
        return this.getPath('layer.active_style_key') ? this.getPath('layer.active_style_key') : uniqueKey;
    }.property('configEntityKey', 'dbEntityKey', 'name').cacheable(),

    layerName: function() {
        return this.getPath('layer.name');
    }.property('layer', 'layerStatus').cacheable()
});

Footprint.generateLayerKey = function (layer) {
    if (layer) {
        return '%@-%@-%@'.fmt(layer.getPath('db_entity.config_entity.key'), layer.get('dbEntityKey'), layer.get('name'));
    }
};

Footprint.visibleLayerAttributesForegroundController = SC.ArrayController.create({
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersVisibleForegroundController.arrangedObjects'),
    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('Footprint.layersController.status'),

    layersDidChange: function() {
        this.invokeOnce('doUpdateContent');
    }.observes('*layers.@each.visible'),
    doUpdateContent: function() {
        this.notifyPropertyChange('content');
    },
    content: function() {
        if (!(this.get('layersStatus') & SC.Record.READY))
            return [];

        return $.flatMap(this.get('layers') || SC.EMPTY_ARRAY, function(layer) {
            // for each of its visible attributes,
            var active_style_key = layer.getPath('active_style_key');
            var active_style = layer.getPath('medium.style_attributes').find(function(style_attribute) {
                return style_attribute.get('key') == active_style_key;
            });
            return [Footprint.LayerAttribute.create({
                activeStyle: active_style,
                layer: layer
            })];
        });
    }.property('layersStatus').cacheable()
});

Footprint.visibleLayerAttributesBackgroundController = SC.ArrayController.create({
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.layersVisibleBaseMapController.arrangedObjects'),
    layersDidChange: function() { this.invokeOnce('doUpdateContent'); }.observes('*layers.@each.visible'),
    doUpdateContent: function() { this.notifyPropertyChange('content'); },
    content: function() {
        // Background layers function without any real attribute, since they don't need to style an attribute
        // TODO we will abstract the idea of an attribute to include options for a background layer (e.g. transit on Google)
        return $.flatMap(this.get('layers') || SC.EMPTY_ARRAY, function(layer) {
            // Simply use a fake attribute 'default' for now
            return [Footprint.LayerAttribute.create({
                layer: layer
            })];
        });
    }.property()
});
