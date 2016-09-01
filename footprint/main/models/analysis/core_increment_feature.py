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

from django.db import models
from footprint.main.models.geospatial.built_form_feature import BuiltFormFeature
from footprint.main.models.geospatial.feature import Feature

__author__ = 'calthorpe_analytics'


class CoreIncrementFeature(Feature, BuiltFormFeature):
    api_include = ['built_form_key', 'land_development_category', 'refill_flag', 'pop', 'hh', 'du', 'du_detsf', 'du_attsf', 'du_mf', 'emp', 'emp_ret', 'emp_off', 'emp_pub', 'emp_ind', 'emp_ag', 'emp_military']
    built_form_key = models.CharField(max_length=100, default=None, null=True)
    land_development_category = models.CharField(max_length=20, default=None, null=True)
    refill_flag = models.IntegerField(null=True)

    pop = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    du = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_ll = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_sl = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_attsf = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_mf = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp_ret = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_off = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_pub = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_ind = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_ag = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_military = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp_retail_services = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_restaurant = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_accommodation = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_arts_entertainment = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_other_services = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp_office_services = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_education = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_public_admin = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_medical_services = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp_wholesale = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_transport_warehousing = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_manufacturing = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_utilities = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_construction = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    emp_agriculture = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_extraction = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = True
        app_label = 'main'
