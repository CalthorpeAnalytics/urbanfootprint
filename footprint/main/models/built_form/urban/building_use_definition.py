# coding=utf-8

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

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager

__author__ = 'calthorpe_analytics'

from footprint.main.mixins.name import Name
from footprint.main.models.keys.keys import Keys
from django.db import models

class BuildingUseDefinition(Name):
    """
        BuildingUseDefinition describes the possible general types of uses for a building
    """
    objects = GeoInheritanceManager()

    type = models.CharField(max_length=100, null=False, blank=False)

    class Meta(object):
        app_label = 'main'

    def get_attributes(self):
        return ['efficiency',
                'square_feet_per_unit',
                'floor_area_ratio',
                'unit_density',
                'net_built_up_area',
                'gross_built_up_area']

    def clean(self):
        use_category_dict = Keys.BUILDING_USE_DEFINITION_CATEGORIES
        category = BuildingUseDefinition.objects.get(name=use_category_dict[self.name]) or None
        self.category = category or 'Unknown'
