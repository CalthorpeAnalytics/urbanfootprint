
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

from footprint.client.configuration.fixture import BuiltFormFixture
from footprint.client.configuration.scag_dm.built_form.scag_dm_land_use import ScagDmLandUse
from footprint.main.lib.functions import merge
from footprint.main.models.config.region import Region
from footprint.main.models.built_form.urban.building_type import BuildingType
from footprint.main.utils.fixture_list import FixtureList


class ScagDmBuiltFormFixture(BuiltFormFixture):
    def built_forms(self):
        return merge(
            self.parent_fixture.built_forms(),
            dict(scag_land_use=self.construct_client_land_uses(ScagDmLandUse, 'scag_lu'))
        )

    def tag_built_forms(self, built_forms_dict):
        self.parent_fixture.tag_built_forms(built_forms_dict),

    def built_form_sets(self):
        return self.parent_fixture.built_form_sets() + FixtureList([
            dict(
                scope=Region,
                key='scag_land_uses',
                attribute='scag_land_use_definition',
                name='SCAG Land Uses',
                description='SCAG Land Use Codes',
                client='scag_dm',
                clazz=BuildingType,
            ),
        ]).matching_scope(class_scope=self.config_entity and self.config_entity.__class__)
