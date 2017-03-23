
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

class ScagDmLandUseDefinition(ClientLandUseDefinition):
    objects = GeoInheritanceManager()
    land_use_description = models.CharField(max_length=100, null=True, blank=True)
    land_use_type = models.CharField(max_length=100, null=True, blank=True)
    # The id imported from Scag
    land_use = models.IntegerField(null=False)

    @property
    def label(self):
        return self.land_use_description

    class Meta(object):
        abstract = False
        app_label = 'main'
