
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
from tastypie.fields import DictField
from footprint.main.lib.functions import deep_copy_dict_structure
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class ModelDictField(DictField):

    def resolve_resource_field(self, *keys):
        return self._resource.base_fields.get(keys[0], self.resolve_resource_field(*keys[1:]) if len(keys)>1 else None)

    def key_dehydrate_override(self):
        """
            Override this method to create mapping from a model class dict key to different dehydrated object key. This is used for instance to map 'db_entities' to 'db_entities' because the ConfigEntity resource class wants to present selects as DbEntityInterests
        :return:
        """
        return {}

    def key_hydrate_override(self):
        """
            Override this method to create mapping from a model class dict key to different dehydrated object key. This is used for instance to map 'db_entities' to 'db_entities' because the ConfigEntity resource class wants to present selects as DbEntityInterests
        :return:
        """
        return {}

    def instance_dehydrate_override(self):
        """
            Overrides instances of the model class dict. Specify functions by dict key that map the instance to a new value. The function receives the bundle.obj and the object of the key. For instance {'db_entities':lambda config_entity, db_entity: db_entity_interest_of_db_entity(db_entity) }
        :return:
        """
        return {}

    def instance_hydrate_override(self):
        """
            Overrides instances of the model class dict. Specify functions by dict key that map the instance to a new value. The function receives the bundle.obj and the object of the key. For instance {'db_entities':lambda config_entity, db_entity: db_entity_interest_of_db_entity(db_entity) }
        :return:
        """
        return {}

    def dehydrate(self, bundle):
        """
            Handles the selections dict. This could be generalized into a custom field that handles a dictionary of assorted model instances and converts each one to a resource URI
        :param bundle:
        :return:
        """

        # Deep copy the structure to create new dict instance so we don't mutilate the source
        value = deep_copy_dict_structure(super(ModelDictField, self).dehydrate(bundle))

        return self.process_dict(value, bundle)

    def process_dict(self, dct, bundle, outer_key=None):
        for key, value in (dct or {}).items():
            updated_key = self.key_dehydrate_override().get(key, key)
            if updated_key != key:
                del dct[key]
                if isinstance(value, dict):
                    dct[updated_key] = value
            if isinstance(value, dict):
                self.process_dict(value, bundle, outer_key=updated_key)
            else:
                # value is a model instance that is to be dehydrated to a resource_uri
                updated_model_instance = self.instance_dehydrate_override().get(updated_key, lambda x,y: value)(bundle.obj, value)
                # Find the resource field on the resource that matches one of these keys
                field = self.resolve_resource_field(*([outer_key, updated_key] if outer_key else [updated_key]))
                if field:
                    field_resource = field.to_class()
                elif value:
                    # Just search FootprintResource for a resource class that matches
                    field_resource = FootprintResource.match_existing_resources(value.__class__)[0]()
                dct[updated_key] = field_resource.dehydrate_resource_uri(updated_model_instance) if value else None
        return dct

    def hydrate(self, bundle):
        """
            Hydrates a dict of resource URI to the corresponding instances by resolving the URIs. Like dehydrate_selections, this could be generalized
        :param bundle:
        :return:
        """
        value = super(ModelDictField, self).hydrate(bundle)

        # Fill the dehydrated bundle for each outer key
        for outer_key, dct in (value or {}).items():
            updated_outer_key = self.key_hydrate_override().get(outer_key, outer_key)
            if (updated_outer_key != outer_key):
                del value[outer_key]
                value[updated_outer_key] = {}
            # Each inner key value is a resource uri that is to be hydrated to an instance
            for key, resource_uri in (dct or {}).items():
                updated_key = self.key_hydrate_override().get(key, key)
                field = self.resolve_resource_field(outer_key, key)
                if not field:
                    # Can't update the value. Probably corrupt data
                    logger.warn('No resource field matching either key %s or %s' % (outer_key, key))
                    continue
                field_resource = field.to_class()
                if (updated_key != key):
                    del value[key]
                    value[updated_key] = {}
                model_instance = field_resource.get_via_uri(resource_uri, bundle.request)
                updated_instance = self.instance_hydrate_override().get(updated_outer_key, lambda x,y: model_instance)(bundle.obj, model_instance)
                value[updated_outer_key][updated_key] = updated_instance
        return value
