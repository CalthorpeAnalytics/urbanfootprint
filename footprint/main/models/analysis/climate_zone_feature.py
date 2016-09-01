
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
from footprint.main.models.geospatial.feature import Feature


__author__ = 'calthorpe_analytics'


class ClimateZoneFeature(Feature):

    evapotranspiration_zone_id = models.IntegerField(null=True)
    forecasting_climate_zone_id = models.IntegerField(null=True)
    title_24_zone_id = models.IntegerField(null=True)

    class Meta(object):
        abstract = True
        app_label = 'main'
