
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
from footprint.main.models.config.scenario import Scenario

__author__ = 'calthorpe_analytics'

class DialUp(models.Model):
    scenario = models.OneToOneField(Scenario, primary_key=True)

    single_family_detached = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    single_family_attached = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    multi_family = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    office_employment = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    retail_employment = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    industrial_employment = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __unicode__(self):
        return unicode("Global Dialup config for %s" % self.scenario.name)

    class Meta:
        app_label = 'main'
