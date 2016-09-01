
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
import string

from django.contrib.gis.db.models import GeoManager
from django.contrib.gis.db.models.query import GeoQuerySet, GeoValuesQuerySet
from django.contrib.gis.geos import Polygon
from django.db import transaction, IntegrityError
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from footprint.main.lib.functions import get_first, compact, flat_map, map_to_dict, map_dict_to_dict, compact_dict, \
    map_dict_first
from footprint.main.utils.model_utils import resolve_field_of_path
from footprint.main.utils.utils import full_module_path

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class GeoInheritanceQuerySetMixin(object):

    def parent_field_names(self, with_id_fields=True):
        """
            The name of the fields that references the parent(s)
            :param with_id_fields: Default True, if False exclude the '*_id' fields from the results
        :return:
        """
        return flat_map(lambda field: [field.name] + ([field.attname] if with_id_fields else []), self.model._meta.parents.values())

    def field_names_to_omit_from_query_values(self, related_models=[]):
        """
            Returns all field names related to table inheritance. We don't want these to show up
            in the query results
        :param related_models:
        :return:
        """
        from footprint.main.models.geospatial.feature import Feature
        return \
            Feature.API_EXCLUDED_FIELD_NAMES + \
            self.parent_field_names() + \
            map(lambda field: field.name,
                flat_map(
                   lambda related_model: related_model._meta.parents.values(),
                   related_models)
            )

    def model_result_paths(self, related_models):
        """
            Finds all paths of the model and given related_models that should be returned as fields
            of the query
        """
        # Find the feature_class parent field so we can remove it from the result fields.
        omit_fields_names = self.field_names_to_omit_from_query_values(related_models)
        # Call query_result.values() to gain access to the field names.
        values_query_set = self if hasattr(self, 'field_names') else self.values()
        result_paths = filter(lambda field_name: field_name not in omit_fields_names, values_query_set.field_names)
        return result_paths

    def model_result_field_path_field_lookup(self, related_models, return_related_models=False):
        """
            Returns a mapping of each result_path from the query to its field class (in string form)
        :param related_models: The models related to the main model by a many-to-many relationship.
        For Feature classes this relationship is through the geographies many-to-many, but it
        could be a direct many-to-many
        :param return_related_models: Default False, if True make the returned lookup value a
        tuple. The first item is the field class path and the second is the related model
        for field that are ForeignKeys or AutoField. This is used for JoinFeature queries
        to resolve foreign key ids to its related model class, since the related model is not
        available in the query results or values() (join) queries
        :return: Two items to form a key/value of the dict. The first ist the field_path.
        The second is field class path or (if return_related_models is True)
        the field class path and the related model class path
        """
        def map_result_path(field_path):
            # Get the field and the optional related model
            field, related_model = resolve_field_of_path(self, field_path, True)
            field_class_path = full_module_path(field.__class__)
            # Return
            return [field_path,
                    field_class_path if\
                        not return_related_models else\
                        (field_class_path, full_module_path(related_model) if related_model else None)]


        return map_to_dict(
            map_result_path,
            self.model_result_paths(related_models))

    def create_result_map(self, related_models=[], map_path_segments={}):
        """
            Given the field_paths of the queryset, returns a ResultMap instance.
            ResultMap.result_fields is a list of field_paths minus specifically omitted ones--
            the parent id and geometry column.
            ResultMap.title_lookup is a lookup from the field_path to a title appropriate for the user.
            The generated title uses '.' in place of '__'
            ResultMap.value_map is a lookup from the field_path to a property path that describes
            how to convert the value to a more human readable form. This is used to convert
            instances to a readable label and dates, etc, to a more readable format.
            :param: related_models: pass the related_models represented in the query results so that unneeded
            paraent reference fields can be removed from the result fields
            :param: map_path_segments: An optional dict that matches segments of the field_paths. The value
            corresponding the key is the name to convert it to for the title. If the value is None it will
            be eliminated from the path when it is rejoined with '.'
        """

        result_paths = self.model_result_paths(related_models)
        # Get a mapping of the each result field_path to its field class path along
        # with the related model of that field, if the field is a ForeignKey or AutoField
        result_field_path_lookup = self.model_result_field_path_field_lookup(related_models, True)
        join_models = map(lambda model: full_module_path(model.__base__), related_models)
        return ResultMap(
            # Replace '__' with '_x_'. We can't use __ because it confuses tastypie
            result_fields=map(lambda path: string.replace(path, '__', '_x_'), result_paths),
            # Create a lookup from field name to title
            # The only processing we do to the title is to remove the middle path
            title_lookup=map_to_dict(
                lambda path: [
                    # Replace '__' with '_x_'. We can't use __ because it confuses tastypie
                    string.replace(path, '__', '_x_'),
                    # match each segment to map_path_segments or failing that return the segment
                    # remove segments that map to None
                    '__'.join(compact(
                        map(
                            lambda segment: map_path_segments.get(segment, segment),
                            path.split('__')
                        )
                    ))
                ],
                result_paths
            ),
            field_lookup=map_dict_to_dict(lambda field_path, tup: [field_path, tup[0]], result_field_path_lookup),
            related_model_lookup=compact_dict(map_dict_to_dict(lambda field_path, tup: [field_path, tup[1]], result_field_path_lookup)),
            join_models=join_models,

        )

    def extent_polygon(self):
        """
            Convert extent into something more useful--a simple geos polygon
        """
        try:
            # This seems to raise if no rows exist
            extent = self.extent()
        except:
            return None
        bounds = Polygon((
            (extent[0], extent[1]),
            (extent[0], extent[3]),
            (extent[2], extent[3]),
            (extent[2], extent[1]),
            (extent[0], extent[1]),
        ))
        return bounds


