
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


class EndangeredSpecies(Feature):
    sname = models.CharField(max_length=50, null=True)
    cname = models.CharField(max_length=50, null=True)
    elmcode = models.CharField(max_length=50, null=True)
    occnumber = models.CharField(max_length=50, null=True)

    kquadname = models.CharField(max_length=50, null=True)
    keycounty = models.CharField(max_length=50, null=True)
    accuracy = models.CharField(max_length=50, null=True)

    presence = models.CharField(max_length=50, null=True)
    occtype = models.CharField(max_length=50, null=True)
    fedlist = models.CharField(max_length=50, null=True)
    callist = models.CharField(max_length=50, null=True)

    location = models.CharField(max_length=50, null=True)
    locdetails = models.CharField(max_length=50, null=True)
    ecological = models.CharField(max_length=50, null=True)

    threat = models.CharField(max_length=50, null=True)
    general = models.CharField(max_length=50, null=True)
    symbology = models.CharField(max_length=50, null=True)


    class Meta(object):
        abstract = True
        app_label = 'main'
