
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.client_land_use_definition import ClientLandUseDefinition

__author__ = 'calthorpe_analytics'

from django.db import models

class SacogLandUseDefinition(ClientLandUseDefinition):
    objects = GeoInheritanceManager()

    @property
    def label(self):
        return self.land_use

    land_use = models.CharField(max_length=100, null=True, blank=True)
    min_du_ac = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    max_du_ac = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    max_emp_ac = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    rural_flag = models.BooleanField(default=False)
    detached_flag = models.BooleanField(default=False)
    attached_flag = models.BooleanField(default=False)

    pct_ret_rest = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_ret_ret = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_ret_svc = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_off_gov = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_off_off = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_off_svc = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_off_med = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_ind = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_pub_edu = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_pub_med = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_pub_gov = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    pct_other = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta(object):
        abstract = False
        app_label = 'main'
