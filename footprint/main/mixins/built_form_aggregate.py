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


from decimal import Decimal, getcontext

__author__ = 'calthorpe_analytics'

from django.contrib.gis.db import models
from django.db.models import Sum


class BuiltFormAggregate(models.Model):
    """
    An abstract class that describes a high-level built form that has a
    :model:`built_forms.building_attribute_set.BuildingAttributeSet`, defines methods to aggregate attributes
    the classes :model:`built_forms.buildingtype.BuildingType` and :model:`built_forms.placetype.Placetype`
    according to the mix of their components.
    """
    class Meta:
        abstract = True
        app_label = 'main'

    def complete_aggregate_definition(self):
        """
        Checks that all the components have been established, to avoid redundant calculations
        :return: True or False
        """

        if self.get_all_component_percents().aggregate(Sum('percent'))['percent__sum'] < .98:
            return False
        else:
            return True

    def get_all_component_percents(self):
        """
        Identifies the component class and returns the component_percent objects representing the relationship
        between the components and the BuildingAggregate
        :return: BuildingAggregate component_percents
        """
        component_percent_field = self.get_component_field().through.__name__
        component_percents = getattr(self, "{0}_set".format(component_percent_field.lower())).all()
        return component_percents

    def aggregate_attribute(self, attribute_set, attribute):

        components_to_aggregate = [
            component_percent for component_percent in self.get_all_component_percents()
            if getattr(component_percent.component(), attribute_set, None)
        ]

        getcontext().prec = 11

        return Decimal((sum([(
             float(getattr(getattr(component_percent.component(), attribute_set), attribute) or 0)) *
             float(component_percent.percent or 0) for component_percent in components_to_aggregate
        ])))

    def aggregate_agriculture_attribute_set(self):
        pass

    def aggregate_building_attribute_set(self):
        pass

    def aggregate_built_form_attributes(self):
        """
        Grabs the component buildings of the BuildingAggregate and does a weighted average of their core attributes,
        before passing the building_attribute_set to the calculate_derived_fields() method.
        """
        if not self.complete_aggregate_definition():
            return
        self.aggregate_building_attribute_set()
        self.aggregate_agriculture_attribute_set()
