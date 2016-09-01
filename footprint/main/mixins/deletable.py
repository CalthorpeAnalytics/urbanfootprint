
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

class Deletable(models.Model):
    deleted = models.BooleanField(default=False)

    def handle_post_save_creation_error(self):
        """
            All deletable instances handle post_save creation process errors by marking themselves as deleted.
        """

        if hasattr(self, '_no_post_save_publishing'):
            self._no_post_save_publishing = True
        self.deleted = True
        self.save()
        if hasattr(self, '_no_post_save_publishing'):
            self._no_post_save_publishing = False

    class Meta(object):
        abstract = True
