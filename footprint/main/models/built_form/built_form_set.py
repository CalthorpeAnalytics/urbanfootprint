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
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name
from footprint.main.models.built_form.built_form import BuiltForm
from django.db import models

__author__ = 'calthorpe_analytics'

class BuiltFormSet(Key, Name, Deletable):
    """
        A BuiltFormSet is a combination of any classes inheriting BuiltForm
    """
    objects = GeoInheritanceManager()
    built_forms = models.ManyToManyField(BuiltForm)

    class Meta(object):
        app_label = 'main'
