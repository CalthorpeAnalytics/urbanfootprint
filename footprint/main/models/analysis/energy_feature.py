
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



class EnergyFeature(Feature):

    title24_zone = models.IntegerField(null=True, default=None)
    fcz_zone = models.IntegerField(null=True, default=None)
    total_commercial_sqft = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    total_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    total_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    residential_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    commercial_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    residential_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    commercial_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_ll_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_sl_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_attsf_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_mf_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    retail_services_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    restaurant_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    accommodation_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_services_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    office_services_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    education_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    public_admin_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    medical_services_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    wholesale_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transport_warehousing_gas_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_ll_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_detsf_sl_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_attsf_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_mf_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    retail_services_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    restaurant_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    accommodation_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_services_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    office_services_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    education_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    public_admin_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    medical_services_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    wholesale_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transport_warehousing_electricity_use = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # for visualization
    annual_million_btus_per_unit = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = True
        app_label = 'main'
