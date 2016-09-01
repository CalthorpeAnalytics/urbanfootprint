
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

from datetime import datetime
import string
import sys

from django.db.models import Q, Min, Count, F, DateTimeField, DateField, TimeField
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date, parse_time

from footprint.main.lib.functions import to_list, map_to_dict, first, compact
from footprint.main.utils.model_utils import resolve_db_entity_key_of_field_path, \
    resolve_field_of_path, resolve_queryable_name_of_type, field_predicate, index_of_field_for_sort, \
    _field_path_and_cloned_field
from footprint.main.utils.utils import clear_many_cache

logger = logging.getLogger(__name__)

COMPARISON_LOOKUP = {
    '<': 'lt',
    '<=': 'lte',
    '>': 'gt',
    '>=': 'gte',
    'BEGINS_WITH': 'startswith',
    'ENDS_WITH': 'endswith',
    'CONTAINS': 'contains' # TODO would be 'in' for SC Arrays
    #'MATCHES':
    #'ANY':
    #TYPE_IS -
}

ARITHMETIC_LOOKUP = {
    '+':'+',
    '-':'-',
    '*':'*',
    '/':'/',
    '**':'**',
    '^':'**'
}


def parse_query(config_entity, manager, filters=None, joins=None, aggregates=None, group_bys=None):
    queryset = manager
    group_by_values = None
    annotation_tuples = None

    # Make sure all related models have been created before querying
    from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
    FeatureClassCreator(config_entity).ensure_dynamic_models()

    # Any joins are db_entity_keys and resolve to feature classes of the config_entity
    related_models = map(lambda join: config_entity.db_entity_feature_class(join), joins or [])

    # Use group_by_values to group by and then attach the aggregates to each unique result via annotation
    # If aggregates are specified but group by is not, we use aggregate to just get a single result
    # For now we assume any filtering should be applied BEFORE aggregation
    if filters:
        queryset = queryset.filter(parse_token(filters, manager, related_models))

    # We only need to join explicitly if the join is not included in one of the group by fields
    manual_joins = joins or [] if not group_bys else \
        set(joins or [])-\
        set(map(lambda group_by: resolve_db_entity_key_of_field_path(parse_group_by(group_by, manager, related_models), manager, related_models), group_bys))

    if manual_joins:
        # If there are joins, filter the queryset by inner join on the related_model pk through geography
        for related_model in related_models:
            related_field_pk_path = resolve_field_path_via_geographies('pk', manager, [related_model])
            queryset = queryset.filter(**{'{0}__isnull'.format(related_field_pk_path):False})

    # If there are aggregates, they are either part of the main table or join table
    if aggregates:
        # Resolve the field path using available joins via geographies or on the main model
        # Then send the resolved field
        annotation_tuples = map(
            lambda aggregate: parse_annotation(aggregate, manager, related_models),
            aggregates)

    if group_bys:
        group_by_values = map(
            lambda group_by: parse_group_by(group_by, manager, related_models),
            to_list(group_bys))

        annotation_tuples = annotation_tuples or []
        # Add a Count to the selection if one isn't present
        if not first(lambda annotation_tuple: Count==annotation_tuple[0], annotation_tuples):
            annotation_tuples.insert(0, (Count, group_by_values[0], 'count'))

        # TODO. We might have to do rounding of floats here using an extra clause:
        # extra(select={'custom_field': 'round(field, 2)'})
        queryset = queryset.values(*group_by_values).order_by(*group_by_values)
    elif annotation_tuples:
        # If there are annotations but no group_bys, we need to fake a group by annotating
        # the count of the pk to each row and then grouping by it. Since every row
        # has one pk all the rows group together
        # Otherwise we'd have to use the aggregate function which doesn't give us
        # a query back
        queryset = queryset.annotate(count=Count('pk')).values('count')

    if annotation_tuples:

        for annotation_tuple in annotation_tuples:
            # Annotation built-in functions or custom functions of the queryset (like geo stuff)
            annotate_method = getattr(queryset, annotation_tuple[0]) if\
                isinstance(annotation_tuple[0], basestring) else\
                annotation_tuple[0]

            if len(annotation_tuple)==3:
                # Apply alias if specified
                queryset = queryset.annotate(**{annotation_tuple[2]:annotate_method(annotation_tuple[1])})
            else:
                # Otherwise default the name to the field
                queryset = queryset.annotate(annotate_method(annotation_tuple[1]))

    elif group_by_values:
        # If no annotations are specified, add in a count annotation to make the group by take effect
        # As long as we annotate a count of one we'll get the correct group_by, since django receives values(group_by1, group_by2, etc).annotate(count(group_by1))
        queryset = queryset.annotate(count=Count(group_by_values[0]))

    return queryset

