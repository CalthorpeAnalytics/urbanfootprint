
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

from footprint.main.models.built_form.built_form_set import BuiltFormSet
from django.contrib.gis.db import models
__author__ = 'calthorpe_analytics'

class BuiltFormSets(models.Model):
    """
        Represents a collection of BuiltFormSets where a default may be specified
    """
    built_form_sets = models.ManyToManyField(BuiltFormSet)

    def add_built_form_sets(self, *built_form_sets):
        """
            Adds one or more BuiltFormSets to the instance's collection. If the instance has not yet overriden its parents' sets, the parents sets will be adopted and then the given built_form_sets will be added
        :return: The computed results after adding the given items
        """
        self._add('built_form_sets', *built_form_sets)

    def remove_built_form_sets(self, *built_form_sets):
        """
            Removes the given built_form_sets from the instances collection. These may be either items inherited from an ancestor or the instance's own items
        :param built_form_sets:
        :return: The computed results after removing the given items
        """
        self._remove('built_form_sets', *built_form_sets)

    class Meta:
        abstract = True
