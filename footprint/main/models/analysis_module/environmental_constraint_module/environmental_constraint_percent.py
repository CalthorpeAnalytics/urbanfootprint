
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



from model_utils.managers import InheritanceManager
from footprint.main.models.geospatial.db_entity import DbEntity
from django.contrib.gis.db import models

__author__ = 'calthorpe_analytics'


class EnvironmentalConstraintPercent(models.Model):

    db_entity = models.ForeignKey(DbEntity)
    analysis_tool = models.ForeignKey('EnvironmentalConstraintUpdaterTool', null=False)
    percent = models.DecimalField(max_digits=14, decimal_places=8, default=1, null=True)
    priority = models.IntegerField(default=1, null=True)

    objects = InheritanceManager()

    class Meta(object):
        app_label = 'main'
        abstract = False
