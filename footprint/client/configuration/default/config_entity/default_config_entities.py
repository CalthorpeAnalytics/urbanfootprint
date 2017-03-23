
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

from footprint.client.configuration.fixture import ConfigEntitiesFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.models.config.scenario import FutureScenario, BaseScenario
from footprint.main.models.keys.keys import Keys
from footprint.main.models.keys.permission_key import PermissionKey, ConfigEntityPermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'


class ConfigEntityMediumKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'config_entity_medium'


class DefaultConfigEntitiesFixture(DefaultMixin, ConfigEntitiesFixture):
    def regions(self, region_keys=None, class_scope=None):
        return []

    def projects(self, region=None, region_keys=None, project_keys=None, class_scope=None):
        return []

    def scenarios(self, project=None, region_keys=None, project_keys=None, scenario_keys=None, class_scope=None):
        return []

    # Fixtures for testing import/cloning
    def import_scenarios(self, origin_instance):
        return FixtureList([
            dict(
                class_scope=FutureScenario,
                key=origin_instance.key[0:10:]+'_future_clone',
                name=origin_instance.name[0:10]+' Future Clone',
                parent_config_entity=origin_instance.parent_config_entity,
                origin_instance=origin_instance,
                bounds=origin_instance.bounds,
                description=origin_instance.description+' Future Clone',
                year=origin_instance.year
            ),
            dict(
                class_scope=BaseScenario,
                key=origin_instance.key[0:10]+'_base_clone',
                name=origin_instance.name[0:10]+' Base Clone',
                parent_config_entity=origin_instance.parent_config_entity,
                origin_instance=origin_instance,
                bounds=origin_instance.bounds,
                description=origin_instance.description+' Base Clone',
                year=origin_instance.year
            )
        ]).matching_scope(class_scope=origin_instance.__class__)

    def default_config_entity_permissions(self, **kwargs):
        """
            By default any PLANNERS with access to a ConfigEntity have PermissionKey.ALL permissions.
            However only the MANAGER and above have permission to merge the ConfigEntity, which
            is encompassed by ConfigEntityPermissionKey.ALL
            INTERNS and below have PermissionKey.VIEW permission
        :param kwargs:
        :return:
        """
        return {
            UserGroupKey.MANAGER: ConfigEntityPermissionKey.ALL,  # include MERGE permission
            UserGroupKey.USER: PermissionKey.ALL,  # exclude MERGE permission
            UserGroupKey.GUEST: PermissionKey.VIEW
        }
