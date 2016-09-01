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

from datetime import datetime
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.percent import Percent
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from django.db import models

__author__ = 'calthorpe_analytics'

class PlacetypeComponentPercent(Percent):
    """
        Many-to-many "through" class adds a percent field
    """
    objects = GeoInheritanceManager()
    placetype_component = models.ForeignKey(PlacetypeComponent, null=True)
    placetype = models.ForeignKey('Placetype')

    @property
    def component_class(self):
        return self.placetype_component.subclassed_built_form.__class__.__name__
    @property
    def container_class(self):
        return self.placetype.subclassed_built_form.__class__.__name__

    class Meta(object):
        app_label = 'main'

    def component(self):
        return BuiltForm.resolve_built_form(self.placetype_component)

    def aggregate(self):
        return BuiltForm.resolve_built_form(self.placetype)
