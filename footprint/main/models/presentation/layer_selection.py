
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

import json
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.db.models.fields import DateField, TextField
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError

from geojson import loads
from picklefield import PickledObjectField

from footprint.main.lib.functions import flat_map, any_true, map_to_dict, dual_map_to_dict, map_dict, compact_dict
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.name import Name
from footprint.main.models.database.information_schema import InformationSchema
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.feature.feature_field_mixin import FeatureFieldMixin
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.medium import Medium
from footprint.main.utils.dynamic_subclassing import create_tables_for_dynamic_classes, drop_tables_for_dynamic_classes, dynamic_model_class
from footprint.main.utils.model_utils import model_field_paths, limited_api_fields
from footprint.main.utils.query_parsing import parse_query, related_field_paths
from footprint.main.utils.utils import parse_schema_and_table, clear_many_cache_on_instance_field, normalize_null, get_property_path, \
    resolve_module_attr
from footprint.main.models.geospatial.feature import Feature

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

DEFAULT_GEOMETRY = GEOSGeometry('MULTIPOLYGON EMPTY')

class LayerSelection(Name, FeatureFieldMixin):
    """
        An abstract feature class that represents selection layers corresponding to a ConfigEntity  and user in the system.
        Each instance has a Layer reference which references FeatureClass via its db_entity_key,
        and this FeatureClass's instances are computed and stored in selected_features based on the value of geometry.
        The selected_feature property returns a query of the FeatureClass. No Feature subclass specific field exists
        in this model instead features are simply cached in a pickedobjectfield.
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
        # LayerSelection is subclassed dynamically per-Layer and are stored in the Layer's ConfigEntity's schema.
        # They are per Layer because the feature toMany must be created dynamically to be specific to the Feature subclass
        abstract = True

    # The user to whom the selection belongs
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    # The geometry of the selection. If accumulating selections we can just add polygons together.
    geometry = models.GeometryField(null=True, default=DEFAULT_GEOMETRY)

    # The selection options, currently the booleans 'constrain_to_bounds' and 'constrain_to_query'
    # Both are true by default, meaning if either bounds or query are present apply each
    # The value of constrain_to_bounds has no affect if bounds is empty
    # The value of constrain_to_query has no affect if the previous results were empty
    selection_options = PickledObjectField(
        null=True,
        default=lambda: dict(constrain_to_bounds=True, constrain_to_query=True))

    aggregates = PickledObjectField(null=True)
    filter = PickledObjectField(null=True)
    joins = PickledObjectField(null=True)
    group_bys = PickledObjectField(null=True)

    # This dictionary of the raw query strings, stored so the UI can show them again
    query_strings = PickledObjectField(null=True, default=lambda: dict(aggregates_string=None, filter_string=None, group_by_string=None))

    # The selected Feature instances of the feature class/table that the layer represents.
    # This field is always written to when the bounds property is set.
    # We model this as a blob because it never needs to be queried in part. Also, it's difficult to get Django
    # to correctly create a ManyToMany dynamic field of a dynamic Feature subclass. The declaration works fine,
    # but resolving field names tends to run into problems with the name_map cache that Django uses to track field
    # relationships.
    # This field is created dynamically in the dynamic class creation below
    #features=models.ManyToManyField(feature_class, through=dynamic_through_class, related_name=table_name)

    # A simple class that provides the fields, title_lookup, and field mapping of the current query results
    result_map = PickledObjectField(null=True)

    # Stores summary results, i.e. results produced by query aggregation. These are always a list of dicts
    summary_results = PickledObjectField(null=True)
    # The ordered list of field names matching the summary results
    summary_fields = PickledObjectField(null=True)
    # A lookup from the field name to a human readable title
    summary_field_title_lookup = PickledObjectField(null=True, default=lambda: {})

    # The sql used to create the results, for exporting and debugging
    query_sql = TextField(null=True)

    # The sql used to create the summary results, for exporting debugging
    summary_query_sql = TextField(null=True)

    @staticmethod
    def cleanup_title(key):
        parts = key.split('__')
        if len(parts) > 2:
            return '_'.join(key.split('__')[2:])
        else:
            return '_'.join(parts)

    def update_features(self, query_set):
        """
            Updates the features property ManyToMany with the features returned by self.create_query_set, whose
            QuerySet is based upon the current values of the LayerSelection instance
            :param query_set: The query_set from create_query_set or similar
        :return:
        """
        self.clear_features()
        if not query_set:
            # If none keep features clear and return
            return
        # Update the features based on the new query_set
        self.features.through.objects.bulk_create(
            map(
                lambda feature: self.features.through(
                    feature=feature,
                    layer_selection=self),
                query_set.all()
            )
        )

    def resolve_join_models(self):
        """
            The array of relevant related_models based on self.joins, which contains 0 or more db_entity_keys
        """
        return map(lambda join: self.config_entity.db_entity_feature_class(join), self.joins or [])


    def clear_features(self):
        """
            Removes all features from the LayerSelectionFeature through class
        """
        self.features.through.objects.all().delete()

    def update_summary_results(self, query_result):
        """
            Updates the summary results with the given QuerySet or results list
        :param self:
        :param query_result:
        :return:
        """
        if isinstance(query_result, QuerySet):
            # Find aggregate and normal field names
            aggregate_names = query_result.aggregate_names if hasattr(query_result, 'aggregate_names') else []
            self.summary_fields = (query_result.field_names if hasattr(query_result, 'field_names') else []) + aggregate_names
            # Find aggregate and normal field titles
            aggregate_titles = map_dict(lambda key, value: self.cleanup_title(key), query_result.query.aggregates) if hasattr(query_result.query, 'aggregates') else []
            titles = map(lambda tup: self.cleanup_title(tup[1]), query_result.query.select) + aggregate_titles
            # Create a lookup from field name to title
            self.summary_field_title_lookup = dual_map_to_dict(lambda key, value: [key, value], self.summary_fields, titles)
            self.summary_query_sql = str(query_result.query)
        elif len(query_result) > 0:
            # For single row aggregates. TODO figure out who to extract the names from the query
            self.summary_fields = query_result[0].keys()
            self.summary_field_title_lookup = map_to_dict(lambda key: [key, key], self.summary_fields)
            self.summary_query_sql = str(query_result.query)

        self.summary_results = list(query_result)
        self.save()

    def clear_summary_results(self):
        self.summary_results = None

    @property
    def unique_id(self):
        """
            A unique id across all LayerSelection subclasses
        """
        return '%s_%s' % (self.user.id, self.layer.id)

    @classmethod
    def from_unique_id(cls, unique_id):
        """
            Recovers a LayerSelection instance from the unique_id
        :param unique_id:
        :return:
        """
        user_id, layer_id = map(lambda part: int(part), unique_id.split('_'))
        layer_selection_class = get_or_create_layer_selection_class_for_layer(Layer.objects.get(id=layer_id), no_table_creation=True)
        return layer_selection_class.objects.get(user__id=user_id)


    @property
    def bounds(self):
        """
            Always the same as the geometry field for read-access
        :return:
        """
        return loads(self.geometry.json)

    @bounds.setter
    def bounds(self, value):
        """
            Convert the bounds from JSON to the GEOSGeometry format
            bounds is a python getter/setter that sets the geometry field
        :param value: geojson python object
        :return:
        """
        # TODO need for geometry
        if value and len(value.keys()) > 0:
            self.geometry = GEOSGeometry(json.dumps(value))
        else:
            self.geometry = GEOSGeometry('MULTIPOLYGON EMPTY')

    @property
    def selected_features(self):
        """
            Returns all Feature instances in self.features
        :return:
        """

        try:
            return self.features.all()
        except FieldError:
            # Fix a terrible Django manyToMany cache initialization bug by clearing the model caches
            clear_many_cache_on_instance_field(self.features)
            return self.features.all()

    @property
    def selected_features_or_values(self):
        """
            Returns either the instance-based query_set--selected_features or the values-based on--values_query_set.
            The latter is returned if self.joins has items, meaning joins are required and we can't return the instances
        """
        return self.values_query_set() if self.joins and len(self.joins) > 0 else self.selected_features

    @property
    def features_count(self):
        """
            Used by the LayerSelectionResource
        :return:
        """
        return len(self.selected_features_or_values)

    def create_join_feature_class(self):
        """
            Make an unmanaged Django model based on the joined fields
        """
        return FeatureClassCreator(
            self.config_entity,
            self.layer.db_entity_interest.db_entity).dynamic_join_model_class(
                self.resolve_join_models(),
                self.result_map.related_model_lookup.keys()
            )

    @property
    def selection_extent(self):
        """
            The extent of the current selection or the whole thing if no selection
        """
        return self.selected_features.extent_polygon() if len(self.selected_features) > 0 else self.feature_class.objects.extent_polygon()

    def clear(self):
        """
            Clears the geometry and the selected features
        :return:
        """
        self.geometry = None
        self.features.delete()

    @property
    def feature_class(self):
        """
            The feature class corresponding to the instance's layer
        :return:
        """
        config_entity = self.__class__.config_entity
        return config_entity.db_entity_feature_class(self.layer.db_entity_key)

    def sync_to_query(self):
        """
            Updates the query_set and related derived values based on the values of the query parameters
        """
        feature_class = self.feature_class
        query_set = self.create_query_set(feature_class.objects)
        # Set the Features to the distinct set. Join queries can result in duplicates of the main model
        self.update_features(query_set and query_set.distinct('pk'))

        # Parse the QuerySet to get the result fields and their column title lookup
        # This will give us the fields of the main model, and if we have joins those of the related models
        regular_query_set = query_set or feature_class.objects
        # Create the values query set if there are joins to handle.
        # If not create the values query set based on the regular query set
        # This function has the side-effect of saving and storing the result_map
        # In the latter case we are just doing calling the function to create the result_map
        values_query_set = self.values_query_set() if\
            self.joins and len(self.joins) > 0 else\
            self.values_query_set(regular_query_set)

        # Save the query for use by the exporter and for debugging
        self.query_sql = str(values_query_set.query)

        # Create the summary results from the entire set
        summary_query_set = self.sync_summary_query_set(feature_class.objects)
        if summary_query_set:
            # Update the summary results
            self.update_summary_results(summary_query_set)
        else:
            self.clear_summary_results()

    def values_query_set(self, query_set=None):
        """
            Returns a ValuesQuerySet based on the query_set and the related_models.
            The given query_set returns Feature class instances. We want the dictionaries with the related models
            joined in
            :param query_set. Optional instance QuerySet to use as the basis for producing the ValueQuerySet.
            If omitted then create_query_set is used to generate it
        """

        feature_class = self.feature_class
        query_set = query_set or self.create_query_set(feature_class.objects)

        # Combine the fields of the join models
        join_models = self.resolve_join_models()
        filtered_fields = limited_api_fields(feature_class)
        is_join_queryset = self.joins and len(self.joins) > 0

        # Limit the returned fields for the main model and related models
        # based on the api_include property on the model. If that property
        # is null, return everything except the wkb_geometry

        def related_field_paths_filter(join_model):
            related_filtered_fields = limited_api_fields(join_model)
            return related_field_paths(
                feature_class.objects,
                join_model,
                for_value_queryset=is_join_queryset,
                field_names=related_filtered_fields,
                excludes=Feature.API_EXCLUDED_FIELD_NAMES if not filtered_fields else [])

        all_field_paths = \
            model_field_paths(
                feature_class,
                for_value_queryset=is_join_queryset,
                field_names=filtered_fields,
                excludes=Feature.API_EXCLUDED_FIELD_NAMES if not filtered_fields else []) + \
            flat_map(
                related_field_paths_filter,
                join_models)

        # Convert the queryset to values with all main and related field paths
        # This makes us lose the model instance
        indistinct_query_set = query_set.values(*all_field_paths)

        # We need the result_map at this point so create it and save the results
        # This is a side effect but all callers need it immediately afterward anyway
        self.result_map = self.create_result_map(indistinct_query_set)

        # Prevent duplicates that occur by joining two feature tables via a primary geography table,
        # since there can be many primary geography features per main feature

        # To limit duplicate checks find the foreign key to each related model in the geographies join table
        # Remove the _id portion since the actual Django field always omits it
        # TODO We can use the following line instead once someone verifies that the only possible values here are
        # _id for non primary geographies and __id for primary geographies
        # lambda attr[:-len('_id')] if not attr.endswith('__id') else attr
        # This corrects the problem that the replace might not replace only at the end of the string
        related_foreign_key_attributes = map(
            lambda attr: attr.replace('_id', '') if not attr.endswith('__id') else attr,
            self.result_map.django_join_model_attributes
        )
        # If we don't have joins, no need for distinct.
        if not is_join_queryset:
            return indistinct_query_set

        # Limit the distinct clause to the pk and the join foreign keys.
        key_attributes = ['pk'] + related_foreign_key_attributes
        return indistinct_query_set.distinct(*key_attributes)

    def resolve_related_model(self, path):
        """
            Given a path that might be for the main or join, this
        :param path:
        :return:
        """
        # TODO this is an empty method...

    def result_field_extra_sql_lookup(self, query_set):
        """
            Returns a lookup that maps some field names to a lambda that describes
            how to create a human readable form of the field value. This is used by the FeatureResource
        :return:
        """
        return dict(select=compact_dict(map_to_dict(
            self.sql_map_lambda(query_set),
            self.result_map.result_fields,
            use_ordered_dict=True
        )))

    def sql_map_lambda(self, query_set):
        field_to_table_lookup = map_to_dict(lambda tup: [tup[1], tup[0]], query_set.query.select)
        def sql_map(path):
            """
                Like field_map, but instead produces a sql version of the mapping.
                Since our export functionality sends sql to ogr, we need to handle
                all the formatting in the sql. We can do this by overriding the normal
                select value with a function (e.g. select updated_date becomes select format(update_data).
                In order to do this we create an extra clause for the Django QuerySet since it sadly
                doesn't have a built-in ability to decorate selections with functions
            :param path:
            :param field_class_path:
            :return: An array with two values, the path and the mapping. If no mapping
            is needed, an array with [path, path] is returned. This way the path is used as an extra
            value and the column order is preserved. Django nonsensically puts the extra fields before
            the normal fields, even if their names match. Apparently they didn't considered the situation
            of replacing a normal column select with a formatted column select, or they don't expect
            raw sql to be used.
            """

            full_column_name = '%s.%s' % (field_to_table_lookup.get(path), path.split('__')[-1]) if field_to_table_lookup.get(path) else path
            field_class_path = self.result_map.field_lookup.get(path)
            if not field_class_path:
                return None
            resolved_field_class = resolve_module_attr(field_class_path)
            if resolved_field_class and issubclass(resolved_field_class, DateField):
                # Format the date to match our prefered style (gotta love SQL :< )
                return [path,
                        "to_char({0}, 'YYYY-MM-DD') || 'T' || to_char({0}, 'HH:MI:SS') || to_char(extract(TIMEZONE_HOUR FROM {0}), 'fm00') || ':' || to_char(extract(TIMEZONE_MINUTE FROM {0}), 'fm00')".format(full_column_name)]
            return None
        return sql_map

    def create_query_set(self, query_set):
        """
            Creates a QuerySet beginning with the given query_set and apply various filters
        """
        starting_query_set = query_set

        # Filter by bounds if present and selection_options.constrain_to_bounds is True (default True)
        # or if no filters or joins are present (joins are inner joins, so function as filters)
        bounded_query_set = starting_query_set.filter(wkb_geometry__intersects=self.geometry) if \
            self.geometry != DEFAULT_GEOMETRY and (
                self.selection_options.get('constrain_to_bounds', True) or
                not (self.filter or self.joins)) else \
            starting_query_set

        # Filter by filter if present
        if self.filter and self.selection_options.get('constrain_to_query', True):
            # If filters have been specified then perform the query.
            return parse_query(self.config_entity, bounded_query_set, filters=self.filter, joins=self.joins)
        elif self.geometry != DEFAULT_GEOMETRY:
            # Return the result unless neither bounded or filtered.
            # Specifying nothing results in an empty query set (i.e. we don't allow select all)
            return parse_query(self.config_entity, bounded_query_set, joins=self.joins)
        elif self.joins:
            return parse_query(self.config_entity, bounded_query_set, joins=self.joins)
        else:
            query_set.none()

    def sync_summary_query_set(self, query_set):
        if not self.aggregates and not self.group_bys:
            return None

        # Filter by bounds if present
        bounded_query_set = self.feature_class.objects.filter(wkb_geometry__intersects=self.geometry) \
            if self.geometry != DEFAULT_GEOMETRY else query_set

        # If filters have been specified then perform the query.
        return parse_query(self.config_entity, bounded_query_set, filters=self.filter, joins=self.joins,
                           group_bys=self.group_bys, aggregates=self.aggregates)

    def properties_have_changed(self, property_dict, *properties):
        return any_true(lambda property:
                            normalize_null(get_property_path(self, property)) !=
                            normalize_null(get_property_path(property_dict, property)),
                        properties)

    @classmethod
    def post_save(self, user_id, objects, **kwargs):
        """
            This is called after a resource saves a layer_selection. We have no use for it at the moment
        """
        pass


class LayerSelectionFeature(models.Model):
    objects = GeoInheritanceManager()

    # A class name is used to avoid circular dependency
    #layer_selection = models.ForeignKey(LayerSelection, null=False)
    #feature = models.ForeignKey(Feature, null=False)
    #layer_selection = None
    #feature = None
    medium = models.ForeignKey(Medium, null=True, default=None)

    def __unicode__(self):
        return "LayerSelection:{0}, Feature:{1}, Medium:{2}".format(self.layer_selection, self.feature, self.medium)
    class Meta(object):
        app_label = 'main'
        abstract = True


# TODO move this to a LayerSelectCreator class which inherits from DynamicModelClassCreator
def get_or_create_layer_selection_class_for_layer(layer, config_entity=None, no_table_creation=False):
    """
        Generate a subclass of LayerSelection specific to the layer and use it to create a table
    :param layer
    :param config_entity: Defaults to the ConfigEntity that owns the DbEntity of the Layer. This
    should be set explicitly if the LayerSelection is in the context of a lower ConfigEntity, namely
    the active Scenario from the user interface. Setting the ConfigEntity is important if the LayerSelection
    contains a query that joins Feature classes that belong to that lower ConfigEntity
    :param no_table_creation for debugging, don't create the underlying table
    :return:
    """

    config_entity = config_entity or layer.config_entity
    # Name the class based on the optional passed in config_entity so that they are cached as separated classes
    dynamic_class_name = 'LayerSelectionL{0}C{1}'.format(layer.id, config_entity.id)
    try:
        feature_class = config_entity.db_entity_feature_class(layer.db_entity_key)
    except:
        logging.exception('no feature class')
        # For non feature db_entities, like google maps
        return None

    dynamic_through_class = dynamic_model_class(
        LayerSelectionFeature,
        layer.config_entity.schema(),
        'lsf_%s_%s' % (layer.id, layer.db_entity_key),
        class_name='{0}{1}'.format(dynamic_class_name, 'Feature'),
        fields=dict(
            layer_selection=models.ForeignKey(dynamic_class_name, null=False),
            feature=models.ForeignKey(feature_class, null=False),
        )
    )

    # Table is layer specific. Use ls instead of layer_selection to avoid growing the schema.table over 64 characters
    table_name = 'ls_%s_%s' % (layer.id, layer.db_entity_key)
    dynamic_class = dynamic_model_class(
        LayerSelection,
        # Schema is that of the config_entity
        layer.config_entity.schema(),
        table_name,
        class_name=dynamic_class_name,
        # The config_entity instance is a class attribute
        # This config_entity can be a child of the layer.config_entity if we need the
        # dynamic class to be in the context of a lower ConfigEntity in order to access lower join tables in its query
        class_attrs=dict(
            config_entity__id=config_entity.id,
            layer__id=layer.id,
            override_db=config_entity.db
        ),
        related_class_lookup=dict(
            config_entity='footprint.main.models.config.config_entity.ConfigEntity',
            layer='footprint.main.models.presentation.layer.layer.Layer'
        ),
        fields=dict(
            features=models.ManyToManyField(feature_class, through=dynamic_through_class, related_name=table_name)
        )
    )

    # Make sure the tables exist
    if not no_table_creation:
        create_tables_for_dynamic_classes(dynamic_class, dynamic_through_class)

    return dynamic_class

def get_or_create_layer_selection_class_for_feature_class(feature_class, no_table_creation=False):
    """
        Gets the layer_selection class for the given feature class
    :param feature_class:
    :param no_table_creation:
    :return:
    """
    config_entity = feature_class.config_entity
    db_entity_key = feature_class.db_entity_key
    layer = Layer.objects.get(db_entity_key=db_entity_key, config_entity=config_entity)
    return get_or_create_layer_selection_class_for_layer(layer, config_entity, no_table_creation=no_table_creation)

def drop_layer_selection_table(layer_selection_class):
    """
        Drop the dynamic LayerSelection class table. This should be called whenever the owning layer is deleted
    :param layer_selection_class:
    :return:
    """
    if InformationSchema.objects.table_exists(*parse_schema_and_table(layer_selection_class._meta.db_table)):
        drop_tables_for_dynamic_classes(layer_selection_class)

def layer_selections_of_config_entity(config_entity):
    """
        Returns all LayerSelection instances of the ConfigEntity
    :param config_entity:
    :return:
    """
    return flat_map(
        lambda layer: list(get_or_create_layer_selection_class_for_layer(layer, config_entity, no_table_creation=True)),
        Layer.objects.filters(config_entity=config_entity))
