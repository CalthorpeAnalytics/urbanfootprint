
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

from django.contrib.gis.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager

__author__ = 'calthorpe_analytics'


class ClientLandUseDefinition(models.Model):
    """
        A generic land use definition class for clients to subclass
    """
    objects = GeoInheritanceManager()

    api_include = None

    @property
    def label(self):
        """
            For display in the API
            Override this in the subclass to delegate to a property that represents the instance
        """
        return None

    class Meta(object):
        abstract = True
        app_label = 'main'
