
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

__author__ = 'calthorpe_analytics'

from django.contrib.auth import get_user_model
from django.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.geospatial.feature import PaintingFeature
from footprint.main.models import AnalysisModule

import logging

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class AgricultureFeature(PaintingFeature):
    """
    A dynamically subclassed abstract class that represents the agriculture canvas table for a specific Scenerio.
    Hence instances of subclasses of this class correspond to geography rows of the canvas table
    """
    objects = GeoInheritanceManager()

    # built_form is added dynamically to subclasses
    api_include = ['built_form', 'built_form_key', 'acres_gross', 'crop_yield', 'market_value', 'production_cost', 'water_consumption', 'labor_force', 'truck_trips']

    built_form_key = models.CharField(max_length=100, default=None, null=True)
    acres_gross = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    crop_yield = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    market_value = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    production_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    water_consumption = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    labor_force = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    truck_trips = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    @classmethod
    def post_save(cls, user_id, objects, **kwargs):
        """
            Called after Features are saved by the FeatureResource. This calls post save publishing for
            Features, which includes updating tilestache for impacted layers and calling the
            Agriculture Builder Analysis Tool
        :param user_id:
        :param objects:
        :param kwargs:
        :return:
        """

        ids = map(lambda obj: obj.id, objects)
        from footprint.main.publishing.feature_publishing import on_feature_post_save
        on_feature_post_save(cls, instance=objects, ids=ids, user_id=user_id)

    class Meta(object):
        app_label = 'main'
        abstract = True
