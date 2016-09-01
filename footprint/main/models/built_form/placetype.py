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
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.built_form.built_form import BuiltForm

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

# noinspection PySingleQuotedDocstring
class Placetype(BuiltForm):
    """
    Placetypes are a set of placetype_components with a percent mix applied to each placetype_component
    """
    objects = GeoInheritanceManager()
    placetype_components = models.ManyToManyField(PlacetypeComponent, through='PlacetypeComponentPercent')

    def get_component_field(self):
        return self.placetype_components

    def get_percent_set(self):
        return self.placetypecomponentpercent_set

    def get_parent_field(self):
        return

    # So the model is pluralized correctly in the admin.
    class Meta(BuiltForm.Meta):
        verbose_name_plural = "Place Types"
        app_label = 'main'
