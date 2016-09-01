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

from django.db.models.signals import post_save

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.building_aggregate import BuildingAttributeAggregate
from footprint.main.mixins.building_attribute_set_mixin import BuildingAttributeSetMixin
from footprint.main.models.built_form.placetype_component import PlacetypeComponent

__author__ = 'calthorpe_analytics'


class BuildingType(PlacetypeComponent, BuildingAttributeAggregate, BuildingAttributeSetMixin):
    """
        BuildingType represents a mix of template building, such as a Rural Community College
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
