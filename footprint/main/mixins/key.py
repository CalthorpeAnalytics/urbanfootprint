
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

class Key(models.Model):
    """
        Mixin applied to classes that use a alpha-numeric key for naming database tables. Keys must not contain spaces.
        They represent a human-readable identifier used to test whether instances should be gotten or created.
        There is a unique constraint on the key. Use SharedKey for model classes that need multiple instances to share
        a key.
    """
    key = models.CharField(max_length=120, null=False, blank=False, unique=True)

    def __unicode__(self):
        return "key:{0}".format(self.key)

    @classmethod
    def unique_key(cls):
        """
            Indicates to mixers that the key must be unique.
        :return:
        """
        return True

    def resolve_by_key(self):
        """
            Resolves an unsaved instance to a database instance that matches its key
            or returns self if already saved
        """
        if self.pk:
            return self
        else:
            return self.__class__.objects.get(key=self.key)

    class Meta:
        abstract = True
