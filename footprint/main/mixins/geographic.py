
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

from footprint.main.models.geographies.geography import Geography

__author__ = 'calthorpe_analytics'

from django.contrib.gis.db import models


class Geographic(models.Model):
    """
    a mixin to add a reference to the Geography class
    """
    geography = models.ForeignKey(Geography, null=True)

    @classmethod
    def geography_type(cls):
        return None

    # todo: we don't need to use the layermapping importer for peer tables, so let's only put this on the base tables
    # Because of the layer importer we need this even though the geometry is in the Geography instance
    #wkb_geometry = models.GeometryField()

    class Meta(object):
        abstract = True
