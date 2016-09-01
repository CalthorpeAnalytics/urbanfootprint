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
 * The field attributes of the Primary Geography DbEntity of the active DbEntity
 * This is usually the DbEntity of the same ConfigEntity scope through which all joins are pre-cached.
 * For Scenarios the it is the Project, but at any rate it is resolved by
 * db_entity.feature_class_configuration.geography_scope, which gives the id of the
 * ConfigEntity for which to find a DbEntity marked with feature_class_configuration.primary_geography
 */
Footprint.primaryDbEntityAttributeIntersectionEditController = Footprint.FeatureFieldsController.create(
    Footprint.JoinIntersectionControllerMixin,
    Footprint.PrimaryGeographyDbEntityMixin, {

    activeDbEntityBinding: SC.Binding.oneWay('Footprint.primaryDbEntitiesEditController.firstObject'),
    joinAttribute: 'from_attribute',
    templateFeatureBinding: SC.Binding.oneWay('Footprint.primaryDbEntityTemplateFeaturesController.firstObject'),
    templateFeatureStatusBinding: SC.Binding.oneWay('Footprint.primaryDbEntityTemplateFeaturesController.status'),
    // Binding here instead of the base class prevents a strange infinite loop
    statusBinding: SC.Binding.oneWay('.templateFeatureStatus')
});

/***
 * The field attributes of the DbEntity being viewed or edited in the Data Manager
 */
Footprint.targetDbEntityJoinAttributeIntersectionEditController = Footprint.FeatureFieldsController.create(
    Footprint.JoinIntersectionControllerMixin, {

    joinAttribute: 'to_attribute',
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityEditController.content'),
    templateFeatureBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.content'),
    templateFeatureStatusBinding: SC.Binding.oneWay('Footprint.templateFeatureActiveController.status'),
    // Binding here instead of the base class prevents a strange infinite loop
    statusBinding: SC.Binding.oneWay('.templateFeatureStatus')
});



/***
 * The selected geography of the DbEntity for a geographic join. This is nulled if the join type becomes attribute
 * This controls the from_geography of the DbEntity's Behavior's intersection
 */
Footprint.primaryDbEntityGeographicIntersectionEditController = SC.ArrayController.create(
    Footprint.JoinIntersectionControllerMixin,
    Footprint.PrimaryGeographyDbEntityMixin,
    Footprint.SingleSelectionSupport, {

    activeDbEntityBinding: SC.Binding.oneWay('Footprint.primaryDbEntitiesEditController.firstObject'),
    content: Footprint.Intersection.GEOGRAPHIC_JOINS,
    joinAttribute: 'from_geography'
});

/***
 * The selected geography of the DbEntity for a geographic join. This is nulled if the join type becomes attribute
 * This controls the to_geography of the DbEntity's Behavior's intersection
 */
Footprint.targetDbEntityGeographicIntersectionEditController = SC.ArrayController.create(
    Footprint.JoinIntersectionControllerMixin,
    Footprint.SingleSelectionSupport, {

    content: Footprint.Intersection.GEOGRAPHIC_JOINS,
    dbEntityBinding: SC.Binding.oneWay('Footprint.dbEntityEditController.content'),
    joinAttribute: 'to_geography'
});