def is_aggregate(annotation_function):
    #TODO
    return False



def parse_group_by(group_by_token, manager, related_models):
    """
    :param group_by_token:
    :return:
    """
    # Pretend the group_by token is a left side value so that we don't ever create an F() statement
    return parse_simple_token(group_by_token, manager, related_models, left=True)

def parse_annotation(aggregate_token, manager, related_models):
    """
        token in the form {rightSide: {tokenValue: field_name}, tokenValue: 'AVG|SUM|COUNT'}
    :param aggregate_token:
    :param manager: main Manager
    :param related_models: related models
    :return: A tuple of the aggregate function to be passed to annotate()  and the resolved field path
    """
    function_or_name = resolve_annotation(manager, aggregate_token['tokenValue']) if aggregate_token.get('tokenValue', None) else None
    # Parse the rightSide as a left side token to parse just the argument of the aggregate function as a literal field
    resolved_field_path = parse_simple_token(aggregate_token['rightSide'] if 'rightSide' in aggregate_token else aggregate_token['tokenValue'],
                                             manager,
                                             related_models,
                                             left=True)
    return (function_or_name, resolved_field_path) if function_or_name else resolved_field_path

def parse_token(token, manager, related_models, left=False, sibling_token=None):

    token_type = token['tokenType']
    left_side = token.get('leftSide', None)
    right_side = token.get('rightSide', None)

    if token_type == 'AND':
        left_side_result = parse_token(left_side, manager, related_models)
        right_side_result = parse_token(right_side, manager, related_models)
        return left_side_result & right_side_result
    elif token_type == 'OR':
        left_side_result = parse_token(left_side, manager, related_models)
        right_side_result = parse_token(right_side, manager, related_models)
        return left_side_result | right_side_result
    # TODO handle NOT with ~Q()
    elif token_type in COMPARISON_LOOKUP.keys():
        left_side_result = parse_token(left_side, manager, related_models, left=True)
        return Q(**{'{0}__{1}'.format(left_side_result, COMPARISON_LOOKUP[token_type]):
                    parse_token(right_side, manager, related_models, sibling_token=left_side)})
    elif token_type == '=':
        return Q(**{parse_token(left_side, manager, related_models, left=True):
                    parse_token(right_side, manager, related_models, sibling_token=left_side)})
    elif token_type == '!=':
        return ~Q(**{parse_token(left_side, manager, related_models, left=True):
                    parse_token(right_side, manager, related_models, sibling_token=left_side)})
    # TODO handle other operators
    elif token_type in ARITHMETIC_LOOKUP.keys():
        # TODO untested
        return eval('parse_token(left_side, manager, related_models)' +
                    'token_type' +
                    'parse_token(right_side, manager, related_models)')

    # If the token type isn't a complex operator, assume it's a primitive
    return parse_simple_token(token, manager, related_models, left=left, sibling_token=sibling_token)


