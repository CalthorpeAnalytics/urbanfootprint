
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

__author__ = 'calthorpe_analytics'

class SharedKey(models.Model):
    """
        Mixin applied to classes that use a alpha-numeric key for naming database tables. Keys must not contain spaces. They represent a human-readable identifier used to lookup by predefined constants. Unlike the Key mixin, this key field has no unique constraint. It is useful when multiple versions of something are available, such as multiple DbEntities, and they should be selected between.
    """
    key = models.CharField(max_length=100, null=False, blank=False)

    @classmethod
    def unique_key(cls):
        """
            Indicates to mixers that the key need not be unique
        :return:
        """
        return False

    def __unicode__(self):
        return "key:{0}".format(self.key)

    class Meta:
        abstract = True
