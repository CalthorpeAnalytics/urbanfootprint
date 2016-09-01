
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

#ActiveController
from tastypie.fields import CharField
from footprint.client.configuration.utils import resolve_fixture_class
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.built_form.client_land_use_definition import ClientLandUseDefinition
from footprint.main.resources.mixins.dynamic_resource import DynamicResource
from footprint.main.utils.dynamic_subclassing import get_dynamic_resource_class
from django.conf import settings


class ClientLandUseDefinitionResource(DynamicResource):
    """
        This is an abstract resource class. A client specific resource subclass is created by dynamic_resource_class
    """

    label = CharField('label', readonly=True)

    class Meta(DynamicResource.Meta):
        abstract = True
        always_return_data = False
        resource_name = 'client_land_use_definition'
        # querysets are not allowed for abstract classes. So use a special property
        # to associate the model
        _model = ClientLandUseDefinition

    def create_subclass(self, params, **kwargs):
        land_use_definition_fixture_class = resolve_fixture_class(
            "built_form",
            "land_use_definition",
            ClientLandUseDefinition,
            settings.CLIENT)

        return get_dynamic_resource_class(
            self.__class__,
            land_use_definition_fixture_class)

    def resolve_config_entity(self, params):
        """
        :param params.config_entity: The id of the config_entity
        :return: The subclassed ConfigEntity instanced based on the param value
        """
        return ConfigEntity.objects.filter(id=int(params['config_entity__id'])).all().select_subclasses()[0]
