#coding=utf-8

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



from django.contrib.gis.db import models

from footprint.main.models.built_form.agriculture.agriculture_attribute_set import AgricultureAttributeSet


class AgricultureAttributeSetMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'main'

    agriculture_attribute_set = models.ForeignKey(AgricultureAttributeSet, null=True)
