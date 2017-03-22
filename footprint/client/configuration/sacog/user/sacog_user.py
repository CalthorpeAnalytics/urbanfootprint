
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
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region

from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'

class SacogUserFixture(UserFixture):
    def users(self, **kwargs):
        key = self.config_entity.key
        return FixtureList(

            # A Region level user for the county
            [dict(groups=[self.config_entity.user_group_name(UserGroupKey.ADMIN)],
                 class_scope=Region,
                 username='director',
                 password='director@uf',
                 email='sacog_director@example.com'),

            # A Project manager level user for each city
            dict(groups=[self.config_entity.user_group_name(UserGroupKey.MANAGER)],
                 class_scope=Project,
                 # User name is [city]_manager
                 username='%s_manager' % key,
                 password='%s@uf' % key,
                 email='sacog_manager_%s@example.com' % key),

            # A Project user level user for each city
            dict(groups=[self.config_entity.user_group_name(UserGroupKey.USER)],
                 class_scope=Project,
                 # User name is [city]_manager
                 username='%s_user' % key,
                 password='%s@uf' % key,
                 email='sacog_user_%s@example.com' % key)]

            # No Scenario level users (although a group for each Scenario does exist)

        ).matching_scope(class_scope=self.config_entity.__class__, delete_scope_keys=True)