class GeoInheritanceValuesQuerySet(GeoValuesQuerySet, GeoInheritanceQuerySetMixin):
    pass

class GeoInheritanceQuerySet(GeoQuerySet, InheritanceQuerySet, GeoInheritanceQuerySetMixin):
    def values(self, *fields):
        return self._clone(klass=GeoInheritanceValuesQuerySet, setup=True, _fields=fields)



class FootprintGeoManager(GeoManager):
    # http://djangosnippets.org/snippets/1114/
    def update_or_create(self, **kwargs):
        """
            updates, creates or gets based on the kwargs. Works like get_or_create but in addition will update
            the kwargs specified in defaults and returns a third value to indicate if an update happened
        :param kwargs:
        :return:
        """
        assert kwargs, 'update_or_create() must be passed at least one keyword argument'
        obj, created = self.get_or_create(**kwargs)
        defaults = kwargs.pop('defaults', {})
        if created:
            return obj, True, False
        else:
            try:
                needs_save = False
                params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
                params.update(defaults)
                for attr, val in params.items():
                    if hasattr(obj, attr):
                        setattr(obj, attr, val)
                # sid = transaction.savepoint()
                obj.save(force_update=True)
                # transaction.savepoint_commit(sid)
                return obj, False, True
            except IntegrityError, e:
                # transaction.savepoint_rollback(sid)
                try:
                    return self.get(**kwargs), False, False
                except self.model.DoesNotExist:
                    raise e

    # Update the related instance or add it. The toMany equivalent to update_or_create
    def update_or_add(self, **kwargs):
        assert kwargs, 'update_or_add() must be passed at least one keyword argument'
        defaults = kwargs.pop('defaults', {})
        obj = get_first(self.filter(**kwargs))
        result = (obj, False, True)
        create = False
        if not obj:
            obj = self.model()
            result = (obj, True, False)
            create = True
        try:
            params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
            params.update(defaults)
            for attr, val in params.items():
                if hasattr(obj, attr):
                    setattr(obj, attr, val)
            sid = transaction.savepoint()
            obj.save(force_update=not create)
            if not create:
                self.add(obj)
            transaction.savepoint_commit(sid)

            return result
        except IntegrityError, e:
            transaction.savepoint_rollback(sid)

class GeoInheritanceManager(FootprintGeoManager, InheritanceManager):
    """
        Combines the GeoManager and Inheritance Managers into one. The get_query_set is overridden below to return a
        class that combines the two QuerySet subclasses
    """

    def get_query_set(self):
        return GeoInheritanceQuerySet(self.model)

    def __getattr__(self, attr, *args):
        """
            Pass unknown methods to the QuerySetManager
        :param attr:
        :param args:
        :return:
        """
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class ProxyGeoInheritanceManager(GeoInheritanceManager):
    """
        Identical to GeoInheritanceManager, but limits the queryset to the passed in query params
        This is used for Proxy models that distinguish their rows in the table with a filter (e.g. key='core')
    """
    def __init__(self, **filter):
        self.filter = filter
        super(ProxyGeoInheritanceManager, self).__init__(self)

    def get_query_set(self):
        return super(ProxyGeoInheritanceManager, self).get_query_set().filter(**self.filter)

class ResultMap(dict):

    def __init__(self, result_fields, title_lookup, field_lookup, related_model_lookup, join_models):
        self['result_fields'] = result_fields
        self['title_lookup'] = title_lookup
        self['field_lookup'] = field_lookup
        self['related_model_lookup'] = related_model_lookup
        self['join_models'] = join_models
        # Create a list of the attributes that correspond to the join_models so we can resolve foreign keys
        # on each JoinFeature (These will look like geographies_3__countyboundary10rel__countyboundary10_ptr_id)
        # Note that if a join_model is the primary geography, it won't match anything in related_model_lookup,
        # hence we use compact to remove None from the results. It isn't needed in the join_model_attributes.
        self['django_join_model_attributes'] = compact(map(
                lambda model_path: map_dict_first(
                    lambda key, value: key if value == model_path else None,
                    related_model_lookup),
                join_models))
        # Map each join model attribute to the _x_ format like result_fields
        # We use these in the distinct clause of the query to get just primary key fields or their join model
        # foreign key equivalents
        self['join_model_attributes'] = map(
            lambda path: string.replace(path, '__', '_x_'),
            self.django_join_model_attributes)

    def __getattr__(self, attr):
        return self[attr] if attr in self else super(ResultMap, self).__getattr__(attr)
