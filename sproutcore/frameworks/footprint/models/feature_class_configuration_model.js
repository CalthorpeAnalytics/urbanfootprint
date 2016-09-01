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


Footprint.FeatureClassConfiguration = Footprint.Record.extend({
    // Add attributes whenever they need to be observed
    source_from_origin_layer_selection: SC.Record.attr(Boolean),
    // Set to the layer id being used for the source LayerSelection
    origin_layer_id: SC.Record.attr(Number),
    generated: SC.Record.attr(Boolean),
    // abstract_class_name is maintained during cloning
    abstract_class_name: SC.Record.attr(String),
    primary_key: SC.Record.attr(String),
    // The ConfigEntity id of the ConfigEntity representing the geographic scope of the DbEntity
    // This is typically the same scope as the owner of the DbEntity, except for Scenario
    // which uses its Project as the scope
    geography_scope: SC.Record.attr(Number),
    // Tells us if this representing a real feature table by checking the geography scope.
    // This is hackish, but other than background imagery all DbEntities backed by a feature table
    // should have a geography scope
    isConfigured: function() {
        return !!this.get('geography_scope');
    }.property('geography_scope')
});
