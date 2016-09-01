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

from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name
from model_utils.managers import InheritanceManager
from django.db import models

__author__ = 'calthorpe_analytics'


class Style(Key, Name):
    """
        Represents a style class that is applied a geographic table column (currently via PresentationMedium).
        Style inherits the properties of Medium. It might be better at some point to make Style a sibling of Medium
        instead.
    """

    objects = InheritanceManager()

    identifier = models.TextField()
    target = models.TextField()
    style_property = models.TextField()

    class Meta(object):
        app_label = 'main'
