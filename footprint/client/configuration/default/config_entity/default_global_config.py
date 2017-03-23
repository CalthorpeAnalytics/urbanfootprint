
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from footprint.main.models.category import Category
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.geospatial.behavior import Behavior, BehaviorKey
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.client.configuration.fixture import GlobalConfigFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.lib.functions import map_dict
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.models.keys.permission_key import PermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from django.conf import settings
__author__ = 'calthorpe_analytics'


class DefaultGlobalConfigFixture(DefaultMixin, GlobalConfigFixture):

    def feature_class_lookup(self):
        return {}

    def default_remote_db_entities(self):
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        mapbox_layers = {
            'Aerial Photo': {"id": "elevan.kib62d92", "key": "mapbox_aerial"},
            'Simple Streets': {"id": "elevan.e53fa071", "key": "mapbox_streets"}
        }

        mapbox_base_url = "https://api.mapbox.com/v4/{id}/{{z}}/{{x}}/{{y}}.png?access_token={api_key}"

        mapbox_setups = map_dict(
            lambda name, attrs: DbEntity(
                key="mapbox_" + attrs['key'],
                name="Mapbox: " + name,
                url=mapbox_base_url.format(id=attrs['id'], api_key=settings.MAPBOX_API_KEY),
                hosts=["a", "b", "c", "d"],
                schema=self.config_entity,
                no_feature_class_configuration=True,
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('remote_imagery')
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.BASEMAPS)]
            ),
            mapbox_layers)

        cloudmade_setups = [DbEntity(
            key='osm_default',
            name='OpenStreetMap: Base Layer',
            url="http://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            schema=self.config_entity,
            no_feature_class_configuration=True,
            feature_behavior=FeatureBehavior(
                behavior=get_behavior('remote_imagery')
            ),
            _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.BASEMAPS)]
        )]
        return mapbox_setups + cloudmade_setups

    def default_db_entities(self):
        """
            Only the remote imagery DbEntities belong to the GlobalConfig
        :return:
        """
        config_entity = self.config_entity
        remote_db_entity_configurations = self.default_remote_db_entities()
        return map(
            lambda remote_db_entity_configuration: update_or_create_db_entity(
                config_entity,
                remote_db_entity_configuration),
            remote_db_entity_configurations)

    def default_config_entity_groups(self, **kwargs):
        """
            The Admin is the ConfigEntity Group of the GlobalConfig
        :param kwargs:
        :return:
        """
        return [UserGroupKey.SUPERADMIN]

    def default_db_entity_permissions(self, **kwargs):
        """
            By default Admins and above can edit GlobalConfig-owned DbEntities. Everyone else can view them
        :param kwargs:
        :return:
        """
        return {UserGroupKey.SUPERADMIN: PermissionKey.ALL,
                UserGroupKey.USER: PermissionKey.VIEW}

    def import_db_entity_configurations(self, **kwargs):
        return []
