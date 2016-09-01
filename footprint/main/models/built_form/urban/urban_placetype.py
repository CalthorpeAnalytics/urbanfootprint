

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

import logging

from django.db import models
from django.db.models.aggregates import Sum

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.building_aggregate import BuildingAttributeAggregate
from footprint.main.mixins.building_attribute_set_mixin import BuildingAttributeSetMixin
from footprint.main.mixins.street_attributes import StreetAttributes
from footprint.main.models.built_form.placetype import Placetype
from footprint.main.models.built_form.built_form import BuiltForm

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

# noinspection PySingleQuotedDocstring
class UrbanPlacetype(Placetype, BuildingAttributeSetMixin, StreetAttributes, BuildingAttributeAggregate):
    """
    Placetypes are a set of BuildingTypes with a percent mix applied to each BuildingType
    """
    objects = GeoInheritanceManager()
    intersection_density = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    def calculate_gross_net_ratio(self):
        all_components = self.get_all_component_percents().all()
        net_components = all_components.filter(placetype_component__component_category__contributes_to_net=True)

        gross = all_components.aggregate(Sum('percent'))['percent__sum']
        net = net_components.aggregate(Sum('percent'))['percent__sum']
        return net / gross

    # So the model is pluralized correctly in the admin.
    class Meta(BuiltForm.Meta):
        verbose_name_plural = "Urban Place Types"
        app_label = 'main'
