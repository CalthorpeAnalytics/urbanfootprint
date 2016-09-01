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

__author__ = 'calthorpe_analytics'

from django.db.models.signals import post_save
from django.db.models import Sum
from django.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.built_form import BuiltForm
import logging
logger = logging.getLogger(__name__)


class PrimaryComponent(BuiltForm):
    """
        primary component represents a template primary input to built form, such as a Rural Community College or a
        tomato crop
    """
    objects = GeoInheritanceManager()

    class Meta(object):
    # This is not abstract so that django can form a many-to-many relationship with it in built_form_set
        app_label = 'main'

    def get_aggregates_field(self):
        return self.placetypecomponent_set

    def get_aggregate_built_forms(self):
        return self.placetypecomponent_set.all()
