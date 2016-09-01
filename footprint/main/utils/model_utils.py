
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

from copy import deepcopy
import logging
import string
from django.db.models import F
from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject
import sys
from footprint.main.lib.functions import compact, map_to_dict, get_value_of_first_matching_key
from footprint.main.utils.utils import clear_many_cache

logger = logging.getLogger(__name__)

def model_fields(manager, fields):
    """
        Returns the fields of the main model that are filtered by fields, if specified
    """
    logger.debug("{0}".format(manager.model._meta.fields))

    return filter(lambda field: not fields or field.name in fields, manager.model._meta.fields)



def field_predicate(field, exclude_field_types, fields, excludes):
    return (not fields or field.name in fields) and \
            not isinstance(field, exclude_field_types) and \
            not field.name in excludes

def index_of_field_for_sort(field_names, for_values_queryset):
    """
        Returns the index of the field_name in fields_names. If not present returns sys.maxint for lowest sort priority
    :param field_names: String field names
    :param for_values_queryset: True if we are using a ValuesQuerySet, meaning wee need the field.attname not field.name
    :return: A function returning a value between 0...len(field_names) or sys.maxint
    """
    def sort_priority(field):
        name = field.attname if for_values_queryset else field.name
        return (field_names or []).index(name) if name in (field_names or []) else sys.maxint
    return sort_priority

def model_field_paths(model, exclude_field_types=(), field_names=None, excludes=[], for_value_queryset=False):
    """
        Returns the field names of the main model.
        If for_value_queryset=True, we use attname rather than name for the field so that ForeignKeys return their [related]_id name
        instead of just [related] name.
        Since model_field_paths is used (right now) for value_query_sets, it's not
        useful to get the name of the foreign key field, because the corresponding value will always
        be the id of the related model, not the related model instance. Thus it's more accurate
        to return the _id version, since either way it points at an id. This allows us to construct
        unmodeled join classes.
    """

    # Sort by the field's position in fields if fields is defined
    return compact(map(
        lambda field: (field.attname if for_value_queryset else field.name) if field_predicate(field, exclude_field_types, field_names, excludes) else None,
        sorted(model._meta.fields, key=index_of_field_for_sort(field_names, for_value_queryset))
    ))




def _field_path_and_cloned_field(related_field, field, separator):
    field_path = string.replace('{0}__{1}'.format(related_field, field.name),
                           '__',
                           separator or '__')
    cloned_field = deepcopy(field)
    cloned_field.name = field_path
    cloned_field.null = True
    return [field_path, cloned_field]







def resolve_db_entity_key_of_field_path(field_path_or_f_statement, manager, related_models):

    for related_model in related_models:
        try:
            # See if the field_name resolves
            # There's probably a more efficient way to do this
            related_model.objects.values(field_path_or_f_statement)
            # Success, return the db_entity_key of the related_models
            return related_model.db_entity_key
        except:
            pass
    try:
        # The given value is either a simple field path (e.g. 'foo__bar') or a Django F class instance
        path = field_path_or_f_statement.name if isinstance(field_path_or_f_statement, F) else field_path_or_f_statement
        # If an absolute path, take the first segment and try to resolve it as a db_entity_key
        first_segment = path.split('__')
        try:
            if manager.model.config_entity.computed_db_entities(key=first_segment).count() > 0:
                return first_segment
        except:
            # Must be a main feature class field_path
            return manager.model.config_entity.db_entity_key_of_feature_class(manager.model)
    except:
        raise Exception("Cannot resolve field path %s to the main model %s or any joined models %s" %
                        (path, manager.model, related_models))

