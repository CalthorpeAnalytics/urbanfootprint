__author__ = 'calthorpe_analytics'


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
from django.contrib.gis.db import models


class StreetAttributeSet(models.Model):
    """
    Attributes of a :models:`main.Building`, :models:`main.BuildingType`, or :models:`main.Placetype`,
    including a reference to its uses through :model:`built_form.building_use_percent.BuildingUsePercent`.
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

    def attributes(self):
        return "building"

    lane_width = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    number_of_lanes = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    block_size = models.DecimalField(max_digits=8, decimal_places=4, default=0)
