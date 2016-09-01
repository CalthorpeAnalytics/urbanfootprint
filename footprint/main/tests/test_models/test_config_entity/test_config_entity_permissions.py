
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
from django.utils import unittest
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.config_entity import ConfigEntityKey
from footprint.main.models.keys.permission_key import PermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.tests.test_models.permission_testing import PermissionTesting

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class TestConfigEntityPermissions(unittest.TestCase):
    def test__config_entity__permissions__match(self):
        # Create a small configuration to verify permissions
        configuration = self.config_entity_configuration()
        configuration.test_permissions()

    @staticmethod
    def config_entity_configuration():
        config_entity_key = ConfigEntityKey.Fab.ricate
        get_config_entity = lambda key: ConfigEntity.objects.get(key=config_entity_key(key)).subclassed
        return PermissionTesting([  # Test GlobalConfig permissions
            dict(
                instance=get_config_entity('global'),
                groups={  # Only the admin can edit this puppy
                    UserGroupKey.SUPERADMIN: PermissionKey.ALL,
                    UserGroupKey.ADMIN: PermissionKey.VIEW,
                    UserGroupKey.MANAGER: PermissionKey.VIEW,
                    UserGroupKey.USER: PermissionKey.VIEW,
                    # All child ConfigEntity Groups can view
                    '__'.join([get_config_entity('kumquat_county').schema_prefix, UserGroupKey.ADMIN]): PermissionKey.VIEW,
                    '__'.join([get_config_entity('irthorn').schema_prefix, UserGroupKey.MANAGER]): PermissionKey.VIEW,
                    '__'.join([get_config_entity('irthorn_base_condition').schema_prefix, UserGroupKey.USER]): PermissionKey.VIEW
                }
            ),
            # Test Region permissions
            dict(
                instance=get_config_entity('kumquat_county'),
                groups={
                    UserGroupKey.SUPERADMIN: PermissionKey.ALL,
                    UserGroupKey.ADMIN: PermissionKey.ALL,
                    UserGroupKey.MANAGER: PermissionKey.VIEW,
                    UserGroupKey.USER: PermissionKey.VIEW,
                    '__'.join([get_config_entity('kumquat_county').schema_prefix, UserGroupKey.ADMIN]): PermissionKey.ALL,
                    # All child ConfigEntity Groups can view
                    '__'.join([get_config_entity('irthorn').schema_prefix, UserGroupKey.MANAGER]): PermissionKey.VIEW,
                    '__'.join([get_config_entity('irthorn_base_condition').schema_prefix, UserGroupKey.USER]): PermissionKey.VIEW
                },
                users={
                    # Verify the user we configured in the region fixture for the Region's Group
                    '__'.join([get_config_entity('kumquat_county').schema_prefix, UserGroupKey.ADMIN]):
                    # We named our user the same as the group plus '_user'
                    'kumquat_county_user',
                }
            ),
            # Test Project permissions
            dict(
                instance=get_config_entity('irthorn'),
                groups={
                    UserGroupKey.SUPERADMIN: PermissionKey.ALL,
                    UserGroupKey.ADMIN: PermissionKey.ALL,
                    UserGroupKey.MANAGER: PermissionKey.ALL,
                    UserGroupKey.USER: PermissionKey.VIEW,
                    '__'.join([get_config_entity('kumquat_county').schema_prefix, UserGroupKey.ADMIN]): PermissionKey.ALL,
                    '__'.join([get_config_entity('irthorn').schema_prefix, UserGroupKey.MANAGER]): PermissionKey.ALL,
                    # All child ConfigEntity Groups can view
                    '__'.join([get_config_entity('irthorn_base_condition').schema_prefix, UserGroupKey.USER]): PermissionKey.VIEW
                },
                users={
                    # Verify the user we configured in the region fixture for the Project's Group
                    '__'.join([get_config_entity('irthorn').schema_prefix, UserGroupKey.MANAGER]):
                    # We named our user the same as the group plus '_user'
                    'irthorn_user',
                }
            ),
            # Test Base Scenario permissions
            dict(
                instance=get_config_entity('irthorn_base_condition'),
                groups={
                    UserGroupKey.SUPERADMIN: PermissionKey.ALL,
                    UserGroupKey.ADMIN: PermissionKey.ALL,
                    UserGroupKey.MANAGER: PermissionKey.ALL,
                    UserGroupKey.USER: PermissionKey.ALL,
                    '__'.join([get_config_entity('kumquat_county').schema_prefix, UserGroupKey.ADMIN]): PermissionKey.ALL,
                    '__'.join([get_config_entity('irthorn').schema_prefix, UserGroupKey.MANAGER]): PermissionKey.ALL,
                    '__'.join([get_config_entity('irthorn_base_condition').schema_prefix, UserGroupKey.USER]): PermissionKey.ALL
                },
                users={
                    # Verify the user we configured in the region fixture for the Project's Group
                    '__'.join([get_config_entity('irthorn_base_condition').schema_prefix, UserGroupKey.USER]):
                    # We named our user the same as the group plus '_user'
                    'irthorn_base_condition_user',
                }
            ),
        ],
        ConfigEntityKey,
        all_groups=[
            UserGroupKey.SUPERADMIN,
            UserGroupKey.ADMIN,
            UserGroupKey.MANAGER,
            UserGroupKey.USER
        ])