def parse_simple_token(token, manager, related_models, left=False, sibling_token=None):
    """
        Parse the simple token dict.
        :param token: a dict with 'tokenType'=='PROPERTY'|'NUMBER'|'STRING'
            and 'tokenValue'==a value of the corresponding type.
        :param manager: The django model manager
        :param related_models: Related models joined to the manager model
        :param left: Default False. If set then the token is an assignee and shouldn't be wrapped in
        an F() expression if it's a property
        :param sibling_token: the left side token if we are evaluating a right side token (left=False)
    """
    if token['tokenType'] == 'PROPERTY':
        # Resolve the field path in case it's relative to a joined related_model
        field_path = resolve_field_path_via_geographies('__'.join(token['tokenValue'].split('.')), manager, related_models)
        # Wrap in an F() expression if field is a right-side argument (the thing being assigned)
        return field_path if left else F(field_path)
    elif token['tokenType'] == 'NUMBER':
        return float(token['tokenValue'])
    elif token['tokenType'] in ['STRING', 'null', 'undefined']:
        if token['tokenType'] in ['null', 'undefined']:
            # Accept the 'null' or 'undefined' tokenType to mean None
            value = None
        else:
            value = token['tokenValue']

        if sibling_token and sibling_token.get('tokenType', None) == 'PROPERTY':
            # If we are evaluating a right-side token, inspect the sibling_token (the left-side token)
            # to find out what type the property is. This only matters for Dates and Times
            # where we need to modify the resolved right-side value to be have a time zone
            # if one isn't specified

            # Resolve the possibly chained property
            field_path = resolve_field_path_via_geographies('__'.join(sibling_token['tokenValue'].split('.')), manager, related_models)
            field = resolve_field_of_path(manager, field_path)
            if not field:
                return

            parser_lookup = {DateTimeField: parse_datetime, DateField: parse_date, TimeField: parse_time}
            if isinstance(field, (DateTimeField, DateField, TimeField)):
                date_time = parser_lookup[field.__class__](value)
                if not date_time and isinstance(field, DateTimeField):
                    # Accept dates without times for datetimes
                    date_time = timezone.utc.localize(datetime.combine(parser_lookup[DateField](value), datetime.min.time()))
                if isinstance(field, (DateTimeField, TimeField)) and not date_time.tzinfo:
                    # Default the timezone to UTC
                    return date_time.replace(tzinfo=timezone.utc)
                return date_time
        return value

    # TODO handle booleans and other types
    return token['tokenType']



def resolve_annotation(manager, annotation):
    class_name = annotation.lower().capitalize()
    if hasattr(sys.modules['django.db.models'], class_name):
        return getattr(sys.modules['django.db.models'], class_name)
    function_name = slugify(annotation.lower())
    if hasattr(manager, function_name):
        return function_name


def annotated_related_feature_class_pk_via_geographies(manager, config_entity, db_entity_keys):
    """
        To join a related model by geographic join
    """
    from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
    feature_class_creator = FeatureClassCreator.from_dynamic_model_class(manager.model)

    def resolve_related_model_pk(db_entity_key):
        related_model = config_entity.db_entity_feature_class(db_entity_key)
        # The common Geography class
        geography_class = feature_class_creator.common_geography_class(related_model)
        geography_scope = feature_class_creator.common_geography_scope(related_model)
        logger.warn("Resolved geography scope %s", geography_scope)
        # Find the geographies ManyToMany fields that relates this model to the related_model
        # via a Geography class. Which geography class depends on their common geography scope
        geographies_field = feature_class_creator.geographies_field(geography_scope)
        try:
            # Find the queryable field name from the geography class to the related model
            related_model_geographies_field_name = resolve_queryable_name_of_type(geography_class, related_model)
        except:
            # Sometimes the geography class hasn't had its fields cached properly. Fix here
            clear_many_cache(geography_class)
            related_model_geographies_field_name = resolve_queryable_name_of_type(geography_class, related_model)

        return '%s__%s__pk' % (geographies_field.name, related_model_geographies_field_name)

    pk_paths = map_to_dict(lambda db_entity_key:
        [db_entity_key, Min(resolve_related_model_pk(db_entity_key))],
        db_entity_keys)

    return manager.annotate(**pk_paths)

