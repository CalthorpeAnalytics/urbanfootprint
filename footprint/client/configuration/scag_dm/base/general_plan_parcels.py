# coding=utf-8

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

from django.contrib.gis.db import models
from footprint.main.models.geospatial.feature import Feature
from django.db.models import DateTimeField

__author__ = 'calthorpe_analytics'


class GeneralPlanParcels(Feature):

    apn = models.CharField(max_length=100, null=True, blank=True)
    fips = models.IntegerField(null=True)
    scaguid12 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    density = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    year_adopt = models.CharField(max_length=100, null=True, blank=True)
    city_gp_code = models.CharField(max_length=100, null=True, blank=True)
    zone_code = models.CharField(max_length=100, null=True, blank=True)
    scag_gp_code = models.IntegerField(null=True, blank=True)
    acres = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    scag_gp_secondary = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=1024, null=True, blank=True)

    class Meta(object):
        abstract = True
        app_label = 'main'
