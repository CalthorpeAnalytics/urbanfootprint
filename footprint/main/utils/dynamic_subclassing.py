
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
import string

from django.contrib.admin.sites import AlreadyRegistered
from django.db import transaction
from django.contrib import admin
from south.db import db
from django.db import models, DatabaseError
from django.db.models.signals import class_prepared
from tastypie.resources import ModelDeclarativeMetaclass
from footprint.main.lib.functions import merge, map_to_dict
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
# Creates a model based on the given abstractClass and customTable name
# This allows us to map dynamically created tables such as those in the inputs_outputs_* schemas
from footprint.main.models.database.information_schema import InformationSchema
from footprint.main.utils.model_utils import resolve_field_of_type
from footprint.main.utils.utils import parse_schema_and_table, resolve_model, resolve_module_attr, resolvable_module_attr_path

logger = logging.getLogger(__name__)

def resolve_dynamic_model_class(base_class, class_name=None, scope=None):
    """
        Finds the dynamic model class if it already exists
    :param base_class: The base class
    :param class_name: Precomputed class_name if it exists, otherwise based on the scope and base_class
    :param scope: another model instance containing an id to use to scope this class
    :return:
    """
    computed_name = class_name or get_dynamic_model_class_name(base_class, scope.id if isinstance(scope, models.Model) else scope or '')
    # Return the model class if already created
    return resolve_model('main.%s' % computed_name)

def dynamic_model_class(base_class, schema, table, class_name=None, class_attrs={}, fields={}, scope=None, related_class_lookup={}, is_managed=True, cacheable=True):
    """
    :param base_class: The class to subclass. This doesn't have to be abstract and could simply be object
    :param schema: The schema of the table.
    :param table: The table name. Used for Meta.db_table
    :param class_name: The name to use for the class. If not specified the name will be formed from the table_name
    :param class_attrs: Nonmodel attributes to add to the subclass
    :param fields: Model fields to add to the subclass, such as ForeignKey, ManyToMany, etc
    :param scope: Optional. A model instance which represents the scope of this subclass. The id is used to form the class name
    :param related_class_lookup: used in conjunction with class_attrs with the form attr__id. For instance, if a class_attr config_entity__id
    :param is_managed: default True, set False to create an unmanaged Django class
    with value 56 is specified, related_class_lookup will be dict(config_entity='footprint.main.models.config.ConfigEntity') to
    specify what model class resolved the related id. The class then gets a getter property that returns the resolved version of the id.
    This is all to prevent storing the instance as a class attr, which is expensive to pickle elsewhere in the system.
    class called config_entity which uses the id stored in
    :return:
    """

    resolved_model = resolve_dynamic_model_class(base_class, class_name, scope) if cacheable else None
    if resolved_model:
        return resolved_model

    computed_name = class_name
    if not computed_name:
        if isinstance(scope, models.Model):
            scope = scope.id
        else:
            scope = scope or ''
        computed_name = get_dynamic_model_class_name(base_class, scope)

    # Source: http://stackoverflow.com/questions/1735434/class-level-read-only-properties-in-python
    # We want do create properties scoped to the class below, but classes by default just return the Property object
    # itself. This chnages that behavior
    class ClassProperty(property):
       def __get__(self, cls, owner):
           return self.fget.__get__(None, owner)()

    class FootprintMetaclass(type(base_class)):
        """Create a metaclass that overrides the name of the class it creates based on the given table name"""
        def __new__(meta, name, bases, attrs):
            # Register any additional model fields specified in fields
            def add_field(sender, **kwargs):
                if sender.__name__ == computed_name:
                    for field_name, field in fields.items():
                        field.contribute_to_class(sender, field_name)
            class_prepared.connect(add_field)

            def create_class_property(class_attr):
                related_attr = class_attr.split('__')[0]
                related_class_name = related_class_lookup.get(related_attr, None)
                if not related_class_name:
                    raise Exception("Expected related_class_lookup to contain %s, since class_attrs contain %s" % (related_attr, class_attr) )
                related_class = resolve_module_attr(related_class_name)
                # Create the getter property that uses the class manager to lookup up the related model by id
                def getter(cls):
                    return related_class.objects.get(id=getattr(cls, class_attr))
                return ClassProperty(classmethod(getter))

            # Create class-level getter properties to resolve things like the config_entity since we only store the id
            class_properties = map_to_dict(
                lambda class_attr: [class_attr.split('__')[0], create_class_property(class_attr)],
                filter(lambda class_attr: class_attr.endswith('__id'), class_attrs))

            return models.base.ModelBase.__new__(
                meta,
                computed_name,
                (base_class,),
                # Merge the manager objects (if the abstract_class has one) with attrs and class_attrs
                merge(dict(objects=base_class.objects.__class__()) if hasattr(base_class, 'objects') else {},
                      attrs,
                      class_attrs,
                      class_properties))


    # Create the custom class using the configured meta class
    class GenericModelClass(object):
        __metaclass__ = FootprintMetaclass

        objects = GeoInheritanceManager()

        class Meta:
            # Set the table name
            db_table = '"{0}"."{1}"'.format(schema, table)
            app_label = 'main'
            managed = is_managed

    try:
        admin.site.register(GenericModelClass)
    except AlreadyRegistered, e:
        logger.warn("Attempt to register class after initialize registration %s", GenericModelClass)

    return GenericModelClass

