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


class SacogExistingLandUseParcelFeature(Feature):

    # land_use_definition is added dynamically to subclasses
    api_include = ['land_use_definition', 'census_blockgroup', 'census_block', 'land_use', 'acres', 'du', 'jurisdiction', 'notes', 'emp', 'ret', 'off', 'pub', 'ind', 'other', 'assessor', 'gp', 'gluc', ]

    census_blockgroup = models.CharField(max_length=100, null=True, blank=True)
    census_block= models.CharField(max_length=100, null=True, blank=True)
    land_use = models.CharField(max_length=100, null=True, blank=True)
    acres = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    jurisdiction= models.CharField(max_length=100, null=True, blank=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    emp = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    ret = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    off = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    pub = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    ind = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    other = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    assessor= models.CharField(max_length=100, null=True, blank=True)
    gp = models.CharField(max_length=100, null=True, blank=True)
    gluc = models.CharField(max_length=100, null=True, blank=True)


    class Meta(object):
        abstract = True
        app_label = 'main'
