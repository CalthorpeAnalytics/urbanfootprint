
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


from footprint.main.models.config.policy_set import PolicySet

__author__ = 'calthorpe_analytics'

from django.contrib.gis.db import models

class PolicySets(models.Model):
    """
        Represents a collection of PolicySets where a default may be specified
    """
    policy_sets = models.ManyToManyField(PolicySet)

    def add_policy_sets(self, *policy_sets):
        """
            Adds one or more PolicySets to the instance's collection. If the instance has not yet overriden its parents' sets, the parents sets will be adopted and then the given built_form_sets will be added. PolicySets matching that of the parent (if the parent's are adopted) will be ignored
        :return: The computed results after adding the given items
        """
        self._add('policy_sets', *policy_sets)

    def remove_policy_sets(self, *policy_sets):
        """
            Removes the given policy_sets from the instances collection. These may be either items inherited from an ancestor or the instance's own items
        :param policy_sets:
        :return: The computed results after removing the given items
        """
        self._remove('policy_sets', *policy_sets)

    class Meta:
        abstract = True
