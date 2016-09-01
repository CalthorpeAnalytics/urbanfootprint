
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
from footprint.main.models.category import Category

__author__ = 'calthorpe_analytics'

class Categories(models.Model):
    """
        Mixin applied to classes whose instances are named. Name is a human-friendly name designed for internationalization.
        Keys, by contrast, server as ids to resolve database tables.
    """
    categories = models.ManyToManyField(Category)

    def add_categories(self, *categories):
        """
            Adds the given categories, enforcing unique keys. Incoming category instances replaces those with duplicate keys
        :param categories:
        :return:
        """
        self.categories.remove(*self.categories.filter(key__in=map(lambda category: category.key, categories)))
        self.categories.add(*categories)

    class Meta:
        abstract = True
