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
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.config_entity import ConfigEntity

__author__ = 'calthorpe_analytics'


class Region(ConfigEntity):
    """
        The Region may have a parent Region.
    """
    objects = GeoInheritanceManager()

    @classmethod
    def parent_classes(cls):
        # Region can also be a parent class, but I don't want to cause infinite recursion
        return [GlobalConfig]

    class Meta(object):
        permissions = (
            ('view_region', 'View Region'),
            # this would permit the merging of region scoped db_entities from one region to another
            ('merge_region', 'Merge Region'),
        )
        app_label = 'main'
