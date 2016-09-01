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
from footprint.main.mixins.agricultural_aggregate import AgricultureAttributeAggregate
from footprint.main.mixins.agriculture_attribute_set_mixin import AgricultureAttributeSetMixin
from footprint.main.models.built_form.placetype_component import PlacetypeComponent

__author__ = 'calthorpe_analytics'


class CropType(PlacetypeComponent, AgricultureAttributeAggregate, AgricultureAttributeSetMixin):
    """
        BuildingType represents a mix of template building, such as a Rural Community College
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
