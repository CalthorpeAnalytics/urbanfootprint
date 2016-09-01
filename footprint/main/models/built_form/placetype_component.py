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
from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.mixins.built_form_aggregate import BuiltFormAggregate
from footprint.main.mixins.name import Name
import logging

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class PlacetypeComponentCategory(Name):
    contributes_to_net = models.BooleanField()
    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'


class PlacetypeComponent(BuiltForm, BuiltFormAggregate):
    """
        PlacetypeComponent represents a mix of PrimaryComponents, such as a "Rural Community College" or a "Boulevard"
    """
    objects = GeoInheritanceManager()
    primary_components = models.ManyToManyField(PrimaryComponent, through='PrimaryComponentPercent')
    component_category = models.ForeignKey(PlacetypeComponentCategory)

    def get_component_field(self):
        return self.__class__.primary_components

    class Meta(object):
        app_label = 'main'

    def calculate_gross_net_ratio(self):
        return 1

    def get_aggregate_field(self):
        return self.placetype_set

    def get_aggregate_built_forms(self):
        return self.placetype_set.all()

    def get_percent_set(self):
        return self.primarycomponentpercent_set
