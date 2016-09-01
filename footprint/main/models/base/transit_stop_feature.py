
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


import logging
logger = logging.getLogger(__name__)

class TransitStopFeature(Feature):
    """
    A transit stop point table based on the GTFS classification schema
    """
    objects = GeoInheritanceManager()
    route_id = models.IntegerField(null=True, blank=True)
    stop_id = models.IntegerField(null=True, blank=True)
    route_type = models.IntegerField(null=True, blank=True)
    #county = models.CharField(max_length=100, null=True, blank=True)

    class Meta(object):
        abstract = True
        app_label = "main"
