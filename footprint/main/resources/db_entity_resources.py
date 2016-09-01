
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

import logging

from tastypie import fields
from tastypie.constants import ALL
from tastypie.fields import ToOneField

from footprint.main.lib.functions import remove_keys
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.resources.behavior_resources import FeatureBehaviorResource
from footprint.main.resources.config_entity_resources import ConfigEntityResource
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.mixins.mixins import TagResourceMixin, TimestampResourceMixin, CloneableResourceMixin, \
    CategoryResourceMixin
from footprint.main.resources.mixins.permission_resource_mixin import PermissionResourceMixin
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.utils.utils import increment_key

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class DbEntityResource(
    FootprintResource,
    TagResourceMixin,
    TimestampResourceMixin,
    CloneableResourceMixin,
    PermissionResourceMixin,
    CategoryResourceMixin):
    hosts = fields.ListField('hosts', null=True)

    def get_object_list(self, request):
        return self.permission_get_object_list(request, super(DbEntityResource, self).get_object_list(request))

    config_entity = fields.ToOneField(ConfigEntityResource, 'config_entity', full=False)


    # This gets sent by the client and is used to set the url.
    # It is marked readonly so that tastypie doesn't try to find a matching
    # DbEntity attribute using it. I don't know how to tell tastypie to just map this
    # value to url
    upload_id = fields.CharField(null=True, readonly=True)

    # FeatureClassConfiguration isn't a model class, so we just pickle it
    feature_class_configuration = PickledDictField(attribute='feature_class_configuration_as_dict', null=True)

    layer = fields.ToOneField('footprint.main.resources.layer_resources.LayerResource', 'layer', null=True, readonly=True)

    def hydrate_feature_class_configuration(self, bundle):
        if bundle.obj.id > 0:
            del bundle.data['feature_class_configuration']
        return bundle

    # Describes the structure of the Feature class
    # TODO this should replace feature_fields of the DbEntityResource once we can model
    # Tastypie's schema object as a non-model class an make this a toOne relationship
    # That way the schema info will only be downloaded when requested
    #feature_schema = PickledDictField(attribute='feature_class', null=True, readonly=True)
    #def dehydrate_feature_schema(self, bundle):
    #    return FeatureResource().dynamic_resource_subclass(db_entity=bundle.obj)().build_schema()

    # FeatureBehavior is a settable property of DbEntity, since the relationship is actually defined
    # from FeatureBehavior to DbEntity.
    feature_behavior = ToOneField(FeatureBehaviorResource, attribute='feature_behavior', null=True)

    _content_type_ids = None
    _perm_ids = None

    def lookup_kwargs_with_identifiers(self, bundle, kwargs):
        """
            Override to remove feature_behavior from the lookup_kwargs,
            since it is actually defined in reverse--feature_behavior has a db_entity
        """

        return remove_keys(
            super(DbEntityResource, self).lookup_kwargs_with_identifiers(bundle, kwargs),
            ['feature_behavior'])


    def full_hydrate(self, bundle):
        hydrated_bundle = super(DbEntityResource, self).full_hydrate(bundle)
        # If new, Ensure the db_entity schema matches that of the config_entity
        # This happens after all hydration since it depends on two different fields
        if not hydrated_bundle.obj.id:
            hydrated_bundle.obj.schema = hydrated_bundle.obj._config_entity.schema()

        return hydrated_bundle

    def hydrate(self, bundle):
        if not bundle.data.get('id'):
            bundle.obj.creator = self.resolve_user(bundle.request.GET)
            # Update the key if this is a new instance but the key already is in use
            while DbEntity.objects.filter(key=bundle.data['key']).count() > 0:
                bundle.data['key'] = increment_key(bundle.data['key'])
            # Set this field to 0 so we can track post save progress and know when
            # the DbEntity is completely ready
            bundle.obj.setup_percent_complete = 0
            bundle.obj.key = bundle.data['key']

        bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return bundle

    def dehydrate_url(self, bundle):
        # Use the upload_id to create a source url for the db_entity
        if bundle.data['url'].startswith('postgres'):
            # Never show a postgres url
            return 'Preconfigured Layer'
        else:
            return bundle.data['url']

    def hydrate_url(self, bundle):
        # Use the upload_id to create a source url for the db_entity
        if bundle.data.get('upload_id', False):
            bundle.data['url'] = 'file:///tmp/%s' % bundle.data['upload_id']
        return bundle

    def dehydrate_feature_class_configuration(self, bundle):
        return remove_keys(bundle.data['feature_class_configuration'], ['class_attrs', 'related_class_lookup']) if\
            bundle.data['feature_class_configuration'] else None

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = DbEntity.objects.filter(deleted=False, setup_percent_complete=100)
        excludes=['table', 'query', 'hosts', 'group_by']
        resource_name= 'db_entity'
        filtering = {
            "id": ALL,
        }
