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


Footprint.intersectionEditController = SC.ObjectController.create({
    intersection: null,
    intersectionBinding: SC.Binding.oneWay('Footprint.dbEntityEditController*feature_behavior.intersection'),
    intersectionStatus: null,
    intersectionStatusBinding: SC.Binding.oneWay('*intersection.status'),
    content: function() {
       return  (this.get('intersectionStatus') & SC.Record.READY) ? this.get('intersection') : null;
    }.property('intersection', 'intersectionStatus').cacheable(),
    // Clears the attributes of the non-selected join type if the user edits the join type
    joinTypeObserver: function() {
        if ((this.get('status') != SC.Record.READY_DIRTY) || !(this.getPath('intersection.status') & SC.Record.READY))
            return;
        if (this.get('join_type') != 'attribute') {
            this.setPathIfChanged('content.from_attribute', null);
            this.setPathIfChanged('content.to_attribute', null);
        }
        else if (this.get('join_type') != 'geography') {
            this.setPathIfChanged('content.from_geography', null);
            this.setPathIfChanged('content.to_geography', null);
        }
    }.observes('.join_type', '*intersection.status')
});

Footprint.joinTypesEditController = Footprint.ArrayController.create(Footprint.SingleSelectionSupport, {
    allowsEmptySelection: NO,
    content: Footprint.Intersection.JOIN_TYPES,
    singleSelectionBinding: 'Footprint.intersectionEditController.join_type'
});

/***
 * Mixin for a join intersection controller. This is used to indicate some value for some kind of
 * join, either for the scoped DbEntity or the primary geography DbEntity
 */
Footprint.JoinIntersectionControllerMixin = {
    allowsEmptySelection: YES,
    dbEntity: null,
    // We two-way bind to the joinAttribute of the intersection
    intersection: null,
    intersectionBinding: SC.Binding.oneWay('Footprint.intersectionEditController.content'),
    joinAttribute: null,
    joinAttributeValue: function(propKey, value) {
        if (!this.get('intersection'))
            return null;
        if (value !== undefined)
            this.get('intersection').set(this.get('joinAttribute'), value);
        return this.get('intersection').get(this.get('joinAttribute'));
    }.property('intersection', 'joinAttribute'),

    singleSelectionBinding: '.joinAttributeValue'
};

Footprint._primaryGeographyDbEntityMixin = {
    activeDbEntity: null,
    activeDbEntityStatus: null,
    activeDbEntityStatusBinding: SC.Binding.oneWay('*activeDbEntity.status'),
    // The ConfigEntity id that represents contains the primary DbEntity for the active DbEntity
    // This can be null for things such as background imagery
    // Using attributes here because of caching bug with nested records in nested stores, sigh
    geographyScopeConfigEntityId: function() {
         return this.getPath('activeDbEntity.attributes.feature_class_configuration.geography_scope');
    }.property('activeDbEntity', 'activeDbEntityStatus').cacheable(),
    geographyScopeConfigEntity: function() {
        if (!this.get('geographyScopeConfigEntityId'))
            return null;
        return Footprint.store.find(Footprint.ConfigEntity, this.get('geographyScopeConfigEntityId'));
    }.property('geographyScopeConfigEntityId').cacheable()
};
/***
 * Used by controllers needing the primary geography DbEntity of the current DbEntity. This scope of the primary
 * Geography DbEntity depends on the current DbEntity
 */
Footprint.PrimaryGeographyDbEntityMixin = $.extend({}, Footprint._primaryGeographyDbEntityMixin, {
    // Find the DbEntity that is owned by the ConfigEntity and is the primary geography
    dbEntity: function() {
        return (this.getPath('geographyScopeConfigEntity.db_entities') || []).find(function(dbEntity) {
            return dbEntity.getPath('feature_class_configuration.primary_geography');
        })
    }.property('geographyScopeConfigEntity').cacheable()
});

/***
 * Used by controllers needing the primary geography DbEntities of the current DbEntity. This scope of the primary
 * Geography DbEntity depends on the current DbEntity, and any other primaries are those of the parent ConfigEntities
 * above the first primary Geography DbEntity
 */
Footprint.PrimaryGeographyDbEntitiesMixin = $.extend({}, Footprint._primaryGeographyDbEntityMixin, {
    _dbEntities: function(geographyScopeConfigEntity) {
       var parent = geographyScopeConfigEntity.get('parent_config_entity');
       return [(geographyScopeConfigEntity.get('db_entities') || []).find(function(dbEntity) {
            return dbEntity.getPath('feature_class_configuration.primary_geography');
       })].concat(parent ? this._dbEntities(parent).compact() : []).uniq();
    },
    dbEntities: function() {
        // Call the recursive function, which gets Primary geography DbEntities as long as they exist in the hierarchy
        if (!this.get('geographyScopeConfigEntity'))
            return null;
        return this._dbEntities(this.get('geographyScopeConfigEntity'));
    }.property('geographyScopeConfigEntity').cacheable()
});
