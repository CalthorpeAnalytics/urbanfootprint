
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


class PhOutcomesSummary(models.Model):

    objects = InheritanceManager()

    outcome = models.CharField(max_length=300, null=True, blank=True)
    source = models.CharField(max_length=30, null=True, blank=True)
    result = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    class Meta(object):
        abstract = True
        app_label = 'main'
