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

from django.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.presentation.presentation import Presentation

__author__ = 'calthorpe_analytics'

class ResultLibrary(Presentation):
    """
        A page configured to show charts, grids, maps, etc
    """
    objects = GeoInheritanceManager()

    presentation_media_alias = 'results'

    # We have to put this here instead of as presentation_media on the base class to prevent a Django bug.
    # Since it is here we make the related class a Result
    results = models.ManyToManyField('Result', related_name='result_libraries')

    @property
    def computed_results(self):
        return self.computed_presentation_media()

    class Meta(object):
        app_label = 'main'
