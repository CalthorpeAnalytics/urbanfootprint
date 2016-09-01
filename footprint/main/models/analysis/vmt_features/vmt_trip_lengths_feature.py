
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

__author__ = 'calthorpe_analytics'

from django.db import models
from footprint.main.models.geospatial.feature import Feature

class VmtTripLengthsFeature(Feature):

    productions_hbw = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    productions_hbo = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    productions_nhb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    attractions_hbw = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    attractions_hbo = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    attractions_nhb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_30min_transit = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_45min_transit = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    region = models.CharField(max_length=100, null=True, blank=True)

    class Meta(object):
        abstract = True
        app_label = 'main'
