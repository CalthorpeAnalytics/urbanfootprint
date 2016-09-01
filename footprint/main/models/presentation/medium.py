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
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name

__author__ = 'calthorpe_analytics'


class Medium(Key, Name, Deletable):
    objects = GeoInheritanceManager()

    url = models.CharField(max_length=200, null=True, blank=True)
    content_type = models.CharField(max_length=20, null=True, blank=True)
    content = PickledObjectField(null=True)

    @property
    def limited_content(self):
        """
            This property is used with the API to avoid dumpoing extraneous information.
            See Template for overrides
        :return:
        """
        return self.content

    def __unicode__(self):
        return "{0} {1}, url:{2}, content_type:{3}".format(Key.__unicode__(self),
                                                           Name.__unicode__(self), self.url, self.content_type)


    class Meta(object):
        app_label = 'main'
        verbose_name_plural = 'media'