def get_dynamic_resource_class(super_class, model_class, fields={}, meta_fields={}):
    """
        Subclass the super_class and change the queryset to the model_class's and abstract to False
    :param super_class: The Resource class to subclass
    :param model_class: The concrete subclassed model class which we want the subclassed Resource class to query
    :param fields: Additional fields to give the class.
    :param meta_fields: Additional meta fields, such as fields or excludes. You can also pass
    a query_set here to use something more specific than the model_class's default QuerySet
    :return:
    """
    class_name = get_dynamic_resource_class_name(super_class, model_class)
    if not meta_fields.get('queryset'):
        # Find the matching resource in the cache if there are no meta_fields that would mutate it
        # Return the class if it was already created
        modname = globals()['__name__']
        existing_class = resolve_module_attr('%s.%s' % (modname, class_name))
        if existing_class:
            return existing_class

    logger.info("Creating Resource Class %s for model class %s with the super class %s" % (class_name, model_class.__name__, super_class.__name__))
    queryset = model_class.objects.all()
    meta_attributes = merge(dict(queryset=queryset, abstract=False), meta_fields)
    meta_class = type('Meta', (super_class.Meta,), meta_attributes)
    resource_attributes = dict(Meta=meta_class, **fields)
    resource_class = ModelDeclarativeMetaclass(class_name, (super_class,), resource_attributes)
    return resource_class

def dynamic_model_table_exists(model_class):
    #logger.debug('Checking model class table {model_class} exists'.format(model_class=model_class._meta.db_table))
    return InformationSchema.objects.table_exists(*parse_schema_and_table(model_class._meta.db_table))

