
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

from django.utils import unittest
from footprint.client.configuration.demo__kumquat_county.config_entity.demo__kumquat_county_region import \
    DemoDbEntityKey
from footprint.main.lib.functions import map_to_dict
from footprint.main.models.config.project import Project
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.config.region import Region
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.tests.test_models.permission_testing import PermissionTesting
from footprint.client.configuration.fixture import ConfigEntityFixture

__author__ = 'calthorpe_analytics'

class TestDbEntityPermissions(unittest.TestCase):
    def test__db_entity__permissions__match(self):
        db_entity_key = DemoDbEntityKey.Fab.ricate

        scenario = Scenario.objects.get(key='irthorn_base_condition')
        get_db_entity = lambda key: DbEntityInterest.objects.get(
            db_entity__key=db_entity_key(key),
            config_entity=scenario,
        ).db_entity

        class_to_default_db_entity_permissions = map_to_dict(lambda config_entity: [
                config_entity.__class__,
                ConfigEntityFixture.resolve_config_entity_fixture(config_entity).default_db_entity_permissions()
            ],
            [scenario]+scenario.ancestors
        )

        # Create a small configuration to verify permissions
        PermissionTesting([  # Test Region DbEntity permissions
                             dict(
                                 instance=get_db_entity(DemoDbEntityKey.CPAD_HOLDINGS),
                                 groups=class_to_default_db_entity_permissions[Region]
                             ),
                             # Test Project permissions
                             dict(
                                 instance=get_db_entity(DemoDbEntityKey.PROJECT_EXISTING_LAND_USE_PARCELS),
                                 groups=class_to_default_db_entity_permissions[Project],
                             ),
                             # Test Scenario permissions
                             dict(
                                 instance=get_db_entity(DemoDbEntityKey.EXISTING_LAND_USE_PARCELS),
                                 groups=class_to_default_db_entity_permissions[Scenario],
                             ),
                          ], DemoDbEntityKey).test_permissions()
