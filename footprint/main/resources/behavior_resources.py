
# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from tastypie.fields import ToManyField, ToOneField
from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.intersection import Intersection, JoinType, GeographicIntersection, \
    AttributeIntersection
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.mixins.mixins import ToOneFieldWithSubclasses

__author__ = 'calthorpe_analytics'


class JoinTypeResource(FootprintResource):
    class Meta(FootprintResource.Meta):
        queryset = JoinType.objects.filter()

class IntersectionResource(FootprintResource):

    # join_type is readonly. The API only expects a subclass to be saved, so we never have to set the
    # join_type
    join_type = ToOneField(JoinTypeResource, attribute='join_type', readonly=True)
    feature_behavior = ToOneField('footprint.main.resources.db_entity_resources.FeatureBehaviorResource', attribute='feature_behavior', readonly=True)

    def dehydrate_join_type(self, bundle):
        return bundle.obj.join_type.key

    class Meta(FootprintResource.Meta):
        queryset = Intersection.objects.all()


class GeographicIntersectionResource(IntersectionResource):
    class Meta(FootprintResource.Meta):
        queryset = GeographicIntersection.objects.filter()
        resource_name= 'geographic_intersection'

class AttributeIntersectionResource(IntersectionResource):
    class Meta(FootprintResource.Meta):
        queryset = AttributeIntersection.objects.filter()
        resource_name= 'attribute_intersection'

class BehaviorResource(FootprintResource):
    parents = ToManyField('self', attribute='parents', null=False)
    intersection = ToOneFieldWithSubclasses(IntersectionResource, attribute='intersection_subclassed', null=True)

    class Meta(FootprintResource.Meta):
        queryset = Behavior.objects.filter(deleted=False)

class FeatureBehaviorResource(FootprintResource):
    behavior = ToOneField(BehaviorResource, attribute='behavior', null=False)
    db_entity = ToOneField('footprint.main.resources.db_entity_resources.DbEntityResource', attribute='db_entity', null=True, readonly=True)
    intersection = ToOneFieldWithSubclasses(IntersectionResource, attribute='intersection_subclassed', null=True)

    class Meta(FootprintResource.Meta):
        queryset = FeatureBehavior.objects.filter(is_template=False)
        resource_name= 'feature_behavior'
