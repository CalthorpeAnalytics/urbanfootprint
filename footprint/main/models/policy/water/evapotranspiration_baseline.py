
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
from model_utils.managers import InheritanceManager

__author__ = 'calthorpe_analytics'


class EvapotranspirationBaseline(models.Model):

    objects = InheritanceManager()

    zone = models.IntegerField(null=False)
    annual_evapotranspiration = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = False
        app_label = 'main'
