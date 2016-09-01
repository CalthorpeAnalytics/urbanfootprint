
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

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager

__author__ = 'calthorpe_analytics'
from django.contrib.gis.db import models


class AgricultureAttributeSet(models.Model):
    """
    A set of agricultural attributes for a place

    all values except unit price are per-acre densities
    """

    objects = GeoInheritanceManager()

    crop_yield = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    water_consumption = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    labor_input = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    truck_trips = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # Operations cost breakouts
    seed_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    chemical_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    fertilizer_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    custom_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    contract_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    irrigation_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    labor_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    equipment_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    fuel_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    feed_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pasture_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # Cash overhead
    land_rent_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_cash_costs = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    # Noncash overhead
    land_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    establishment_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    other_noncash_costs = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = False
        app_label = 'main'
