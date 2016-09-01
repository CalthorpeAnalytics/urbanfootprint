
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

from reversion.models import Revision
from tastypie.constants import ALL
from tastypie.fields import ToOneField, DictField

from footprint.main.lib.functions import filter_keys, merge
from footprint.main.resources.mixins.dynamic_resource import DynamicResource
from footprint.main.resources.user_resource import UserResource


__author__ = 'calthorpe_analytics'

class RevisionResource(DynamicResource):
    """
        A Django-Revision Revision model resource
    """
    user = ToOneField(UserResource, 'user', full=True, null=False)
    def dehydrate_user(self, bundle):
        """
            Expose only the username
        :param bundle:
        :return:
        """
        return filter_keys(bundle.data['user'].data, ['username'])

    class Meta(DynamicResource.Meta):
        always_return_data = True
        abstract = False
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }
        queryset = Revision.objects.all()
        resource_name = 'revision'


class VersionResource(DynamicResource):
    # There's no need to show the revision. We pull the important fields out
    # and put them in the feature resource
    #revision = ToOneField(RevisionResource, 'revision', full=True, null=False)
    #field_dict = DictField('field_dict', null=False)
    class Meta(DynamicResource.Meta):
        always_return_data = True
        abstract = True
        # Format must be excluded since it clashes with the tastypie format param
        # We exclude field_dict and instead serialize a Feature subclass instance, so that
        # we can pick up any properties that are not serialized in the version (because they don't change)
        excludes = ['format', 'revision', 'field_dict', 'serialized_data', 'type', 'object_repr', 'object_id', 'object_id_int', 'manager_slug']
        filtering = {
            # Accept the django query id__in
            "id": ALL
        }
        resource_name = 'version'

    def create_subclass(self, params, **kwargs):
        """
            Subclass this class to create a resource class specific to the Feature
        :param params.layer__id: The layer id. Optional. Used to resolve the Feature/FeatureResource subclasses if we are in FeatureResource (not in a subclass)
        :return: The subclassed resource class
        """

        layer = self.resolve_layer(params)
        config_entity = layer.config_entity.subclassed
        # Use the abstract resource class queryset model or given db_entity_key to fetch the feature subclass
        feature_class = self.resolve_model_class(config_entity=config_entity, layer=layer)
        instance = self.resolve_instance(params, feature_class)
        return self.dynamic_resource_subclass(instance, params=params, **merge(kwargs, dict(feature_class=feature_class)))
