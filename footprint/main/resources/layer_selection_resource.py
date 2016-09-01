
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

import logging

from tastypie.contrib.gis.resources import GeometryApiField

from footprint.main.models import ConfigEntity
from footprint.main.publishing.layer_publishing import update_or_create_layer_selections_for_layer
from footprint.main.resources.layer_resources import LayerResource


__author__ = 'calthorpe_analytics'

from django.contrib.auth import get_user_model
import geojson
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from footprint.main.lib.functions import deep_merge
from footprint.main.models.config.scenario import FutureScenario
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.main.resources.mixins.dynamic_resource import DynamicResource
from footprint.main.resources.user_resource import UserResource
from footprint.main.utils.dynamic_subclassing import get_dynamic_resource_class
from footprint.main.resources.caching import using_bundle_cache
logger = logging.getLogger(__name__)

class CustomGeometryApiField(GeometryApiField):
    def hydrate(self, bundle):
        return super(GeometryApiField, self).hydrate(bundle)
        # I don't know why the base class does this
        #if value is None:
        #    return value
        #return simplejson.dumps(value)

class LayerSelectionResource(DynamicResource):
    """
        An abstract resource class that is subclassed by the resources.py wrapper to match a particular layer_id
    """

    # Writable Fields


    query_strings = PickledDictField(attribute='query_strings', null=True, blank=True,
                                     default=lambda: dict(aggregates_string=None, filter_string=None, group_by_string=None))

    bounds = CustomGeometryApiField(attribute='bounds', null=True, blank=True, default=lambda:{})

    filter = PickledDictField(attribute='filter', null=True, blank=True)
    group_bys = PickledDictField(attribute='group_bys', null=True, blank=True)
    joins = fields.ListField(attribute='joins', null=True, blank=True)
    aggregates = PickledDictField(attribute='aggregates', null=True, blank=True)

    # Readonly Fields

    # Unique id for the Client across all LayerSelections in the system--a combination of the layer id and user id
    unique_id = fields.CharField(attribute='unique_id', null=False, readonly=True)

    user = fields.ToOneField(UserResource, 'user', readonly=True, full=False)

    # The number of features in selected_features. The LayerSelection doesn't need to include Features
    # or their ids. Features will be downloaded separately via a FeatureResource request with the
    # LayerSelection unique_id as a parameter
    features_count = fields.IntegerField(attribute='features_count', readonly=True, default=0)

    # Profiles result_fields, a result title lookup, and result mapping
    result_map = PickledDictField(attribute='result_map', null=True, readonly=True)

    summary_results = fields.ListField(attribute='summary_results', null=True, blank=True, readonly=True, default=[])
    summary_fields = fields.ListField(attribute='summary_fields', null=True, blank=True, readonly=True, default=[])
    summary_field_title_lookup = PickledDictField(attribute='summary_field_title_lookup', null=True, blank=True, readonly=True)

    query_sql = fields.CharField(attribute='query_sql', null=True, readonly=True)
    summary_query_sql = fields.CharField(attribute='summary_query_sql', null=True, readonly=True)

    # The layer instance is not a LayerSelection field, but a property of the LayerSelection subclass

    @using_bundle_cache
    def selection_layer_queryset(bundle):
        return bundle.obj.__class__.layer
    selection_layer = fields.ToOneField(LayerResource, attribute=selection_layer_queryset, readonly=True, full=False)

    selection_extent = CustomGeometryApiField(attribute='selection_extent', null=True, blank=True, default=lambda:{}, readonly=True)

    # TODO remove
    filter_by_selection = fields.BooleanField(attribute='filter_by_selection', default=False)
    # TODO unused
    selection_options = PickledDictField(attribute='selection_options', null=True, blank=True,
                                         default=lambda: dict(constrain_to_bounds=True, constrain_to_previous_results=False))

    def full_hydrate(self, bundle, for_list=False):
        """
            Clear the previous bounds or query if the other is sent
        :param bundle:
        :return:
        """

        # Remove the computed properties. Some or all will be set
        bundle.obj.summary_results = None
        bundle.obj.summary_fields = None
        bundle.obj.summary_field_title_lookup = None

        # Call super to populate the bundle.obj
        bundle = super(LayerSelectionResource, self).full_hydrate(bundle)

        # Default these to None
        for attr in ['filter', 'aggregates', 'group_bys', 'joins', 'bounds']:
            if not bundle.data.get(attr, None):
                setattr(bundle.obj, attr, None)

        # Update the features and related derived fields to the queryset
        bundle.obj.sync_to_query()
        return bundle

    def query_data_specified(self, data):
        return data.get('query', None)

    def create_subclass(self, params, **kwargs):
        """
            Subclasses the LayerSelectionResource instance's class for the given config_entity and layer.
        :param params Must contain a 'config_entity__id' and 'layer__id'
        :return:
        """

        layer = self.resolve_layer(params)
        config_entity = self.resolve_config_entity(params)

        logger.debug("Resolving LayerSelection for config_entity %s, layer %s" % (config_entity.key, layer.db_entity.key))
        layer_selection_class = get_or_create_layer_selection_class_for_layer(layer, config_entity)
        # Have the LayerPublisher create the LayerSelection instance for the user if needed
        update_or_create_layer_selections_for_layer(layer, users=[self.resolve_user(params)])

        if not layer_selection_class:
            raise Exception("Layer with db_entity_key %s has no feature_class. Its LayerSelections should not be requested" % layer.db_entity_key)
        return get_dynamic_resource_class(
            self.__class__,
            layer_selection_class
        )

    def search_params(self, params):
        """
        :param params
        :return:
        """
        user = get_user_model().objects.get(username=params['username'])
        return dict(user__id=user.id)

    def resolve_config_entity(self, params):
        """
            If the ConfigEntity param is specified it gets precedence. Otherwise
            use the Layer param
        :param params:
        :return:
        """
        if params.get('config_entity__id'):
            return ConfigEntity.objects.get_subclass(id=params['config_entity__id'])
        else:
            return Layer.objects.get(id=params['layer__id']).config_entity

    def create_layer_from_layer_selection(self, params):
        """
            Used to create a new Layer from the current LayerSelection features
        :param params:
        :return:
        """
        # Resolve the source layer from the layer_selection__id
        source_layer = self.resolve_layer(params)
        config_entity = source_layer.config_entity
        db_entity = source_layer.db_entity_interest.db_enitty
        feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
        layer = Layer.objects.get(presentation__config_entity=config_entity, db_entity_key=db_entity.key)
        layer_selection = get_or_create_layer_selection_class_for_layer(layer, config_entity, False).objects.all()[0]
        # TODO no need to do geojson here
        feature_dict = dict(
            type="Feature"
        )
        feature_dicts = map(lambda feature:
                            deep_merge(feature_dict, {"geometry":geojson.loads(feature.wkb_geometry.json)}),
                            layer_selection.selected_features or feature_class.objects.all())
        json = dict({"type": "FeatureCollection", "features": feature_dicts})
        db_entity_configuration = update_or_create_db_entity(config_entity, **dict(
            class_scope=FutureScenario,
            name='Import From Selection Test',
            key='import_selection_test',
            url='file://notusingthis'
        ))
        self.make_geojson_db_entity(config_entity, db_entity_configuration, data=json)

    class Meta(DynamicResource.Meta):
        abstract = True
        filtering = {
            # There is only one instance per user_id. This should always be specified for GETs
            "user": ALL_WITH_RELATIONS,
            "id": ALL
        }
        always_return_data = True
        # We don't want to deliver this, the user only sees and manipulates the bounds
        excludes = ['geometry']
        resource_name = 'layer_selection'
        # The following is set in the subclass based upon the dynamic model class passed into the class creator
        # queryset = LayerSelection.objects.all() # Just for model_class initialization, should never be called
