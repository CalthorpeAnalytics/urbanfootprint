
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

from footprint.client.configuration.fixture import RegionFixture, GlobalConfigFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.client.configuration.utils import resolve_fixture
from footprint.main.lib.functions import merge
from footprint.main.models.keys.permission_key import PermissionKey, DbEntityPermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'


class DefaultRegionFixture(DefaultMixin, RegionFixture):

    def feature_class_lookup(self):
        # Get the client global_config fixture (or the default region if the former doesn't exist)
        client_global_config = resolve_fixture("config_entity", "global_config", GlobalConfigFixture)
        global_config_feature_class_lookup = client_global_config.feature_class_lookup()
        return merge(global_config_feature_class_lookup, {})

    def default_db_entities(self):
        """
            Region define DbEntities specific to the region.
            Currently there are none.
        """
        return self.default_remote_db_entities()

    def default_config_entity_groups(self, **kwargs):
        """
            Instructs Regions to create a UserGroup for directors of this region.
            The group will be named config_entity.schema()__UserGroupKey.DIRECTOR
        :param kwargs:
        :return:
        """
        return [UserGroupKey.ADMIN]

    def default_db_entity_permissions(self, **kwargs):
        """
            By default only Admins can edit Region-owned DbEntities and approve Feature changes.
            Everyone else can view them
        :param kwargs:
        :return:
        """
        return {UserGroupKey.ADMIN: DbEntityPermissionKey.ALL,
                UserGroupKey.USER: PermissionKey.VIEW}

    def import_db_entity_configurations(self, **kwargs):
        return FixtureList([])
