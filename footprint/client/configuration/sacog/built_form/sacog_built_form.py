
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
from django.template.defaultfilters import slugify

from footprint.client.configuration.fixture import BuiltFormFixture, LandUseSymbologyFixture
from footprint.client.configuration.sacog.built_form.sacog_land_use_definition import SacogLandUseDefinition
from footprint.client.configuration.sacog.built_form.sacog_land_use import SacogLandUse
from footprint.main.lib.functions import merge
from footprint.main.models.config.region import Region
from footprint.main.models.built_form.urban.building_type import BuildingType
from footprint.main.models.built_form.urban.urban_placetype import UrbanPlacetype
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.utils.fixture_list import FixtureList
from django.conf import settings


RUCS_CROPTYPE_COLORS = {
    'Alfalfa': '#5A975A',
    'Alfalfa - Organic': '#33D685',
    'Almond': '#EEEECD',
    'Almond - Organic': '#FFFEDA',
    'Apples': '#FF645E',
    'Asparagus': '#759533',
    'Beans - Common Dried': '#B76A56',
    'Beans - Black-Eyed & Lima': '#E5CEA7',
    'Beans - Chinese Long': '#497F21',
    'Blackberries': '#2B252C',
    'Blueberry': '#445A76',
    'Broccoli': '#245306',
    'Cabbage': '#C2E674',
    'Celery': '#BFE751',
    'Cherries': '#9E0009',
    'Corn for Silage': '#F0E26D',
    'Cotton': '#E1EAFC',
    'Daikon': '#D0B28C',
    'Eggplant': '#670047',
    'Figs': '#774764',
    'Grain for Silage': '#A28544',
    'Grapes - Red Wine': '#620015',
    'Grapes - White Wine': '#DDD469',
    'Lemons': '#F4BE00',
    'Lettuce - Iceberg': '#A9D75A',
    'Lettuce - Leaf': '#79A319',
    'Lettuce - Organic Leaf': '#B8EE50',
    'Mandarins': '#EC6A00',
    'Melons': '#FDBC60',
    'Nectarines': '#FD7B4B',
    'Oat Hay': '#FDD28D',
    'Olives - Table': '#39000B',
    'Olives - Oil': '#FFFF00',
    'Onions': '#BB5B75',
    'Oranges': '#F06500',
    'Orchardgrass': '#557A38',
    'Pasture': '#557F27',
    'Prunes': '#37282E',
    'Peaches - Processing':'#FD6900',
    'Pears - Green Bartlett':'#8E9600',
    'Pears - Organic':'#B36E26',
    'Pecans': '#C16F2A',
    'Peppers - Fresh': '#F52933',
    'Peppers - Processing': '#E3AA2B',
    'Pistachios': '#E3AA2B',
    'Plums': '#E99C00',
    'Pomegranates': '#80000C',
    'Potatoes - Fresh': '#7A4102',
    'Potatoes - Processing': '#E8B24C',
    'Rangeland': '#6E6B31',
    'Raspberries': '#D00D46',
    'Rice': '#DBB192',
    'Rice - Wild': '#4C2D20',
    'Rice Rotation': '#E1D7BD',
    'Safflower': '#FB5600',
    'Small Farm Leafy Greens': '#458B00',
    'Small Farm Nightshades': '#A586FD',
    'Small Farm Nuts': '#D98E4E',
    'Small Farm Nuts - Organic': '#B0441D',
    'Small Farm Root Vegetables': '#EDD8EF',
    'Small Farm Root Vegetables - Organic': '#F9E576',
    'Seed Rotation': '#7D532B',
    'Sorghum - Grain': '#986213',
    'Sorghum - Silage': '#8E3F15',
    'Sudangrass - Hay': '#72974C',
    'Sudangrass - Silage': '#5E7F3D',
    'Sunflower': '#FDD400',
    'Sweet Potato': '#E64900',
    'Squash': '#F46F00',
    'Strawberry - Fresh': '#F41123',
    'Timothygrass': '#9B9642',
    'Tomatoes - Fresh Market': '#EA612E',
    'Tomatoes - Processing': '#AD0900',
    'Walnut': '#FFE6AB',
    'Walnut - Organic': '#EEA13C',
    'Wheat': '#C17D2E'
}



class SacogBuiltFormFixture(BuiltFormFixture):
    def built_forms(self):
        return merge(
            self.parent_fixture.built_forms(client=settings.CLIENT),
            self.parent_fixture.built_forms(),
            dict(sacog_land_use=self.construct_client_land_uses(SacogLandUse, 'sac_lu')))

    def tag_built_forms(self, built_forms_dict):
        self.parent_fixture.tag_built_forms(built_forms_dict),

    def built_form_sets(self):
        return self.parent_fixture.built_form_sets() + FixtureList([
            dict(
                scope=Region,
                key='sacog_building_type',
                attribute='building_attribute_set',
                name='SACOG Buildingtypes',
                description='Built Forms for SACOG',
                client='sacog',
                clazz=BuildingType,
            ),
            dict(
                scope=Region,
                key='sacog_rucs',
                name='RUCS Types',
                attribute='agriculture_attribute_set',
                description='SACOG RUCS types',
                client=False,
                clazz=CropType,
            ),
        ]).matching_scope(class_scope=self.config_entity and self.config_entity.__class__)
