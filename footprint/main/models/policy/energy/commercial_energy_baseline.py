
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
from model_utils.managers import InheritanceManager


__author__ = 'calthorpe_analytics'


class CommercialEnergyBaseline(models.Model):

    objects = InheritanceManager()

    zone = models.IntegerField(null=False)

    retail_services_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    restaurant_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    accommodation_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    arts_entertainment_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_services_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    office_services_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    public_admin_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    education_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    medical_services_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transport_warehousing_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    wholesale_electricity = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    retail_services_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    restaurant_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    accommodation_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    arts_entertainment_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_services_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    office_services_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    public_admin_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    education_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    medical_services_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transport_warehousing_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    wholesale_gas = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = False
        app_label = 'main'
