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

from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.chart import Chart


__author__ = 'calthorpe_analytics'

class LayerChart(Chart):
    """
        A chart that has a layer configuration to allow subcharts to be displayed geographically
    """
    layer = models.ForeignKey(Layer, null=False)

    class Meta(object):
        app_label = 'main'
