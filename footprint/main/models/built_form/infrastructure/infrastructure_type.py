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

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.built_form.infrastructure_attributes import InfrastructureAttributeSet
from footprint.main.models.built_form.infrastructure import Infrastructure
from django.db import models
__author__ = 'calthorpe_analytics'

class InfrastructureType(PlacetypeComponent, InfrastructureAttributeSet):
    """
        Infrastructure is the container for streets, parks, detention/utilities
    """
    objects = GeoInheritanceManager()

    infrastructures = models.ManyToManyField(Infrastructure, through='InfrastructurePercent')

    def get_component_field(self):
        return self.infrastructures

    class Meta(object):
        app_label = 'main'

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name
