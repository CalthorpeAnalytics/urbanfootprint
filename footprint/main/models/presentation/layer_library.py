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
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.presentation.presentation import Presentation

__author__ = 'calthorpe_analytics'


class LayerLibrary(Presentation):
    """
        A library that organizes the db_entities of its inherited Presentation that are associated via presentation's media. A Library supports sorting, filtering, hiding of the underlying data.
    """
    objects = GeoInheritanceManager()

    presentation_media_alias = 'layers'

    # We have to put this here instead of the base class as presentation_media to prevent a Django bug.
    # Since it is here we make the related class a Layer
    layers = models.ManyToManyField('Layer', related_name='layer_libraries')

    @property
    def computed_layers(self):
        """
            All Layers of the LayerLibrary that are not deleted and do not reference an incomplete
            DbEntity
        :return:
        """
        return self.computed_presentation_media(db_entity_interest__db_entity__setup_percent_complete=100)

    def layers_of_owned_db_entities(self):
        owned_db_entities = self.config_entity.owned_db_entities()
        return filter(lambda layer: layer.db_entity_interest.db_entity in owned_db_entities, self.layers.all())

    class Meta(object):
        app_label = 'main'
