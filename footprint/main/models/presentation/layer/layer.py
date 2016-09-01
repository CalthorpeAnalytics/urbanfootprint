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
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.cloneable import Cloneable
from footprint.main.models.presentation.presentation_medium import PresentationMedium
from tilestache_uf.utils import invalidate_cache
import logging
logger = logging.getLogger(__name__)
__author__ = 'calthorpe_analytics'

class Layer(PresentationMedium, Cloneable):

    """
        Relational data configured for display as a map layer
    """
    objects = GeoInheritanceManager()

    # Indicates along with the origin_instance that the Layer is created from the origin_instance's selection
    create_from_selection = models.BooleanField(default=False)
    active_style_key = models.CharField(max_length=200, null=True, blank=True, default=None)
    # indicates whether the db_entity is a background image (basemap) explicity. these have special handling

    @property
    def full_name(self):
        return '{0} of {1}'.format(self.name, self.config_entity.name)

    @property
    def keys(self):
        return ["layer:{layer},attr:{attribute},type:{type}".format(layer=self.id, attribute=attr, type='raster')
                for attr in self.visible_attributes or []]

    @property
    def owning_presentation(self):
        """
            Every Layer has an owning LayerLibrary which is the LayerLibrary of the config_entity
            that owns the Layer's DbEntity
        :return:
        """
        from footprint.main.publishing.layer_initialization import LayerLibraryKey
        return self.db_entity_interest.db_entity.db_entity_owner.presentation_set.get(key=LayerLibraryKey.DEFAULT)

    def invalidate(self):
        logger.info("invalidating tilestache layers for layer {0}".format(self.full_name))
        for layer_key in self.keys:
            logger.info("\tkey: {0}".format(layer_key))
            invalidate_cache(layer_key)

    class Meta(object):
        app_label = 'main'
