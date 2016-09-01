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
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name

__author__ = 'calthorpe_analytics'

class SortType(Key, Name):
    """
        SortType instances describes a way of sorting the a Django model collection
    """
    objects = GeoInheritanceManager()

    # The order_by attribute upon which to base the search of whatever Many class is being sorted
    # This will be applied to the QuerySet using order_by (self.order_by) when instance.sorted(**SortType) is called.
    order_by = models.CharField(max_length=100, null=True, blank=False, unique=True, default=None)

    class Meta(object):
        app_label = 'main'
