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
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name

__author__ = 'calthorpe_analytics'


class BuiltFormExample(Key, Name):
    objects = GeoInheritanceManager()

    url_aerial = models.CharField(max_length=200, null=True, blank=True)
    url_street = models.CharField(max_length=200, null=True, blank=True)
    content = PickledObjectField(null=True)

    def __unicode__(self):
        url = self.url_aerial or self.url_street
        if self.content:
            content_type = self.content.get_internal_type()
        else:
            content_type = '(none)'
        return "{0} {1}, url:{2}, content_type:{3}".format(
            Key.__unicode__(self),
            Name.__unicode__(self),
            url, content_type)

    class Meta(object):
        app_label = 'main'
        verbose_name_plural = 'media'
