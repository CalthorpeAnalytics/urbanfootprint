
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

from django.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.geospatial.feature import Feature


__author__ = 'calthorpe_analytics'


class PhGridFeature(Feature):
    """
    Pre-processed data that does not change in future years.
    """
    objects = GeoInheritanceManager()
    county = models.CharField(max_length=250, null=True, blank=True, default=None)
    acres = models.DecimalField(max_digits=14, decimal_places=4)
    all_roads_length_feet = models.FloatField(default=0)
    local_roads_length_feet = models.FloatField(default=0)
    secondary_roads_length_feet = models.FloatField(default=0)
    freeway_arterial_length_feet = models.FloatField(default=0)
    acres_parcel_park_open_space = models.FloatField(default=0)

    class Meta(object):
        app_label = 'main'
        abstract = True
