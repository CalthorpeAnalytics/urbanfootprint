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


sc_require('models/key_mixin');
sc_require('models/name_mixin');
sc_require('models/tags_mixin');
sc_require('models/deletable_mixin');

Footprint.Intersection = Footprint.Record.extend({
    isPolymorphic: YES,

    join_type: SC.Record.attr(String),
    from_geography: SC.Record.attr(String),
    from_attribute: SC.Record.attr(String),
    to_geography: SC.Record.attr(String),
    to_attribute: SC.Record.attr(String),
    db_entity_key: SC.Record.attr(String),
    feature_behavior: SC.Record.toOne('Footprint.FeatureBehavior', {isMaster: NO, aggregate:YES}),

    description: function () {
        return "%@ join".fmt(this.get('join_type').titleize());
    }.property('join_type').cacheable(),

    db_entity: function() {
        if (this.get('db_entity_key')) {
            var layer = Footprint.layersController.find(function(layer) {
                return layer.getPath('dbEntityKey')==this.get('db_entity_key');
            }, this);
            return layer && layer.getPath('db_entity_intereset.db_entity.name');
        }
    }.property('db_entity_key').cacheable()
});

Footprint.Intersection.mixin({
    // The available join types. This could some day come from the server's JoinType class
    JOIN_TYPES: ['geographic', 'attribute'],
    // The available geographic joins. This could some day come from the server's GeographicType class
    GEOGRAPHIC_JOINS: ['polygon', 'centroid'],

    // Used by the UI to indicate the attribute of the subclass concerning the primary geography DbEntity
    joinAttribute: null,
    // Used by the UI to indicate the attribute of the subclass concerning the DbEntity in scope
    toAttribute: null
});


/***
 * A Geographic intersection between the DbEntity in scope and its primary geography DbEntity
 */
Footprint.GeographicIntersection = Footprint.Intersection.extend({
    from_geography: SC.Record.attr(String),
    to_geography: SC.Record.attr(String),

    fromAttribute: 'from_geography',
    toAttribute: 'to_geography'
});

/***
 * An Attribute intersection between an attribute of the DbEntity in scope and an attribute of its primary geography DbEntity
 */
Footprint.AttributeIntersection = Footprint.Intersection.extend({
    from_attribute: SC.Record.attr(String),
    to_attribute: SC.Record.attr(String),

    fromAttribute: 'from_attribute',
    toAttribute: 'to_attribute'
});
