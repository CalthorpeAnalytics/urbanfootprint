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


sc_require('models/presentation_models');
sc_require('models/presentation_medium_model');

// LayerLibrary is configuration of various Layers
Footprint.LayerLibrary = Footprint.Presentation.extend({
    // We currently use the results attribute instead of presentation_media.
    // In theory Sproutcore supports subclassing on nested records,
    // so we should be able to use the presentation_media attribute instead of results.
    // A Result is a subclass of PresentationMedium
    layers: SC.Record.toMany("Footprint.Layer", {
        isMaster:YES,
        inverse: 'presentation'
    }),

    _copyProperties: function () {
        return sc_super().concat([]);
    },
    _cloneProperties: function () {
         return sc_super().concat(['layers']);
    }
});

Footprint.Layer = Footprint.PresentationMedium.extend({
    // Override superclass property to specify correct related model.
    presentation: SC.Record.toOne("Footprint.LayerLibrary", {
        isMaster: NO
    }),
    // Overrides the base class. This is always a Template
    medium: SC.Record.toOne("Footprint.LayerStyle", {
        nested: YES
    }),

    isLayer: YES,
    //unique key for the active style
    active_style_key: SC.Record.attr(String),

    origin_instance: SC.Record.toOne("Footprint.Layer"),
    // A simple flag to indicate that a cloned layer's db_entity features should be created based on the
    // current layer_selection of the origin_instance
    create_from_selection: SC.Record.attr(Boolean),

    dbEntityFeatureBehavior: null,
    // Don't allow binding to the DbEntity before it's saved, since this results in retrieveRecord
    // requests when the DbEntity saves
    dbEntityFeatureBehaviorBinding: SC.Binding.oneWay('*db_entity.feature_behavior').transform(function(value) {
        return value && value.get('id') >= 0 ? value : null;
    }),

    dbEntityFeatureBehaviorStatus: null,
    dbEntityFeatureBehaviorStatusBinding: SC.Binding.oneWay('*dbEntityFeatureBehavior.status'),
    // Returns true if a layer implements remote_imagery behavior
    isBaseMap: function() {
        if (this.getPath('dbEntityFeatureBehavior') &&
            (this.getPath('dbEntityFeatureBehaviorStatus') & SC.Record.READY)) {
            return this.getPath('dbEntityFeatureBehavior.behavior').matchesSimpleKey('remote_imagery')
        }
    }.property('status', 'dbEntityFeatureBehavior', 'dbEntityFeatureBehaviorStatus').cacheable(),

    isForeground: function() {
        if (this.getPath('dbEntityFeatureBehavior') &&
            (this.getPath('dbEntityFeatureBehaviorStatus') & SC.Record.READY)) {
            return !this.getPath('dbEntityFeatureBehavior.behavior').matchesSimpleKey('remote_imagery')
        }
    }.property('status', 'dbEntityFeatureBehavior', 'dbEntityFeatureBehaviorStatus').cacheable(),

    _skipProperties: function() {
        return ['origin_instance'];
    },

    _cloneSetup: function(sourceRecord) {
        this.set('origin_instance', sourceRecord);
    }
});