def resolve_field_path_via_geographies(field_path, manager, related_models):
    """
        Resolve the given field path in case its not absolute.
        For instance, if it is 'block' and one of our related models accessible via geographies__relatedmodel has that property,
        return 'geographies_[scope_id]__relatedmodel__block'
        It will also be tested against the main manager after all related models fail,
        e.g. manager.values(field_path) if successful would simply return field_path
    :param field_path: django field path. e.g. du or built_form__name
    :param manager: The main manager by which the related models are resolved and by which the full path is computed
    :param related_models: models joined to the manager. For instance. manager.model is CanvasFeature, a related_model could be
        CensusBlock, which might be related to the former via 'geographies_[scope_id]__censusblock9rel'. The relationship is computed
        by assuming that the related model is related by geographies and looking for a field matching its type
    :return:
    """
    from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
    feature_class_creator = FeatureClassCreator.from_dynamic_model_class(manager.model)
    for related_model in related_models:
        try:
            # See if the field_name resolves
            # There's probably a more efficient way to do this
            related_model.objects.values(field_path)
            resolved_field_path = field_path
        except:
            # See if the first segment matches the related_model db_entity_key
            first_segment = field_path.split('__')[0]
            if first_segment != related_model.db_entity_key:
                # If not, move on
                continue
            # Take all but the first segment
            resolved_field_path = '__'.join(field_path.split('__')[1:])
        # Success, find the path to this model from geographies
        geography_class = feature_class_creator.common_geography_class(related_model)
        geographies_field = feature_class_creator.geographies_field(feature_class_creator.common_geography_scope(related_model))
        geography_related_field_name = resolve_queryable_name_of_type(geography_class, related_model)
        return '%s__%s__%s' % (geographies_field.name, geography_related_field_name, resolved_field_path)
    # See if it matches the main model
    try:
        if field_path.split('__')[0] == manager.model.db_entity_key:
            # If the manager model db_entity_key was used in the path, just strip it out
            updated_field_path = '__'.join(field_path.split('__')[1:])
            manager.values(updated_field_path)
        else:
            # Otherwise test query with the full path
            updated_field_path = field_path
            manager.values(updated_field_path)
        # Success, return the field_path
        return updated_field_path
    except:
        logger.exception('Cannot resolve field path %s to the main model %s or any joined models %s',
                          field_path, manager.model, related_models)
        raise

def resolve_related_model_path_via_geographies(manager, related_model):
    """
        Returns the query string path 'geographies_[scope_id]__[field name of the related model form the main model]'
        The scope_id is the id of the ConfigEntity that both models share in common by ascending the ConfigEntity
        hierarchy starting at each models' geography_scope
    """
    from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
    feature_class_creator = FeatureClassCreator.from_dynamic_model_class(manager.model)
    geography_scope = feature_class_creator.common_geography_scope(related_model)
    geographies_field = feature_class_creator.geographies_field(geography_scope)
    geography_class = feature_class_creator.common_geography_class(related_model)
    geography_related_field_name = resolve_queryable_name_of_type(geography_class, related_model)
    return '%s__%s' % (geographies_field.name, geography_related_field_name)


def related_field_paths(manager, related_model, exclude_field_types=(), field_names=None, excludes=[], separator=None, for_value_queryset=False):
    """
        Iterates through the fields of the related model, appending each to the related model field name
        from the main model. Returns the list of related field paths.

        if for_values_query_set=True, we use attname instead of the name of the field. This gives us the _id version of Foreign keys,
        which is what we want assuming we're created a values_query_set, since the the value will always
        be the related instance id and not the instance itself
    """
    related_field = resolve_related_model_path_via_geographies(manager, related_model)
    return compact(map(
        lambda field: string.replace(
            '{0}__{1}'.format(related_field, field.attname if for_value_queryset else field.name),
            '__',
            separator or '__') if \
                field_predicate(field, exclude_field_types, field_names, excludes) else \
                None,
        # Sort by the field's position in fields if fields is defined
        sorted(
            related_model._meta.fields,
            key=index_of_field_for_sort(field_names, for_value_queryset)
    )))

def related_field_paths_to_fields(manager, related_model, exclude_field_types=(), fields=None, excludes=[], separator=None):
    """
        Iterates through the fields of the related model, appending each to the related model field name
        from the main model. Returns the dict of related field paths as keys valued by the field.
        :param exclude_field_types. Optional tuple of Field classes that should be filtered out.
        :param separator: Optional separator with which to replace __ in the related_field_paths
    """
    related_field = resolve_related_model_path_via_geographies(manager, related_model)
    return map_to_dict(
        lambda field: _field_path_and_cloned_field(related_field,field, separator) if \
            field_predicate(field, exclude_field_types, fields, excludes) else None,
        related_model._meta.fields)

def related_field_paths_to_fields(manager, related_model, exclude_field_types=(), fields=None, excludes=[], separator=None):
    """
        Iterates through the fields of the related model, appending each to the related model field name
        from the main model. Returns the dict of related field paths as keys valued by the field.
        :param exclude_field_types. Optional tuple of Field classes that should be filtered out.
        :param separator: Optional separator with which to replace __ in the related_field_paths
    """
    related_field = resolve_related_model_path_via_geographies(manager, related_model)
    return map_to_dict(
        lambda field: _field_path_and_cloned_field(related_field,field, separator) if \
            field_predicate(field, exclude_field_types, fields, excludes) else None,
        related_model._meta.fields)
