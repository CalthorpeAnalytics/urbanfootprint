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

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.presentation.presentation_medium import PresentationMedium

__author__ = 'calthorpe_analytics'

class Result(PresentationMedium):
    """
        Relational data displayed as a result for reporting
    """
    objects = GeoInheritanceManager()

    @property
    def owning_presentation(self):
        """
            Every Result has an owning ResultLibrary which is a ResultLibrary of the config_entity.
            We find all The ResultLibraries or that config_entity and search each for the Result
        :return:
        """
        return filter(
            lambda result_library: isinstance(result_library, ResultLibrary) and self in result_library.results,
            self.db_entity_interest.db_entity.db_entity_owner.presentation_set.all().select_subclasses()
        )

    class Meta(object):
        app_label = 'main'
