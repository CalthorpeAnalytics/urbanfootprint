
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

from django.db import models
from footprint.client.configuration.scag_dm.built_form.scag_dm_land_use_definition import ScagDmLandUseDefinition
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.built_form.client_land_use import ClientLandUse

class ScagDmLandUse(ClientLandUse):
    objects = GeoInheritanceManager()
    land_use_definition = models.ForeignKey(ScagDmLandUseDefinition, null=False)

    class Meta(object):
        app_label = 'main'
