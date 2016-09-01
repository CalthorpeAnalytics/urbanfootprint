# coding=utf-8

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

__author__ = 'calthorpe_analytics'


class Geography(models.Model):
    """
        Represents a geographic shape such as a parcel, grid cell, line, etc. Other classes having features should
        associate to subclasses of this subclass it.
    """
    objects = models.GeoManager()
    geometry = models.GeometryField()
    # An identifier that uniquely identifies the source table that provided these geographies.
    source_table_id = models.IntegerField(null=False, db_index=True)
    # An identifier that uniquely a row from the source table, usually its id
    source_id = models.IntegerField(null=False, db_index=True, max_length=200)

    class Meta(object):
        abstract = True,
        app_label = 'main'
