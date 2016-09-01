
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
from footprint.main.models.geospatial.feature import Feature


class CensusBlock(Feature):

    objects = GeoInheritanceManager()
    block = models.CharField(max_length=20)
    blockgroup = models.CharField(max_length=20)
    tract = models.CharField(max_length=20)

    @property
    def label(self):
        return self.block

    class Meta:
        abstract = True
        app_label = 'main'
