
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
from footprint.main.models.tag import Tag

__author__ = 'calthorpe_analytics'

class Tags(models.Model):
    """
        Mixin applied to classes whose instances are named. Name is a human-friendly name designed for internationalization.
        Keys, by contrast, server as ids to resolve database tables.
    """
    tags = models.ManyToManyField(Tag)

    def clear_tags(self):
        self.tags.delete()

    def add_tags(self, *tags):
        """
            Adds the given tags if they don't exist
        :param tags
        :return:
        """
        self.tags.add(*(set(tags)-set(self.tags.all())))

    class Meta:
        abstract = True
