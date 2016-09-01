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
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.deletable import Deletable

from footprint.main.models.config.policy import Policy, PolicyLookup
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name


__author__ = 'calthorpe_analytics'


class PolicySet(Key, Name, PolicyLookup, Deletable):
    """
        A policy set is a list of policies, which may themselves embed policies. PolicySet also defines an attributes object to store arbitrary information about the policy set
    """
    objects = GeoInheritanceManager()
    policies = models.ManyToManyField(Policy)

    class Meta(object):
        app_label = 'main'
