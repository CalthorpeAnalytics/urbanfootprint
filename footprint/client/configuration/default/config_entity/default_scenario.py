
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

from django.contrib.auth import get_user_model
from django.conf import settings
from footprint.main.models.category import Category
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.client.configuration.fixture import ScenarioFixture, project_specific_project_fixtures
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.lib.functions import merge
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.config.scenario import FutureScenario, Scenario
from footprint.main.models.geospatial.intersection import Intersection, JoinTypeKey, GeographicIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.models.keys.permission_key import PermissionKey, DbEntityPermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.publishing.config_entity_initialization import get_behavior
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'


class DefaultScenarioFixture(DefaultMixin, ScenarioFixture):
    def feature_class_lookup(self):
        # Get the client project fixture (or the default region if the former doesn't exist)
        project_class_lookup = merge(*map(lambda project_fixture: project_fixture.feature_class_lookup(),
                                          project_specific_project_fixtures(config_entity=self.config_entity)))
        return project_class_lookup

    def default_db_entities(self):
        """
            Scenarios define DbEntities specific to the Scenario. Creates a list a dictionary of configuration functionality.
            These are filtered based on whether the given scenario matches the scope in the configuration
            The Default ScenarioFixture has no db_enitties. Override this method in a client-specific ScenarioFixture to
            create Scenario-specific DbEntities for that client.
        :return:
        """
        return []

    def default_config_entity_groups(self, **kwargs):
        """
            Instructs Scenarios to create a UserGroup for Users of this region.
            The group will be named config_entity.schema()__UserGroupKey.USER.
            This group probably has no use unless we wanted users limited to a specific Scenario
        :param kwargs:
        :return:
        """
        return [UserGroupKey.USER]

    def default_db_entity_permissions(self, **kwargs):
        """
            By default Manager and above can edit Scenario-owned DbEntity and approve Feature changes
            By default Planners and above can edit Scenario-owned DbEntities.
            Everyone below can view them
        :param kwargs:
        :return:
        """
        return {
            UserGroupKey.MANAGER: DbEntityPermissionKey.ALL,
            UserGroupKey.USER: PermissionKey.ALL,
            UserGroupKey.GUEST: PermissionKey.VIEW
        }

    def import_db_entity_configurations(self, **kwargs):
        """
            This is to simulate layer upload
        """
        # TODO if Scenario level layer testing is needed, use default_project.py as an example
        return []
