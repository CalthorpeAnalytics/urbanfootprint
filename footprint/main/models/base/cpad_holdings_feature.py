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

from django.contrib.gis.db import models
from footprint.main.models.geospatial.feature import Feature

__author__ = 'calthorpe_analytics'


class CpadHoldingsFeature(Feature):
    agency_name = models.CharField(max_length=100, null=True, blank=True)
    unit_name = models.CharField(max_length=100, null=True, blank=True)
    access_type = models.CharField(max_length=100, null=True, blank=True)
    acres = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    county = models.CharField(max_length=100, null=True, blank=True)
    agency_level = models.CharField(max_length=100, null=True, blank=True)
    agency_website = models.CharField(max_length=300, null=True, blank=True)
    site_website = models.CharField(max_length=300, null=True, blank=True)
    layer = models.CharField(max_length=100, null=True, blank=True)
    management_agency = models.CharField(max_length=100, null=True, blank=True)
    label_name = models.CharField(max_length=100, null=True, blank=True)
    ownership_type = models.CharField(max_length=100, null=True, blank=True)
    site_name = models.CharField(max_length=100, null=True, blank=True)
    alternate_site_name = models.CharField(max_length=100, null=True, blank=True)
    land_water = models.CharField(max_length=100, null=True, blank=True)
    specific_use = models.CharField(max_length=100, null=True, blank=True)
    hold_notes = models.CharField(max_length=320, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    designation_agency = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    primary_purpose = models.CharField(max_length=100, null=True, blank=True)
    apn = models.CharField(max_length=100, null=True, blank=True)
    holding_id = models.CharField(max_length=100, null=True, blank=True)
    unit_id = models.CharField(max_length=100, null=True, blank=True)

    superunit = models.CharField(max_length=100, null=True, blank=True)
    agency_id = models.CharField(max_length=100, null=True, blank=True)
    mng_ag_id = models.CharField(max_length=100, null=True, blank=True)
    al_av_parc = models.CharField(max_length=100, null=True, blank=True)
    date_revised = models.CharField(max_length=100, null=True, blank=True)
    src_align = models.CharField(max_length=100, null=True, blank=True)
    src_attr = models.CharField(max_length=100, null=True, blank=True)
    d_acq_yr = models.CharField(max_length=100, null=True, blank=True)


    class Meta(object):
        abstract = True
        app_label = 'main'