# From http://dynamic-models.readthedocs.org/en/latest/topics/database-migration.html#topics-database-migration
def create_tables_for_dynamic_classes(*model_classes):
    """
        Creates the table for the dynamic model class if needed
    :param model_classes: 0 or more model classes for which to create a table
    :return:
    """
    for model_class in model_classes:
        if dynamic_model_table_exists(model_class):
            continue

        #info = "Model class table {model_class} doesn't exist -- creating it \n"
        #logger.debug(info.format(model_class=model_class._meta.db_table))

        fields = [(f.name, f) for f in model_class._meta.local_fields]
        table_name = model_class._meta.db_table
        db.create_table(table_name, fields)

        # some fields (eg GeoDjango) require additional SQL to be executed
        # Because of the poor Django/GeoDjango support for schemas, we have to manipulate the GeoDjango sql here so that the table is resolved to the correct schema, sigh
        if len(table_name.split('.'))==2:
            schema, table = parse_schema_and_table(table_name)
            for i, sql in enumerate(db.deferred_sql):
                # Replace the POSTGIS single argument with two arguments
                # TODO this stupidly assumes that all deferred sql is POSTGIS
                # Substitution for '"schema"."table"' to 'schema','table'. This is for AddGeometryColumn
                db.deferred_sql[i] = re.sub("'{0}'".format(table_name), "'{0}','{1}'".format(schema, table), sql)
                # Substitution for "schema"."table" to schema.table. This is for CREATE INDEX
                db.deferred_sql[i] = re.sub("{0}".format(table_name), "{0}.{1}".format(schema, table), db.deferred_sql[i])
                # Substitution for "schema"."tableHEX". Some indexes add random hex to the table name inside the double quotes. They may also truncate the table name, so just capture everything between "s
                # Also truncate to 64 characters the schema name minus the length of the table name, favoring the end of the schema which is most unique
                db.deferred_sql[i] = re.sub(r'"(".*)"\."(.*") ON', r'\1.\2 ON'.format(schema, table), db.deferred_sql[i])
                # Last ditch effort to remove extra " when we can't match generated index
                db.deferred_sql[i] = re.sub(r'""', r'"', db.deferred_sql[i])
                if string.find(db.deferred_sql[i], 'CREATE INDEX') == 0:
                    subs = db.deferred_sql[i]
                    # Truncate the index name. This could be done more elegantly
                    db.deferred_sql[i] = subs[0:14] + subs[14:string.index(subs, '" ON')][-63:] + subs[string.index(subs, '" ON'):]

        try:
            db.execute_deferred_sql()
        except Exception, e:
            raise Exception("The table {table_name} was not created. Original exception: {message}. Deferred sql calls: {sql}".format(table_name=model_class._meta.db_table, message=e.message, sql='\n'.join(db.deferred_sql)))
        # TODO I don't know if or when this is needed.
        if transaction.is_managed():
            transaction.commit()
        # if not InformationSchema.objects.table_exists(*parse_schema_and_table(model_class._meta.db_table)):
        #     raise Exception("The table {table_name} was not created".format(table_name=model_class._meta.db_table))
        #info = "Model class table {model_class} created\n"
        #logger.debug(info.format(model_class=model_class._meta.db_table))

def drop_tables_for_dynamic_classes(*model_classes):
    for model_class in model_classes:
        full_table_name = model_class._meta.db_table
        schema, table = parse_schema_and_table(full_table_name)
        if InformationSchema.objects.table_exists(schema, table):
            try:
                logger.info("Dropping table %s" % full_table_name)
                db.delete_table(full_table_name)
            except DatabaseError, e:
                raise Exception('full_table_name: {full_table_name}. Original exception: {e}'.format(full_table_name=full_table_name, e=e))

def get_dynamic_resource_class_name(super_class, model_class):
    # Form the name from the model class's name schema portion
    return "{0}{1}".format(model_class.__name__, super_class.__name__)

def get_dynamic_model_class_name(abstract_class, scope_id):
    """
        Returns the naming used for a dynamic model class, which is always based on the table name
    :param abstract_class: The table name in the form "'schema'.'table'"
    :param scope_id: The id of the scope of the dynamic subclass, such as a ConfigEntity id
    :return:
    """
    return "{0}{1}".format(abstract_class.__name__, scope_id)



