
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

from footprint.client.configuration.fixture import UserFixture
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region


__author__ = 'calthorpe_analytics'

class ScagDmUserFixture(UserFixture):
    def users(self, **kwargs):
        # A sample user who belongs to the client ConfigEntity's director group
        # This user therefore has full permission to all config_entities of the demo client

                # A Region level user
        region_admin = {
            'groups': [self.config_entity.user_group_name(UserGroupKey.ADMIN)],
            'class_scope': Region,
            'username': 'scag_admin',
            'password': 'scag_admin@uf',
            'first_name': 'scag_dm',
            'last_name': 'admin',
            'email': 'scag_admin@example.com'
        }

        # A Project level user for each city
        project_manager = {
            'groups': [self.config_entity.user_group_name(UserGroupKey.MANAGER)],
            'class_scope': Project,
            # User name is [city]_manager
            'username': '%s_manager' % self.config_entity.key,
            'password': '%s@uf' % self.config_entity.key,
            'first_name': self.config_entity.name,
            'last_name': 'Manager',
            'email': '%s_manager@example.com' % self.config_entity.key,
        }

        # A Scenario level user for each city
        user = {
            # Make sure to include the groups of all sibling scenarios. Even if they haven't all been
            # created yet, the final scenario will capture all scenario groups
            'groups': [scenario.user_group_name(UserGroupKey.USER) for
                       scenario in self.config_entity.parent_config_entity.children()],
            'class_scope': Scenario,
            # User name is [city]_[i]
            'username': '%s' % self.config_entity.parent_config_entity.name.replace(" ", "").lower(),
            'password': '%s@uf' % self.config_entity.parent_config_entity.name.replace(" ", "").strip(),
            'first_name': self.config_entity.parent_config_entity.name,
            'last_name': 'Planner',
            'email': '%s_planner@example.com' % self.config_entity.parent_config_entity.name.replace(" ", "").lower()
        }

        # TODO:
        #   This is an experiment to not create users that are in the
        #   fixtures in order to test footprint_init performance without
        #   as many users. For now, we simply return pass as emtpty array
        #   to FixtureList()
        # return FixtureList([
        #     region_admin,
        #     project_manager,
        #     user
        # ]).matching_scope(class_scope=self.config_entity.__class__, delete_scope_keys=True)
        return FixtureList([]).matching_scope(class_scope=self.config_entity.__class__, delete_scope_keys=True)
