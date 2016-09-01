
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

__author__ = 'calthorpe_analytics'

from django.db import models

class Name(models.Model):
    """
        Mixin applied to classes whose instances are named. Name is a human-friendly name designed for internationalization.
        Keys, by contrast, serve as ids to resolve database tables.
    """
    name = models.CharField(max_length=1024, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    @property
    def full_name(self):
        """
            Override to add context to the name, such as the ConfigEntity name
        """
        return self.name

    @property
    def label(self):
        """
            Used by queries to present a human readable version of the instance
        :return:
        """
        return self.name

    def __unicode__(self):
        return "name:{0}, description:{1}".format(self.name, self.description)

    class Meta:
        abstract = True