def create_join(source_class, source_field, related_class, related_field, **kwargs):
    """
        Creates a join between two classes without using a modeled Django association. We do this to in order to populate a Through table manually during import, or two simply create
        a join query that Django does not support through its related field mechanisms.
        Always try to use Django's implicit joining with filter() + extra(select=...) to create a join before resorting to this. Also try filter() with F() functions (see Django docs)
    :param source_class:
    :param source_field:
    :param related_class:
    :param related_field:
    :param **kwargs: Optional arguments for join
        'extra' dict of extras to select
        'join_on_base' if True use the base class for the join
        'join_related_on_base' if True use the base class of the join class for the join
    :return:
    """

    # We either want to join to the related_class or its base, the latter case being when the related_class
    # inherits the field that we want to join
    resolved_related_class = related_class.__base__ if kwargs.get('join_related_on_base', False) else related_class

    selections = source_class.objects.extra(**merge(dict(
        select={'related_pk': '{join_class_table}.{join_class_pk}'.format(
            join_class_table=resolved_related_class._meta.db_table, join_class_pk=resolved_related_class._meta.pk.column)
        }),
                                                    kwargs.get('extra', {}) or {})
    )
    # setup initial FROM clause
    selections.query.join((None, source_class._meta.db_table, None, None))

    if kwargs.get('join_on_base', False):
        # Manually join in the base model so that is joins before the join below
        parent_field = source_class._meta.parents.values()[0]
        connection = (
            source_class._meta.db_table,
            source_class.__base__._meta.db_table,
            parent_field.column,
            'id'
        )
        selections.query.join(connection)

    # join to join class
    connection = (
        (source_class.__base__ if kwargs.get('join_on_base', False) else source_class)._meta.db_table,
        resolved_related_class._meta.db_table,
        source_field.column,
        related_field.column,
    )
    selections.query.join(connection)

    return selections


def create_join_across_association(feature_class, association_field_name):

    association_field = getattr(feature_class._meta, association_field_name)
    association_class = association_field.through.blah

    features = feature_class.objects.extra(
        select={'pk': '{association_class_table}.{association_class_pk}'.format(
            association_class_table=association_class._meta.db_table, association_class_pk=association_class.pk.column)
        }
    )
    # setup intial FROM clause
    feature_class.query.join((None, feature_class._meta.db_table, None, None))

    # join to through class
    primary_connection = (
        feature_class._meta.db_table,
        association_field.m2m_db_table(),
        feature_class._meta.pk.column,
        association_field.m2m_column_name(),
    )
    feature_class.query.join(primary_connection, promote=True)

    # join to association class
    reverse_connection = (
        association_field.m2m_db_table(),
        association_class._meta.db_table,
        association_field.m2m_reverse_name(),
        association_class._meta.pk.column,
    )
    feature_class.query.join(reverse_connection, promote=True)

class JoinRelationship(object):
    def __init__(self, source_class, related_field_name, related_field_configuration,
                 query=None, filter_dict=None, extra=None, custom_join=None, join_on_base=False, join_related_on_base=False):
        self.source_class = source_class
        self.related_field = getattr(source_class, related_field_name).field
        self.related_class = self.related_field.rel.to
        self.query = query
        self.filter_dict = filter_dict
        self.extra = extra
        self.custom_join = custom_join
        self.join_on_base = join_on_base
        self.join_related_on_base = join_related_on_base

        self.source_class_join_field_name = related_field_configuration.get('source_class_join_field_name', None)
        self.related_class_join_field_name = related_field_configuration.get('related_class_join_field_name', None)

class SingleJoinRelationship(JoinRelationship):
    def __init__(self, source_class, related_field_name, related_field_configuration, query=None, filter_dict=None, extra=None, custom_join=None, join_on_base=None, join_related_on_base=None):
        super(SingleJoinRelationship, self).__init__(source_class, related_field_name, related_field_configuration,
                                                     query=query, filter_dict=filter_dict, extra=extra, custom_join=custom_join, join_on_base=join_on_base, join_related_on_base=join_related_on_base)

class ManyJoinRelationship(JoinRelationship):
    def __init__(self, source_class, related_field_name, related_field_configuration, query=None, filter_dict=None, extra=None, custom_join=None, join_on_base=None, join_related_on_base=None):
        super(ManyJoinRelationship, self).__init__(source_class, related_field_name, related_field_configuration,
                                                   query=query, filter_dict=filter_dict, extra=extra, custom_join=custom_join, join_on_base=join_on_base, join_related_on_base=join_related_on_base)

        # Extract field and column info about the through class
        self.through_class = self.related_field.rel.through
        self.through_class_self_field = resolve_field_of_type(self.through_class, source_class)
        self.through_class_self_column_name = self.through_class_self_field.column

        self.through_class_related_field = resolve_field_of_type(self.through_class, self.related_class)
        self.through_class_related_column_name = self.through_class_related_field.column
