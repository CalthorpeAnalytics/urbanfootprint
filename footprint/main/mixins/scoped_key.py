
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
from footprint.main.utils.utils import resolve_model

__author__ = 'calthorpe_analytics'


class ScopedKey(models.Model):
    """
        This is just like the Key mixin but it doesn't enforce a unique constraint on the key in the database.
        The key/scope should be unique per config_entity scope, however, and enforced in code.
    """
    key = models.CharField(max_length=120, null=False, blank=False, unique=False)

    # Represents the scope of the key. It should be a ConfigEntity key or something similar
    scope = models.CharField(max_length=120, null=False, blank=False, unique=False)

    def __unicode__(self):
        return "key:{0}, scope:{1}".format(self.key, self.scope)

    @property
    def class_scope(self):
        """
            Resolve the actual model class, since it's non-trivial to store in the database
        :return:
        """
        return resolve_model('footprint.main.{0}'.format(self.scope))

    def __unicode__(self):
        return "key:{0}".format(self.key)

    @classmethod
    def unique_key(cls):
        """
            Indicates to mixers that the key must be unique in the scope it pertains to.
        :return:
        """
        return True

    class Meta:
        abstract = True