def resolve_field_of_path(manager, field_path, return_related_models=False):
    """
        Resolves a field for a manager and field_path that might have __'s indicating relations
    :param manager:
    :param field_path:
    :param return_related_models
    :return: Either the resolved field, or if return_related_models is True this
    instead returns a tuple of the resolve field and the related model, the latter being non-null
    only for foreign key properties or id properties that represent foreign keys
    (e.g. built_form or built_form_id, respectively, would return the tuple
    (ForeignKey, BuiltForm) or (AutoField, BuiltForm), respectively
    """
    parts = field_path.split('__')
    model = manager.model
    related_model = None
    while len(parts) > 0:
        part = parts.pop(0)
        # Each part either results in a model or field. Field is the end-case
        # Work around Django init bug for dynamic models
        clear_many_cache(model)
        model_or_field_tuple = model._meta._name_map.get(part)
        if not model_or_field_tuple:
            # It might be that the part represents the attname of a field, not the field name
            # This is true for ForeignKey relationships
            # Find the matching field, and if found find the related model's id field
            related_field_tuple = get_value_of_first_matching_key(
                lambda name, field: part == field[0].attname if hasattr(field[0], 'attname') else False,
                model._meta._name_map)
            if related_field_tuple:
                model_or_field_tuple = related_field_tuple[0].rel.to._meta._name_map['id']
                related_model = related_field_tuple[0].rel.to
            if not model_or_field_tuple:
                # Something went wrong, give up
                return None
        if isinstance(model_or_field_tuple[0], RelatedField):
            # RelatedField. Recurse unless we are out of parts of the field_path
            if len(parts) > 0:
                # Continue on
                model = model_or_field_tuple[0].rel.to
                continue
            else:
                related_model = model_or_field_tuple[0].rel.to
        elif isinstance(model_or_field_tuple[0], RelatedObject):
            # RelatedObject. Always recurse
            model = model_or_field_tuple[0].model
            continue

        # RelatedField with no parts left or simple Field type
        return model_or_field_tuple[0] if not return_related_models else\
        (model_or_field_tuple[0], related_model or None)

def resolve_field(model_class, field_name):
    """
        Given a model class and a field_name, returns the matching Field instance
    :param model_class:
    :param field_name:
    :return:
    """
    try:
        return filter(lambda field: field.name == field_name, model_class._meta.fields)[0]
    except Exception, e:
        raise Exception("Model class {model_class} has no field {field_name}".format(model_class=model_class, field_name=field_name))

def resolve_field_of_type(model, target_class):
    """
        Given a model class an a target model class for a related field, finds
        the related field with that target model class
    :param model:
    :param target_class:
    :return:
    """
    return filter(lambda field: field.rel and field.rel.to and field.rel.to == target_class,
                  model._meta.fields)[0]

def resolve_queryable_name_of_type(model, target_class):
    results = filter(lambda field: field.rel and field.rel.to and field.rel.to == target_class,
                  model._meta.fields)
    if len(results) == 1:
        return results[0].name
    # Search RelatedObject for a matching model. These are tuples, hence the [0]s
    m2m_results = filter(lambda related_object: related_object[0].model == target_class,
                         model._meta.get_all_related_m2m_objects_with_model())
    if len(m2m_results) == 1:
        return m2m_results[0][0].var_name
    raise Exception("No queryable name matching target_class %s for model %s" % (target_class, model))

def limited_api_fields(model, for_template=False):
    """
    Returs a model's limited api fields or None if it doesn't define  limited_api_fields
    :param model:
    :return:
    """
    return model.limited_api_fields(for_template) if hasattr(model, 'limited_api_fields') and model.limited_api_fields() else None

def form_module_name(module, module_fragment, schema):
    return '%s.%s.%s_%s' % (schema, module, schema, module_fragment) if module else \
        '%s.%s_%s' % (schema, schema, module_fragment)


def model_field_names(model):
    opts = model._meta
    return map(lambda field: field.name, opts.fields + opts.many_to_many)


def field_value(model_instance, field, include_null=False):
    """
        Returns a tuple of the field name and model_instance value of that field if not null, otherwise
        returns null unless include_null=True
    """
    try:
        value = getattr(model_instance, field.name)
        return [field.name, value] if include_null or value else None
    except:
        # Proabably a toOne that isn't accessible yet
        return None


def model_dict(model_instance, include_null=False, include_many=False, omit_fields=[], include_primary_key=False):
    """
        Returns a dict keyed by field name and valued by model_instance's corresponding field value
        Primary keys are not included
        :param model_instance: The model instance
        :param include_null: Default False, set True to return fields that evalate to null
        :param omit_fields: Default [], list fields to omit. This is good if there are fields that throw an
        error if null or are simply unwanted
    """

    if not model_instance:
        return dict()

    opts = model_instance.__class__._meta
    return map_to_dict(lambda field: field_value(model_instance, field, include_null),
                       filter(lambda field: not (field.primary_key and not include_primary_key) and field.name not in omit_fields,
                              opts.fields + (opts.many_to_many if include_many else [])
                       )
    )


def uf_model(model_path):
    return 'footprint.main.models.%s' % model_path


class classproperty(object):
    """
        Creates a @classproperty attribute to access class-scope methods as properties
        http://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python
    """
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
       return self.getter(owner)
