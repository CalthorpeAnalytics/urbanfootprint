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

from footprint.main.models.built_form.infrastructure import Infrastructure
from footprint.main.models.built_form.infrastructure_type import InfrastructureType
from footprint.main.mixins.percent import Percent
from django.db import models

__author__ = 'calthorpe_analytics'

class InfrastructurePercent(Percent):
    """
        Many-to-many "through" class adds a percent field
    """
    infrastructure = models.ForeignKey(Infrastructure)
    infrastructure_type = models.ForeignKey(InfrastructureType)

    class Meta(object):
        app_label = 'main'
