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

__author__ = 'calthorpe_analytics'


class ElkGroveLandUseParcel(Feature):
    pidstr = models.CharField(max_length=100, null=True, blank=True)
    parcelid = models.CharField(max_length=100, null=True, blank=True)
    pid_2005 = models.CharField(max_length=100, null=True, blank=True)
    apn = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    plan_area = models.CharField(max_length=100, null=True, blank=True)
    land_use = models.CharField(max_length=100, null=True, blank=True)
    build_density = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    zoning_code = models.CharField(max_length=100, null=True, blank=True)
    dwelling_units = models.DecimalField(max_digits=14, decimal_places=4)
    general_plan_code = models.CharField(max_length=100, null=True, blank=True)
    # land_use_definition is added dynamically to subclasses
    api_include = ['pidstr', 'parcelid', 'pid_2005', 'apn', 'name', 'plan_area', 'land_use', 'build_density',
                   'zoning_code', 'dwelling_units', 'general_plan_code']

    class Meta(object):
        abstract = True
        app_label = 'main'
