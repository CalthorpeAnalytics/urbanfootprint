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
from footprint.main.mixins.percent import Percent
from django.db import models
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.built_form.primary_component import PrimaryComponent

__author__ = 'calthorpe_analytics'
import logging
logger = logging.getLogger(__name__)

class PrimaryComponentPercent(Percent):
    """
        Many-to-many "through" class adds a percent field
    """
    objects = GeoInheritanceManager()
    primary_component = models.ForeignKey(PrimaryComponent)
    placetype_component = models.ForeignKey(PlacetypeComponent)

    @property
    def component_class(self):
        return self.primary_component.subclassed_built_form.__class__.__name__
    @property
    def container_class(self):
        return self.placetype_component.subclassed_built_form.__class__.__name__


    class Meta(object):
        app_label = 'main'

    def component(self):
        return BuiltForm.resolve_built_form(self.primary_component)

    def aggregate(self):
        return BuiltForm.resolve_built_form(self.placetype_component)

    def __unicode__(self):
        return '{2}: [{1}% {0}]'.format(self.primary_component.name,
                                         round(self.percent * 100, 3),
                                         self.placetype_component.name)
