
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


class JurisdictionBoundary(Feature):
    city_uid = models.IntegerField(null=True)
    city = models.CharField(max_length=50, null=True)
    county = models.CharField(max_length=50, null=True)
    county_id = models.IntegerField(null=True)
    pop12 = models.DecimalField(max_digits=14, decimal_places=2)
    pop20 = models.DecimalField(max_digits=14, decimal_places=2)
    pop35 = models.DecimalField(max_digits=14, decimal_places=2)
    pop40 = models.DecimalField(max_digits=14, decimal_places=2)
    hh12 = models.DecimalField(max_digits=14, decimal_places=2)
    hh20 = models.DecimalField(max_digits=14, decimal_places=2)
    hh35 = models.DecimalField(max_digits=14, decimal_places=2)
    hh40 = models.DecimalField(max_digits=14, decimal_places=2)
    emp12 = models.DecimalField(max_digits=14, decimal_places=2)
    emp20 = models.DecimalField(max_digits=14, decimal_places=2)
    emp35 = models.DecimalField(max_digits=14, decimal_places=2)
    emp40 = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta(object):
        abstract = True
        app_label = 'main'
