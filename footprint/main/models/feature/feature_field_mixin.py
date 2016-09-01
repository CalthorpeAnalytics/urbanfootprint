
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

import re
from dateutil.tz import tzlocal
from django.db import models
from django.db.models.fields.related import RelatedField
from django.forms import DateField
from footprint.main.lib.functions import map_to_dict, merge, compact_dict, map_dict_to_dict, flat_map
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.utils.model_utils import model_field_paths, limited_api_fields
from footprint.main.utils.query_parsing import resolve_related_model_path_via_geographies, related_field_paths
from footprint.main.utils.utils import resolve_module_attr, resolve_model

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class FeatureFieldMixin(models.Model):

    class Meta:
        abstract = True
        app_label = 'main'

    @property
    def feature_class(self):
        """
            Returns the Feature class related to this instance
        :return:
        """
        raise NotImplementedError("Must be defined by mixer")

    def sync_to_query(self):
        """
            Prepares the underlying query that determines the features fields that present in the result
            data. For LayerSelection this matters because of the underlying query. For DbEntities this
            just creates the result data with no restrictions
        :return:
        """
        raise NotImplementedError("Must be defined by mixer")

    def resolve_join_models(self):
        """
            Optional Join models. See LayerSelection
        """
        return []

    @property
    def joins(self):
        """
            Optional joins. See LayerSelection
        :return:
        """
        return []

    def create_query_set(self, query_set):
        """
            The query set to use to get field info
        """
        query_set.none()

    """
        Mixin class for LayerSelection and DbEntity to expose Feature field info
    """
    def create_result_map(self, values_query_set):
        related_models = self.resolve_join_models()
        logger.debug("Creating result map for related models %s feature class %s" % (', '.join(map(lambda r: str(r), related_models)), self.feature_class))
        feature_class_creator = FeatureClassCreator.from_dynamic_model_class(self.feature_class)
        geography_scopes = feature_class_creator.geography_scopes()
        # Get the related model paths final segment. We want to map these to the db_entity_key names
        related_model_path_to_name = map_to_dict(
            lambda related_model:
            [resolve_related_model_path_via_geographies(
                self.feature_class.objects,
                related_model).split('__')[1],
             related_model.db_entity_key],
            related_models
        )
        return values_query_set.create_result_map(
            related_models=related_models,
            # map_path_segments maps related object paths to their model name,
            # and removes the geographies segment of the path
            map_path_segments=merge(
                # Map each geography scope to its corresponding field on the feature class
                map_to_dict(
                    lambda geography_scope: [
                        feature_class_creator.geographies_field(geography_scope).name,
                        None
                    ],
                    geography_scopes),
                related_model_path_to_name)
        )

    @property
    def related_field_lookup(self):
        """
            Only for join queries
            Looks for any field of type AutoField and returns a key value of the related field,
            except for the id field. This is not for related_models being joined, but rather
            for models related to the feature tables, like BuiltForm
            For example built_form_id=AutoField maps to built_form_id=lambda built_form_id:
            :param The JoinFeature class
        :return:
        """
        def related_field_map(field_path, related_model_class_path):
            """
                This helps join feature_classes resolve related models,
                such as BuiltForms. The join feature class can't do this
                through the query since we have to use a values() query.
                Thus the query only contains built_form_id and not built_form with a
                reference to the built_form instance. The API needs to be
                able to return a property built_form=uri so we tell it how do
                do that here.
            :param field_path:
            :param related_model_class_path:
            :return: a key and value, the key is the escaped path (using _x_ for __) with the
             final _id removed and the value is
            the related model class. Ex: built_form_id results in
            [built_form, BuiltForm] for the main model or geographies_[scope_id]_end_state_feature__built_form_id in
            [geographies_[scope_id]_x_end_state_feature_x_built_form, BuiltForm]
            """

            # For static classes you module name resolution. For dynamic classes rely on current truth
            # that dynamic classes are all created in the main app, since module name resolution relies
            # on static module files
            logger.debug("Resolving %s" % related_model_class_path if\
                'dynamic_subclassing' not in related_model_class_path else\
                'main.%s' % related_model_class_path.split('.')[-1])

            related_model_class = resolve_module_attr(related_model_class_path)

            escaped_field_path = field_path.replace(r'_id$', '').replace('__', '_x_')
            return [escaped_field_path, related_model_class]

        return compact_dict(map_dict_to_dict(
            related_field_map,
            self.result_map.related_model_lookup))

    @property
    def result_field_lookup(self):
        """
            Returns a lookup that maps some field names to a lambda that describes
            how to create a human readable form of the field value. This is used by the FeatureResource
        :return:
        """

        if not self.result_map:
            # If a query has never been stored, we need to sync to an empty query
            self.sync_to_query()

        return compact_dict(map_dict_to_dict(
            self.field_map,
            self.result_map.field_lookup))



    @staticmethod
    def resolve_instance_label(instance):
        """
            Return the label property of the instance or unicode() it
        :param instance:
        :return:
        """
        return instance and (instance.label if hasattr(instance, 'label') else unicode(instance))

    @staticmethod
    def field_map(path, field_class_path):
        """
            Maps paths to a lambda that converts a value of that path
            to a human readable type. Dates are formatted and
            related objects called object.label
            :param path: The simple or concatinated path to a field
            :param field_class_path: A string representation of the field class
        """
        resolved_field_class = resolve_module_attr(field_class_path)
        if issubclass(resolved_field_class, DateField):
            # Convert to localtime (tzinfo for client will need to be specified in settings or passed from client)
            # We need to convert the timezone offset from [-]HHMM to [-]HH:MM to match javascript's format
            return [path, lambda date: date and re.sub(
                r'(\d{2})(\d{2})$',
                r'\1:\2',
                date.astimezone(tzlocal()).strftime("%Y-%m-%dT%H:%M:%S%z"))
            ]
        if issubclass(resolved_field_class, RelatedField):
            # Insist that the related instances have a label property to present to
            # the user. Use the string format as a last resort
            return [path, FeatureFieldMixin.resolve_instance_label]
        return None
