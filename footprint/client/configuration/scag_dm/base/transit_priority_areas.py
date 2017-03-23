
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

from footprint.main.models.geospatial.feature import Feature
from django.contrib.gis.db import models

__author__ = 'calthorpe_analytics'


class TransitPriorityAreas(Feature):

    city = models.CharField(max_length=150, null=True)
    county = models.CharField(max_length=150, null=True)
    county_id = models.IntegerField(null=True, blank=True)


    class Meta(object):
        abstract = True
        app_label = 'main'
