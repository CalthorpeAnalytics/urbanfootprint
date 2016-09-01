
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

from tastypie.resources import ModelResource
from footprint.main.lib.functions import one_or_none
from footprint.main.models import DbEntity, ConfigEntity
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.main.publishing.layer_initialization import LayerLibraryKey
from footprint.main.publishing.layer_publishing import update_or_create_layer_selections_for_layer

__author__ = 'calthorpe_analytics'

class FeatureResourceMixin(ModelResource):
    def search_params(self, params):
        """
            The user may optionally specify a layer_selection__id instead of feature ids when querying for features.
            This prevents huge feature id lists in the URL.
        :param params
        :return:
        """
        return params

    def resolve_layer_selection(self, params):
        """
            Used to get that actual selected features, which is a short cut querying, so we don't have to query
            for potentially thousands of ids. If No layer exists then there is also no LayerSelection, in which case
            we return None
        """
        layer = self.resolve_layer(params)
        config_entity = self.resolve_config_entity(params)
        if not layer:
            return None
        update_or_create_layer_selections_for_layer(layer, users=[self.resolve_user(params)])
        layer_selection_class = get_or_create_layer_selection_class_for_layer(layer, config_entity, False)
        return layer_selection_class.objects.get(user=self.resolve_user(params))

    def remove_params(self, params):
        """
            Remove params that are used to identity the Feature subclass, but not for filtering instances
        :param params:
        :return:
        """
        return ['layer_selection__id', 'config_entity__id', 'layer__id', 'db_entity__id', 'id', 'file_dataset__id']

    def resolve_config_entity(self, params):
        if params.get('config_entity__id'):
            return ConfigEntity.objects.get_subclass(id=params['config_entity__id'])
        else:
            return self.resolve_db_entity(params).config_entity

    def resolve_db_entity(self, params):
        if params.get('db_entity__id'):
            return DbEntity.objects.get(id=params['db_entity__id'])
        else:
            return self.resolve_layer(params).db_entity

    def resolve_layer(self, params):
        """
            Resolve the Layer if one exists. We don't resolve a Layer from a DbEntity, only from a layer__id.
            It's assumed that if a Layer id doesn't come from the request params that the user doesn't
            doesn't need Features related to LayerSelection, thus no Layer is needed
        :param params:
        :return:
        """
        if params.get('layer__id'):
            return Layer.objects.get(id=params['layer__id'])
        return None

    def resolve_instance(self, params, dynamic_model_class):
        return dynamic_model_class.objects.get(id=params['id'])

    def resolve_model_class(self, config_entity=None, db_entity=None):
        """
            Resolves the model class of the dynamic resource class. In this case it's a Feature subclass
        """
        return db_entity.feature_class if \
            db_entity else \
            config_entity.feature_class_of_base_class(self._meta.queryset.model)
