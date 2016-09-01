
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

import inspect
import logging
import re
import traceback
import sys

from django.contrib.gis.db import models
from django.db import DEFAULT_DB_ALIAS, reset_queries
from django.db.models import Max, Min, Count
from django.db.models.fields import NOT_PROVIDED, DateTimeField, CharField, TextField
from django.db.models.fields.related import ReverseManyRelatedObjectsDescriptor
from django.db.models.query import RawQuerySet
from django.utils.timezone import now
from south.utils.datetime_utils import datetime
from django.conf import settings
import psycopg2

from footprint.main.database.import_data import ImportData
from footprint.main.lib.functions import map_property, merge, map_dict, map_to_dict, filter_dict, map_dict_to_dict, deep_merge, compact, \
    accumulate, dual_map, flat_map, remove_keys, filter_keys
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.geospatial.intersection import GeographicKey, AttributeIntersection, Intersection
from footprint.main.publishing.import_processor import ImportProcessor
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.utils.dynamic_subclassing import create_tables_for_dynamic_classes, drop_tables_for_dynamic_classes, create_join, ManyJoinRelationship, SingleJoinRelationship, \
    dynamic_model_table_exists
from footprint.main.utils.model_utils import resolve_field
from footprint.main.utils.uf_toolbox import count_cores, queue_process, MultithreadProcess
from footprint.main.utils.utils import get_property_path, resolve_module_attr
from footprint.main.models.database.information_schema import InformationSchema
from footprint.uf_tools import dictfetchall
from footprint.utils.postgres_utils import pg_connection_parameters

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)
UF_GEOMETRY_ID = 'uf_geometry_id'
UF_GEOMETRY_ID_TYPE = 'varchar'


def on_config_entity_post_save_data_import(sender, **kwargs):
    """
        Import the data for all DbEntities (if needed) of the ConfigEntity
    :param sender:
    :param kwargs: 'instance': The config_entity, 'db_entity_keys': Optional. Limits the DbEntities processed to the
    given keys
    :return: None
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_save_data_import. ConfigEntity: %s" % config_entity.name)

    process_db_entities(**kwargs)

    reset_queries()


def on_db_entity_post_save_data_import(sender, **kwargs):
    """
        On DbEntity save import its data
        :param sender:
        :param kwargs: 'instance': The DbEntityInterest
        :return: None
    """

    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    if db_entity_interest.deleted:
        # Nothing to do for deleted instances
        return

    if db_entity_interest.db_entity.source_db_entity_key:
        # No import to do for cloned DbEntities, such as Result DbEntities
        return

    config_entity = db_entity_interest.config_entity
    db_entity = db_entity_interest.db_entity
    logger.info("Handler: on_db_entity_post_save_data_import. DbEntity: %s" % db_entity.full_name)

    process_db_entity(
        config_entity,
        db_entity,
        **kwargs)


def process_db_entities(**kwargs):
    """
        process all of the db_entities or a limited number for the given config_entity
        :param kwargs: 'instance' is the config_entity, 'db_entity_keys' is an optional list of
        keys to limit the DbEntities. 'importer_processor' overrides the default ImportProcessor with a custom class
        used on each DbEntity
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)

    # Get the list of DbEntity instances and their corresponding subclasses (the latter if it is configured)
    # Make sure these are both owned by the config_entity and not clones
    # Only import the DbEntity if the config_entity is the owner of the db_entity.
    # The ones that adopt it need not re-import
    limited_db_entity_keys = kwargs.get('db_entity_keys', None)

    db_entities = filter(lambda db_entity:
                            (not limited_db_entity_keys or db_entity.key in limited_db_entity_keys) and\
                            not db_entity.is_clone, config_entity.owned_db_entities(**filter_keys(kwargs, ['deleted']))
                         )

    def db_entity_priority(db_entity):
        # Scores the DbEntity to make sure primary geographies get the lowest (best) score, and that DbEntities with
        # dependencies to others score below those others
        related_sum = accumulate(
            lambda sum, db_entity: sum+db_entity_priority(db_entity),
            0,
            config_entity.computed_db_entities(
                # Find the key of any related DbEntities
                key__in=compact(map_property((get_property_path(db_entity, 'feature_class_configuration.related_fields') or {}).values(), 'related_key')))
        )
        # Higher score is lower priority
        # primary is most important, followed by sum of related db_entities, followed by id
        return 10e16 * (0 if get_property_path(db_entity, 'feature_class_configuration.primary_geography') else 1) + \
               10e8*related_sum + \
               db_entity.id

    # Sort so primary_geographies are processed first
    # We also need to make sure that any DbEntity that has a relation to another is processed after the latter
    for db_entity in sorted(
            db_entities,
            key=db_entity_priority):
        feature_class_configuration = FeatureClassCreator(config_entity, db_entity)
        # TODO this filter is just here to block remote urls of background layers
        # It doesn't really make much sense otherwise, although we do have to import from somewhere
        # It certainly doesn't make sense in the clone case have clones copy their source's urls
        # reimportable is True except for db_entities that got their data from uploading,
        # which means no source is available after creation
        if db_entity.importable and\
            (db_entity.reimportable or
            (kwargs.get('import_processor') == DeleteImportProcessor) or
                (feature_class_configuration.has_dynamic_model_class() and
                not dynamic_model_table_exists(feature_class_configuration.dynamic_model_class()))):
            process_db_entity(
                config_entity,
                db_entity,
                **kwargs)


def process_db_entity(config_entity, db_entity,  **kwargs):
    """
        Processes a db_entity according to its feature_class_configuration.
        An ImportProcessor is chosen for the db_entity based on its feature_class_configuration.data_importer
        configuration, or it defaults to DefaultImporter. The kwargs of this importer's constructor
        optionally come from feature_class_configuration.data_importer_kwargs
        The ImporterProcessor does one of three operations: importer, peer_importer, or cloner.
        Importer imports primary data from a source peer_importer imports based on a peer DbEntity in
        the config_entity. cloner clones from the same db_entity of another config_entity.
        The operation chosen is based on the feature_class_configuration
        :param config_entity: The db_entity owner
        :param db_entity: The instance whose features are being importer
        :param kwargs: specify 'import_processor' to specify a custom ImportProcessor for all db_entities
        to override it for the db_entity with a custom class
    """
    custom_import_processor = db_entity.feature_class_configuration.data_importer if db_entity.feature_class_configuration else None
    import_processor_class = kwargs.get('import_processor',
        (resolve_module_attr(custom_import_processor) if custom_import_processor else DefaultImportProcessor))

    import_processor = import_processor_class(db_entity=db_entity, **remove_keys(kwargs, ['import_processor']))

    logger.info("Data Import Publishing. Processor: %s DbEntity: %s" % (
        import_processor.__class__.__name__, db_entity.full_name))

    if config_entity.origin_instance and FeatureClassCreator(config_entity, db_entity).dynamic_model_class_is_ready:
        # If there is an origin_instance we override our importing and clone from the origin if this isn't a newly imported layer
        # feature_class_is_ready indicates that tit has already been imported
        # The db_entity configured to import from another db_entity's class instance objects
        logger.info("Cloning DbEntity: %s of ConfigEntity %s from that of ConfigEntity %s" % (db_entity.full_name, config_entity.name, config_entity.origin_instance.name))
        import_processor.cloner(config_entity, db_entity)
    elif db_entity.feature_class_configuration and db_entity.feature_class_configuration.import_from_db_entity_key:
        # Copy data from a peer table
        # The db_entity configured to import from another db_entity's class instance objects
        logger.info("Peer Importing DbEntity: %s" % db_entity.full_name)
        import_processor.peer_importer(config_entity, db_entity, filter_query=db_entity.feature_class_configuration.filter_query)
    elif db_entity.importable:
        # Import from a source table
        # The table data needs to be imported from a seed table in the public schema
        logger.info("Source Importing DbEntity: %s" % db_entity.full_name)

        # logic added to allow user to replace a table based on the db_entity configuration
        # if configured, the table and all of its relations are dropped prior to a new import of the data.
        # the default of db_entity.feature_class_configuration.replace_table is False
        if db_entity.feature_class_configuration.replace_table:
            logger.info("DbEntity Exists and is configured to be replaced - DROPPING: %s" % db_entity.full_name)
            DeleteImportProcessor().drop_data(config_entity, db_entity)

        import_processor.importer(config_entity, db_entity)


class DefaultImportProcessor(ImportProcessor):

    def importer(self, config_entity, db_entity):
        """
            Imports a feature table from a remote server or creates empty table with or without associations base on
            configurations
        :param config_entity:
        :param db_entity:
        :return:
        """

        # Import from a sql dump and create Geography instances for each feature in anticipation of importing the feature
        # Get the name of the source db_entity table, which might be modified for testing

        if not InformationSchema.objects.table_exists(db_entity.schema, db_entity.table):
            # Attempt to fetch the feature tables from the import database. This dumps the tables to the local server
            # and pipes them into the config_entity's schema.
            if db_entity.feature_class_configuration.empty_table:
                feature_class = config_entity.db_entity_feature_class(db_entity.key)
                # Create the table here since there is no import
                create_tables_for_dynamic_classes(feature_class)
            else:
                ImportData(config_entity=config_entity, db_entity_key=db_entity.key).run()
                add_primary_key_if_needed(db_entity)

        # Once the db_entity feature data is present in the system, get or create the feature_class_configuration and
        # pouplate association tables
        # Use the feature_class configuration to create the feature_class. Otherwise inspect the imported table to create it
        if db_entity.feature_class_configuration and not db_entity.feature_class_configuration.generated:
            # Nothing to do
            pass
        else:
            # Create the feature_class_configuration using introspection on the table and assign it to the db_entity
            feature_class_creator = FeatureClassCreator(config_entity, db_entity)
            # Find fields by introspecting the imported table
            feature_class_configuration = feature_class_creator.feature_class_configuration_from_introspection()
            # Add these fields to the feature_class_configuration
            feature_class_creator.update_db_entity(feature_class_configuration)

        if not db_entity.feature_class_configuration.no_table_associations:
            # Create association classes and tables and populate them with data
            create_and_populate_relations(config_entity, db_entity)

    def peer_importer(self, config_entity, db_entity, import_from_origin=False, source_queryset=None, filter_query=None):
        """
            Creates the ConfigEntity specific FeatureClass table by importing from a peer table, the former is
            indicated by the feature_class and the latter by the source_feature_class.
        :param config_entity: The config_entity import target
        :param db_entity: The db_entity target
        :param import_from_origin: Optionally set True to import from the origin_instance of the DbEntity.
        :param source_queryset: Optionally limit the features imported, or even expand what is import to a joined queryset.
        The latter would have to be done in conjunction with import_fields (and isn't implemented.)
        By default all fields modeled by the feature_class are imported
        :return:
        """
        source_db_entity_key = db_entity.origin_instance.key if \
            import_from_origin else \
            db_entity.feature_class_configuration.import_from_db_entity_key
        # Custom import field names. Normally not needed
        import_fields = db_entity.feature_class_configuration.import_fields or []
        source_db_entity = config_entity.computed_db_entities().get(key=source_db_entity_key)
        source_feature_class = config_entity.db_entity_feature_class(source_db_entity_key)
        feature_class = config_entity.db_entity_feature_class(db_entity.key)
        # Create the feature_class table and its base class if they don't yet exist
        create_tables_for_dynamic_classes(feature_class.__base__, feature_class)

        if filter_query:
            filtered_queryset = source_feature_class.objects.filter(**filter_query)
        else:
            filtered_queryset = source_queryset
        # Import the data from the source feature class
        if not db_entity.feature_class_configuration.empty_table:

            _peer_or_clone_table_import(feature_class, source_feature_class,
                                        source_queryset=filtered_queryset,
                                        import_fields=import_fields,
                                        import_ids_only=db_entity.feature_class_configuration.import_ids_only)
        # Add and optionally fill the association tables based on the origin db_entity
        create_and_populate_associations_from_clone_source(
            config_entity, db_entity, source_db_entity=source_db_entity, source_queryset=filtered_queryset, no_populate=db_entity.feature_class_configuration.empty_table)

    def cloner(self, config_entity, db_entity):
        """
            Clones data from the config_entity's origin_instance. We only do this if the db_entity
            is owned by the config_entity. In other words if we're a Scenario don't copy Project or Region
            scoped db_entities. They will be adopted by the cloned Scenario from the Project
        :param config_entity:
        :param db_entity_key:
        :param import_fields. Optional limited fields to import. If None it imports all fields.
        :return:
        """

        # Never clone a DbEntity belonging to a parent ConfigEntity, or a DbEntity
        # whose feature_class_configuration belongs to a peer DbEntity, as is the case
        # for Result DbEntity instances
        if config_entity.db_entity_owner(db_entity) != config_entity:
            logger.info("Skipping Clone of DbEntity %s because it is not owned by ConfigEntity: %s, rather parent ConfigEntity %s",
                        (db_entity.full_name, config_entity.name, config_entity.db_entity_owner(db_entity).name))
            return
        if db_entity.feature_class_configuration.feature_class_owner:
            logger.info("Skipping Clone of DbEntity %s because it does not own the feature_class, rather it is owned by DbEntity %s",
                        (db_entity.full_name, db_entity.feature_class_configuration.feature_class_owner))
            return

        destination_feature_class = config_entity.db_entity_feature_class(db_entity.key)
        source_feature_class = config_entity.origin_instance.db_entity_feature_class(db_entity.key)
        # Custom import field names. Normally not needed
        import_fields = db_entity.feature_class_configuration.import_fields or []

        if not InformationSchema.objects.table_exists(db_entity.schema, db_entity.table):
            # Create the destination_feature_class table and its base class if they don't yet exist
            if db_entity.feature_class_configuration.no_table_associations:
                create_tables_for_dynamic_classes(destination_feature_class)
            else:
                create_tables_for_dynamic_classes(destination_feature_class.__base__, destination_feature_class)

        # Copy the data from the source_feature_class - if there are no table associations configured only do a simple
        # import of the data - otherwise all associations will be copied
        if db_entity.feature_class_configuration.no_table_associations:
            _base_or_main_table_import(destination_feature_class,
                                       source_feature_class,
                                       simple_import=True)
        else:
            _peer_or_clone_table_import(destination_feature_class, source_feature_class, import_fields)

        # Add and fill the association tables based on the origin db_entity
        source_db_entity = config_entity.origin_instance.computed_db_entities().get(key=db_entity.key)

        if not db_entity.feature_class_configuration.no_table_associations:
            create_and_populate_associations_from_clone_source(config_entity, db_entity, source_db_entity=source_db_entity)


def add_primary_key_if_needed(db_entity):
    """
        If an imported table came in without a primary key column, add it. If it came in with
        a different primary_key than our preferred one, rename it
    """

    InformationSchema.create_primary_key_column_from_another_column(
        db_entity.schema,
        db_entity.table,
        from_column=db_entity.feature_class_configuration.primary_key,  # TODO rename primary_key
        # We always want our primary_key to be id
        primary_key_column='id')


def create_and_populate_geography_associations(db_entity, feature_class):

    feature_class_creator = FeatureClassCreator(feature_class.config_entity, db_entity)

    # First, if the db_entity is a primary_geography we need to fill the geography
    # table for this db_entity's geography_scope with the features of this db_entity
    if db_entity.feature_class_configuration.primary_geography:
        # By default create geography associations
        geography_class = feature_class_creator.dynamic_geography_class()
        # Create the geography class table if not already created
        create_tables_for_dynamic_classes(geography_class)
        # If the table contains primary geographies, get or create a dynamic subclass of
        # Geography to fill the table with the geographies.
        # We use the source_table_id column of the Geography table to guarantee uniqueness of the rows,
        # so that they won't be imported twice.
        update_or_create_primary_geographies(db_entity, feature_class)

    # Next we need to iterate through the Geography class for each ConfigEntity scope
    # beginning at this DbEntity's geography_scope. We only iterate on the Geography classes that have
    # physical tables, since sometimes there is no primary geography at a certain scope.
    # Note that we assume that the intersection type from our features to the Geometry table at each
    # geography scope is the same type of join. E.g. if we configured our features to join with
    # an attribute join they will join with such to each Geography table.
    # Ensure that all geography classes of parent scopes are instantiated
    feature_class_creator.dynamic_geography_classes

    for config_entity_geography_scope in feature_class_creator.geography_scopes():
        populate_geography_association(config_entity_geography_scope, db_entity, feature_class)


def populate_geography_association(config_entity_geography_scope, db_entity, feature_class):
    """
        Populate the geography association table for a feature_class's table's relationship
        to the geography table at that scope. The population is based on the intersection
        type defined for the db_entity. It might be an attribute join with the primary geography
        db_entity or it might be a geographic join (centroid, polygon, etc)
    :param config_entity_geography_scope: A ConfigEntity at or above the geography_scope of the
    db_entity. This is typically the ConfigEntity of the DbEntity or higher. However DbEntities
    at Scenario scope start with the Project scope since Scenarios never have a primary geography
    :param db_entity: The DbEntity representing the Feature class
    :param feature_class: The Feature class
    :return:
    """
    # Get the geography class corresponding to the geography scope
    geography_class = FeatureClassCreator(config_entity_geography_scope, no_ensure=True).dynamic_geography_class()
    if db_entity.feature_class_configuration.primary_geography or \
       db_entity.feature_behavior and db_entity.feature_behavior.intersection and isinstance(db_entity.feature_behavior.intersection_subclassed, AttributeIntersection):
        # This case covers primary geography tables or attribute join tables.
        # In both case we want to create a join from the db_entity's feature table to
        # the Geography table by comparing the id of the features to the primary_key of the primary_geography
        # features.
        # Find the DbEntity that represents the primary_geography. Use it as our source
        primary_db_entity = feature_class.config_entity.subclassed.primary_geography_db_entity
        source_db_entity = db_entity if \
            db_entity.feature_class_configuration.primary_geography else \
            primary_db_entity

        parent_field = feature_class._meta.parents.values()[0]
        related_field_configuration = dict(
            source_class_join_field_name=parent_field.name,
            related_class_join_field_name='source_id',
        )
        many_relation_params = dict(
            extra=(dict(
                where=['{geography_class_name}.source_table_id = {source_table_id}'.format(
                    geography_class_name=geography_class._meta.db_table,
                    source_table_id=source_db_entity.id)])))

        # For each config_entity including that of this feature_class up to but not including
        # The GlobalConfig, we want to populate the many relationship between this feature_class's
        # geographies and the Geography table at each config_entity scope. This allows
        # us to quickly join two feature tables in a query by joining them by attribute through
        # the appropriate Geography table
        populate_many_relation(
            feature_class,
            'geographies_%s' % config_entity_geography_scope.id, related_field_configuration,
            **many_relation_params)
    else:
        related_field_configuration = dict(
            source_class_join_field_name='wkb_geometry',
            related_class_join_field_name='geometry'
        )
        # Perform the intersection based on the configuration. The intersection dict has type and to keys
        # Type is the type of intersection for the main class and to holds the type of intersection for the primary
        # geographies to which where joining. Either can be point or centroid
        intersection = db_entity.feature_behavior.intersection_subclassed
        if not intersection:
            raise Exception("Expected key intersection not configured for feature_behavior of db_entity %s" % db_entity)
        if intersection.__class__ == Intersection:
            raise Exception("Should be a subclass: %s" % (intersection.__dict__))
        intersection_types = dict(centroid='ST_Centroid({0})', polygon='{0}')
        custom_join = r'ON ST_Intersects({frm}, {to})'.format(
            frm=intersection_types[intersection.from_geography].format('\g<1>'),
            to=intersection_types[intersection.to_geography or GeographicKey.POLYGON].format('\g<2>')
        )
        many_relation_params = dict(
            custom_join=custom_join,
            join_on_base=True,
            extra=(dict(
                where=['{db_table}.id >= {start_id} AND {db_table}.id <= {end_id}'.format(
                    db_table=geography_class._meta.db_table,
                    start_id='{start_id}',
                    end_id='{end_id}'
                )]
            ))
        )

        populate_many_relation_multithread(
            feature_class,
            'geographies_%s' % config_entity_geography_scope.id, related_field_configuration,
            **many_relation_params)


def create_and_populate_relations(config_entity, db_entity):
    """
        Creates all association classes and tables and populates the tables according to the DbEntity feature_class_configuration
    :param db_entity: The DbEntity whose feature_class associations are to be populated
    :return:
    """

    logger.info("Data Import Publishing. Creating and populating relations for DbEntity: %s" % (
        db_entity.full_name))

    feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
    # Create the feature_class relation table if it doesn't exist. The base table will be created by the import process
    create_tables_for_dynamic_classes(feature_class)

    logger.info("Data Import Publishing. Creating single field relations DbEntity: %s" % (
        db_entity.full_name))

    # For ForeignKey relationships, the feature_class table holding the relationships is populated
    # This populates the feature_class's rel table no matter what so that it can be used below
    single_related_field_configurations = filter_dict(
        lambda related_field_name, related_field_configuration: related_field_configuration['single'],
        db_entity.feature_class_configuration.related_fields or {})
    populate_single_relations(feature_class, single_related_field_configurations)

    logger.info("Data Import Publishing. Creating associations for DbEntity: %s" % (
        db_entity.full_name))

    # Don't run this unless we have the feature_behavior, since it defines how these associations are populated
    if not db_entity.feature_behavior:
        raise Exception("Feature Behavior is not yet defined on db_entity %s" % db_entity.full_name)
    create_and_populate_associations(config_entity, db_entity)

    logger.info("Data Import Publishing. Finished creating relations for DbEntity: %s" % (
        db_entity.full_name))


def create_and_populate_associations(config_entity, db_entity):
    # Populate the Geography table of the config_entity schema for db_entities marked feature_class_configuration.primary_geography
    # Also create and populate the Feature to Geography through classes and tables. These through tables will associate with any
    # rows in the Geogrpahy table that they match by intersection (or by attribute match if the through class associates a primary geogrpahy DbEntity)

    logger.info("Data Import Publishing. Creating and populating associations for DbEntity: %s" % (
        db_entity.full_name))

    feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
    create_and_populate_geography_associations(db_entity, feature_class)

    # Each field_name in the mapping indicates a mapping from the associated class to the local class
    for relation_field_name, related_field_configuration in filter_dict(
            lambda related_field_name, related_field_configuration: not related_field_configuration['single'],
            db_entity.feature_class_configuration.related_fields or {}):
        # Each field_name in the mapping indicates a mapping from the associated class to the local class
        # For ForeignKey relationships, the feature_class table holding the relationships is populated
        populate_many_relation(feature_class,
                               relation_field_name,
                               related_field_configuration,
                               # Join the related class on its base table if its a related_db_entity
                               # since only the base table has the field we want to join
                               join_related_on_base=related_field_configuration.get('related_db_entity', False) and True)


def populate_single_relations(feature_class, related_field_configurations, query=None, filter_dict=None, extra=None, custom_join=None):
    """
        Populates all ForeignKey fields in the feature_class relationships table.
        Even if there are no ForeignKey fields this will populate the table with just the parent table pk so that it can be used for querying
    :param feature_class:
    :param related_field_configurations:
    :param query:
    :param filter_dict:
    :param extra:
    :param custom_join:
    :return:
    """

    # Quit if the feature_class relationships table is already populated
    if feature_class.objects.count() > 0:
        return

    # Create each SingleJoinRelationship
    relationships = map_dict_to_dict(
        lambda related_field_name, related_field_configuration: [
            related_field_name,
            SingleJoinRelationship(feature_class, related_field_name, related_field_configuration,
                                   query=None, filter_dict=None, extra=None, custom_join=None,
                                   # Join on the base class of the related class if its a feature relationship
                                   join_related_on_base=related_field_configuration.get('related_key', False) and True)],
        related_field_configurations)

    parent_field = feature_class._meta.parents.values()[0]

    def get_mapped_related_results(related_field_name, relationship):
        # Create a single dict for the results of each relationship. This will be in the form
        # {pk1: {related_field_name:value}, pk2: {related_field_name: value}, ...}
        related_field_column = resolve_field(relationship.source_class, related_field_name).column
        return map_to_dict(
            # Take each result dict {pk:n, related_pk:m} and map it to a 2-level dict with unique inner key that we can merge
            lambda result:
                [result['id'], {related_field_column: result['related_pk'], parent_field.column: result['id']}],
            # Use the base version of the feature_class. The rel table is what we're filling
            get_related_results(feature_class.__base__, relationship))

    def get_all_base_results():
        # make sure to merge in all base object values in case there are no relationships or null foreign keys that cause joins to be missing
        return map_to_dict(
            # Take each result dict {pk:n, related_pk:m} and map it to a 2-level dict with unique inner key that we can merge
            lambda result: [result['id'], {parent_field.column: result['id']}],
            # Use the base version of the feature_class. The rel table is what we're filling
            feature_class.__base__.objects.values('id'))

    def get_default_fields():
        # Find fields of the rel class that have defaults
        return filter(
            lambda field: field.model==feature_class and field.default and
                            # Accept auto_now_add fields
                           ((hasattr(field, 'auto_now_add') and field.auto_now_add) or
                            # Reject NOT_PROVIDED defaults
                           (not (inspect.isclass(field.default) and issubclass(field.default, NOT_PROVIDED)))),
            feature_class._meta.fields)

    def get_mapped_default_results():
        fields_with_defaults = get_default_fields()
        default_dict = map_to_dict(lambda field: [field.name, now() if field.auto_now_add else field.default()], fields_with_defaults)
        return map_to_dict(
            # Take each result dict {pk:n, related_pk:m} and map it to a 2-level dict with unique inner key that we can merge
            lambda result: [result['id'], default_dict],
            # Use the base version of the feature_class. The rel table is what we're filling
            feature_class.__base__.objects.values('id'))

    def field_formatter(field):
        if isinstance(field, (DateTimeField, CharField, TextField)):
            return lambda value: "'%s'" % str(value) if value else 'null'
        return lambda value: str(value) if value else 'null'

    # Get the results of each relationship and create a lookup table by coalescing the results based on pk
    merged_results = deep_merge(
        # Get all the results from the base so we have every record
        # Merge the relationship results. This will create the form
        # pk1: {related_field_name1:value, related_field_name2: value, ...}, pk2: ...}
        *[get_all_base_results()] +
         [get_mapped_default_results()] +
        map_dict(
            get_mapped_related_results,
            relationships)
    ).values()  # forget the keys--we don't need them

    if merged_results:
        # Do a manual SQL insert. Django doesn't support bulk inserts on child models, plus the parent table is already full of the records,
        # so inserting via Django doesn't make sense
        columns = [parent_field.column] +\
                  map(lambda field: field.column, get_default_fields()) +\
                  map(lambda relationship: relationship.related_field.column, relationships.values())
        column_formatters = map(lambda field: field_formatter(field),
                  [parent_field] + \
                  map(lambda field: field, get_default_fields()) + \
                  map(lambda relationship: relationship.related_field, relationships.values()))

        column_names = ', '.join(columns)
        column_values = ', '.join(map(lambda result:
                                           '(' +', '.join(dual_map(
                                               lambda column, column_formatter: column_formatter(result.get(column, None)),
                                               columns, column_formatters)) +
                                           ')',
                                       merged_results))
        cmd = "INSERT INTO {table} ({column_names}) VALUES {column_values}".format(
            table=feature_class._meta.db_table, column_names=column_names, column_values=column_values
        )
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        result = cursor.execute(cmd)
        if result:
            raise result


def populate_many_relation_multithread(feature_class, related_field_name, related_field_configuration,
                                       query=None, filter_dict=None, extra=None, custom_join=None,
                                       join_on_base=False, join_related_on_base=False):
    """
        Populate an association table that is associated with the given feature_class.
        You must specify source_field_name and field_name_on_related_class to join on those two values, or specify a query to skip the join process
    :param feature_class:
    :param related_field_name: The field name of the feature_class that leads to the associated class.
    This doesn't have to be a real column on the table, but it must be modeled as a ForeignKey, ManyToMany, etc
    :param related_field_configuration. Configuration dict containing:
        source_class_join_field_name: Optional The name of the feature_class field whose value will be used to join with the associated class table
        related_class_join_field_name: Optional The field name of the feature_class that points to the association
    :param query: Optional query that contains the data fro bulk insert
    :param filter_dict: Optional filter for the query
    :param extra: For where clauses on the join table
    :param custom_join: regex string to replace the normal table1.field1 = table2.field2 join clause. The two table.field segments are captured by a regex and put in the custom_join
    regex. So the custom_join must be a regex and include a \1 and \2.
    :param join_on_base: Join the feature_class using its base class (not its rel class)
    :param join_related_on_base: Join the related_class using its base class (not its rel class)
    :return:
    """

    #count the number of cores available to assign jobs to
    thread_count = count_cores()
    queue = queue_process()

    relationship = ManyJoinRelationship(feature_class, related_field_name, related_field_configuration,
                                        query=query, filter_dict=filter_dict, extra=extra, custom_join=custom_join,
                                        join_on_base=join_on_base, join_related_on_base=join_related_on_base)

    #find the min and max id values from the table - this will be utilized to derive the number of rows to assign to each task
    geography_class_id_dict = relationship.related_class.objects.aggregate(Max('id'), Min('id'), Count('id'))
    #derive the number of rows per thread

    if geography_class_id_dict['id__count'] < 100:
        #for small datasets do not run as a distributed process - enforce only one thread for the whole table
        rows_per_thread=geography_class_id_dict['id__count']
        thread_count=1
    else:
        rows_per_thread = int(round((geography_class_id_dict['id__max'] - geography_class_id_dict['id__min']) / thread_count))

    # Create the through table if doesn't yet exist. This would only happen for an explicit through class
    create_tables_for_dynamic_classes(relationship.through_class)

    # Quit if the table is already populated
    if relationship.through_class.objects.count() > 0:
        return

    queryset = get_related_results(
        feature_class,
        relationship,
        return_queryset=True,
        field_names=['related_pk', 'pk'])

    through_table_columns = [
        # TODO this order corresponds with the order of the queryset selection. It shouldn't be so arbitrary
        relationship.through_class_related_column_name,
        relationship.through_class_self_column_name]

    if isinstance(queryset, RawQuerySet):
        select_query = queryset.query.sql
    else:
        select_query = queryset.query

    insert_sql = 'insert into {through_table} ({through_table_columns}) {select_query}'.format(
        through_table=relationship.through_class._meta.db_table,
        through_table_columns=','.join(through_table_columns),
        select_query=select_query
    )
    logger.info("Populating through table {through_table} between {feature_class_table} and {related_class_table}".format(
        through_table=relationship.through_class._meta.db_table,
        feature_class_table=feature_class._meta.db_table,
        related_class_table=relationship.related_class._meta.db_table
    ))
    logger.info("Using insert sql: {insert_sql}".format(insert_sql=insert_sql))

    for i in range(thread_count):
        t = MultithreadProcess(queue, insert_sql)
        t.setDaemon(True)
        t.start()

    #always start with the lowest id value
    start_id = geography_class_id_dict['id__min']

    #iterate over the number of threads assigning start and end id values for each process
    for i in range(thread_count):
        if i == thread_count - 1:
            #always end with the maximum id value
            end_id = geography_class_id_dict['id__max']
        else:
            #incremental id value for the top end of the range
            end_id = start_id + rows_per_thread - 1

        rows_to_process = {
            'start_id': start_id,
            'end_id': end_id
        }
        start_id += rows_per_thread
        queue.put(rows_to_process)

    #wait on the queue until everything has been processed
    queue.join()


def populate_many_relation(feature_class, related_field_name, related_field_configuration,
                           query=None, filter_dict=None, extra=None, custom_join=None,
                           join_on_base=False, join_related_on_base=False):
    """
        Populate an association table that is associated with the given feature_class.
        You must specify source_field_name and field_name_on_related_class to join on those two values, or specify a query to skip the join process
    :param feature_class:
    :param related_field_name: The field name of the feature_class that leads to the associated class.
    This doesn't have to be a real column on the table, but it must be modeled as a ForeignKey, ManyToMany, etc
    :param related_field_configuration. Configuration dict containing:
        source_class_join_field_name: Optional The name of the feature_class field whose value will be used to join with the associated class table
        related_class_join_field_name: Optional The field name of the feature_class that points to the association
    :param query: Optional query that contains the data fro bulk insert
    :param filter_dict: Optional filter for the query
    :param extra: For where clauses on the join table
    :param custom_join: regex string to replace the normal table1.field1 = table2.field2 join clause. The two table.field segments are captured by a regex and put in the custom_join
    regex. So the custom_join must be a regex and include a \1 and \2.
    :param join_on_base: Join the feature_class using its base class (not its rel class)
    :param join_related_on_base: Join the related_class using its base class (not its rel class)
    :return:
    """

    relationship = ManyJoinRelationship(feature_class, related_field_name, related_field_configuration,
                                        query=query, filter_dict=filter_dict, extra=extra, custom_join=custom_join,
                                        join_on_base=join_on_base, join_related_on_base=join_related_on_base)

    # Create the through table if doesn't yet exist. This would only happen for an explicit through class
    create_tables_for_dynamic_classes(relationship.through_class)

    # Quit if the table is already populated
    if relationship.through_class.objects.count() > 0:
        return

    queryset = get_related_results(
        feature_class,
        relationship,
        return_queryset=True,
        field_names=['related_pk', 'pk'])

    through_table_columns = [
        # TODO this order corresponds with the order of the queryset selection. It shouldn't be so arbitrary
        relationship.through_class_related_column_name,
        relationship.through_class_self_column_name]

    insert_sql = 'insert into {through_table} ({through_table_columns}) {select_query}'.format(
        through_table=relationship.through_class._meta.db_table,
        through_table_columns=','.join(through_table_columns),
        select_query=queryset.query.sql if isinstance(queryset, RawQuerySet) else queryset.query
    )
    logger.info("Populating through table {through_table} between {feature_class_table} and {related_class_table}".format(
        through_table=relationship.through_class._meta.db_table,
        feature_class_table=feature_class._meta.db_table,
        related_class_table=relationship.related_class._meta.db_table
    ))
    logger.info("Using insert sql: {insert_sql}".format(insert_sql=insert_sql))

    conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    result = cursor.execute(insert_sql)


def get_related_results(feature_class, relationship, page_size=10000, return_queryset=False, field_names=None):
    if relationship.source_class_join_field_name and relationship.related_class_join_field_name:
        # The field name on the main class and related class are specified. Resolve and join.
        source_field = resolve_field(feature_class, relationship.source_class_join_field_name)
        related_class_field = resolve_field(relationship.related_class, relationship.related_class_join_field_name)
        # Create the join. The extra parameter can supply additional select and where options.
        # The join will always add the related table's pk column as 'related_pk'. The main table's columns are all
        # by default in the query
        selections = create_join(feature_class, source_field, relationship.related_class, related_class_field,
                                 join_on_base=relationship.join_on_base, join_related_on_base=relationship.join_related_on_base, extra=relationship.extra)
    elif relationship.query:
        # Instead of specifying field names, a custom query is passed in with its own joining done
        selections = relationship.query
    else:
        raise Exception(
            "Function requires either both source_class_join_field_name and related_class_join_field_name to be specified, or else query \
            [{feature_class}]".format(feature_class=feature_class))

    # If specified, add a filter with any extra filter options passed in.
    if relationship.filter_dict:
        filtered_selections = selections.filter(**relationship.filter_dict)
    else:
        filtered_selections = selections

    # If specified, limit the fields
    filtered_selections = filtered_selections.values(*field_names) if field_names else filtered_selections
    if relationship.custom_join:
        # If we defined a custom join, we replace the join generated by the query. Capture the two table.column parts
        # and format the custom join with them.
        # TODO it would be much better if the create_join function above accepted an alternate join equation.
        query_string = str(filtered_selections.query)
        pattern = r'^ON \((.*?) = (.*?)\)'
        join_index = [m.start() for m in re.finditer('ON', query_string)][-1]
        replacement_query = query_string[:join_index] + re.sub(pattern, relationship.custom_join, query_string[join_index:])
        # Excecute the updated query and put the results in dicts
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        if return_queryset:
            return selections.model.objects.raw(replacement_query)
        else:
            cursor = conn.cursor()
            return dictfetchall(cursor)
    else:
        if return_queryset:
            return filtered_selections
        else:
            return filtered_selections.values()


def update_or_create_primary_geographies(db_entity, feature_class):
    """
        Create or update the geography rows for the given primary geography db_entity.
    :param db_entity
    :param feature_class
    """

    # Get or create the Geography class for the config_entity schema
    geography_class = FeatureClassCreator(feature_class.config_entity, db_entity).dynamic_geography_class()
    geography_table = geography_class._meta.db_table

    # Handled by PostGIS 2 as long as the table already has the right projection
    # Tell PostGIS about the new geometry column of the dynamic geography table if needed
    # schema, table = parse_schema_and_table(geography_table)
    # sync_geometry_columns(schema, table)

    full_table_name = db_entity.full_table_name
    logger.info("Updating/Creating rows of geography table {geography_table} for of schema {schema} with tables {source_table} of db_entity key {db_entity_key}".format(
        geography_table=geography_table,
        schema=db_entity.schema,
        source_table=full_table_name,
        db_entity_key=db_entity.key))

    if not feature_class.objects.count() > 0:
        logging.debug("No rows found in primary geography table {full_table_name}".format(full_table_name=full_table_name))
        return

    # If the Geography table already has one of our source_ids assume that we already did the import
    if len(geography_class.objects.filter(source_table_id=str(db_entity.id))) > 0:
        logging.debug("Geography table {geography_table} already contains a source_id matching the first value of {full_table_name}".format(
            geography_table=geography_table,
            full_table_name=full_table_name,
        ))
        return

    # Insert the geography and source_table_id and source_id into the schema's geography table.
    # Use the db_entity.id as the source_table_id and the
    # This indicates what table provide each row of data
    geography_column_insert_sql = "insert into {geography_table} (geometry, source_table_id, source_id) \
      select st_SetSRID(st_transform(wkb_geometry, 4326),4326), {source_table_id}, id from {source_table}".format(
        geography_table=geography_table,
        source_table=full_table_name,
        source_table_id=db_entity.id)
    conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    result = cursor.execute(geography_column_insert_sql)

    if result:
        raise result

    # TODO We must tell existing DbEntities to update their association tables to join to the new geometries


def _peer_or_clone_table_import(destination_feature_class, source_feature_class, source_queryset=None, import_fields=None, import_ids_only=False):
    """
        Handles the details of clone_table_import and peer_table_import
        A clone table import is used when cloning a ConfigEntity. Each db_entity feature table of the config_entity is copied here
        A peer import is used when one feature table of a ConfigEntity is based on another. For example, the future_sceanrio_feature table
        is derived from the base_feature table.

        Because Feature classes are modeled with two tables, the "raw" table and the subclass table containing any ForeignKey relationships,
        this method fills two tables from their source tables.
    :param destination_feature_class:
    :param source_feature_class:
    :param import_fields:
    :param import_ids_only: Default false, copy the rows but only insert the primary key
    :return:
    """

    # First fill the base feature class table with that of the source
    # The base class represents the "raw" table that doesn't have Footprint created relationships
    source_feature_class_base = source_feature_class.__bases__[0]
    destination_feature_class_base = destination_feature_class.__bases__[0]

    # Resolve the DbEntity of the source to find out if it's a clone
    # TODO this might be better for copying uploaded feature tables
    _base_or_main_table_import(destination_feature_class_base,
                               source_feature_class_base,
                               source_queryset=source_queryset,
                               import_fields=import_fields,
                               import_ids_only=import_ids_only)

    # Second fill the rel feature class table, which inherits the base and adds ForeignKey columns
    # We don't clone the ManyToMany association tables here
    _base_or_main_table_import(destination_feature_class,
                               source_feature_class,
                               # Never allow ids from the source that are not in the base feature_class
                               # This stems from the corner case where some rows from the base are
                               # removed, such as for an output table, and we need to refresh the
                               # rel rows to match (See the public_health_updater_tools, table ph_grid_outcomes)
                               source_queryset=(source_queryset or source_feature_class.objects).filter(pk__in=destination_feature_class_base.objects.values_list('pk', flat=True)),
                               import_fields=import_fields,
                               map_primary_key=True,
                               import_ids_only=import_ids_only)


def _base_or_main_table_import(destination_feature_class, source_feature_class,
                               source_queryset=None,
                               import_fields=None,
                               map_primary_key=False,
                               import_ids_only=False,
                               simple_import=False):

    import_manager = source_feature_class.objects
    import_table = import_manager.model._meta.db_table

    if simple_import:
        # If set simple just copy the features directly over
        sql = 'truncate table {feature_class_table} cascade; ' \
              'insert into {feature_class_table} ' \
              'select * from {source_table};'.format(
            feature_class_table=destination_feature_class._meta.db_table,
            source_table=import_table)
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(sql)
        return

    if destination_feature_class.objects.count() == 0:

        # TODO does id belong in here or can we rely on autoincrement?
        source_fields = source_feature_class._meta.fields if not import_ids_only else filter(
            lambda field: field.primary_key or isinstance(field, models.GeometryField),
            source_feature_class._meta.fields
        )

        source_columns = map_property(filter(lambda field: field.model == source_feature_class, source_fields), 'column')

        destination_fields = destination_feature_class._meta.fields if not import_ids_only else filter(
            lambda field: field.primary_key or isinstance(field, models.GeometryField),
            destination_feature_class._meta.fields
        )

        destination_columns = map_property(filter(
            lambda field: field.model == destination_feature_class, destination_fields), 'column')

        # Get all the columns of the destination table that are also in the source table
        columns = filter(lambda c: c in source_columns, destination_columns)
        if import_fields:
            if len(columns) > len(import_fields)+1:
                # If explicit import_fields were provided that don't exist on the source, raise an error
                raise Exception(
                    "Some source feature_class, fields in the explicit import_fields array "
                    "do not exist on the source table. Missing fields %s" %
                    (source_feature_class, set(columns) - set(source_columns)))
            elif len(columns) < len(import_fields)+1:
                # If explicit import_fields were provided that don't exist on the destination, raise an error
                raise Exception(
                    "For destination feature class %s, Some fields in the explicit import_fields array "
                    "do not exist on the destination table. Missing fields %s" %
                    (destination_feature_class, set(source_columns) - set(columns+['id'])))

        destination_column_string = ', '.join(
            columns + ([destination_feature_class._meta.parents.values()[0].column] if map_primary_key else [])
        )

        # We need the source field names, not columns, since we use Django to select from the source
        source_column_to_field_name = map_to_dict(lambda source_field: [source_field.column, source_field.name], source_fields)
        source_field_names = map(lambda column: source_column_to_field_name[column], columns)
        updated_source_field_names = source_field_names + ([source_feature_class._meta.parents.values()[0].name] if map_primary_key else [])
        logger.info("Source field names: %s" % ', '.join(updated_source_field_names))
        logger.info("Destination columns: %s" % destination_column_string)

        # Get default values for the columns NOT in columns
        default_column_string, column_defaults_string = _get_default_columns_and_values(destination_feature_class, columns, skip_primary_key=map_primary_key)

        query = (source_queryset or source_feature_class.objects).values(*updated_source_field_names).query
        fields = map(lambda grandchild: grandchild[0].field,
                     flat_map(lambda child: child.children, query.where.children))
        query_tuple = query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
        selected_query = query_tuple[0] % tuple(dual_map(lambda var, field: "'%s'" % var if isinstance(field, (CharField, TextField)) else var,
                         query_tuple[1], fields))
        select_query_with_defaults = selected_query.replace(' FROM', ', {column_defaults_string} FROM'.format(
            column_defaults_string=column_defaults_string) if column_defaults_string else ' FROM', 1)
        logger.info("Source query %s" % select_query_with_defaults)

        sql = 'insert into {feature_class_table} ({destination_column_string} {default_columns_string}) ' \
              '{select_queryset}'.format(
            feature_class_table=destination_feature_class._meta.db_table,
            destination_column_string=destination_column_string,
            select_queryset=select_query_with_defaults,
            source_table=import_table,
            default_columns_string=', %s' % default_column_string if (default_column_string and destination_column_string) else default_column_string
        )

        logger.info("Insert SQL: %s" % sql)
        conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(sql)


def fill_geography_association_from_source(source_feature_class, destination_feature_class, related_field_configuration,
                                           related_field_name, no_populate):
    # Construct a class instance that models the ManyToMany relationship through the related field for the source
    # class
    source_relationship = ManyJoinRelationship(
        related_field_configuration['source']['source_class'],
        related_field_name,
        related_field_configuration['source']
    )
    # Construct a class instance that models the ManyToMany relationship through the related field for the destination class
    relationship = ManyJoinRelationship(
        related_field_configuration['destination']['source_class'],
        related_field_name,
        related_field_configuration['destination']
    )
    create_tables_for_dynamic_classes(relationship.through_class)
    if relationship.through_class.objects.count() > 0 or no_populate:
        # Already populated this through class table
        pass

    # Fetch the source through instance queryset limited to the features in the destination
    queryset = source_relationship.through_class.objects
    if destination_feature_class.objects.count() != source_feature_class.objects.count():
        queryset = queryset.filter(
            **{'{0}__pk__in'.format(
                source_relationship.through_class_self_field.name): destination_feature_class.objects.values_list('id',
                                                                                                                  flat=True)}
        )
    queryset = queryset.values(
        source_relationship.through_class_related_field.name,
        source_relationship.through_class_self_field.name
    )
    through_table_columns = [
        # TODO this order corresponds with the order of the queryset selection. It shouldn't be so arbitrary
        relationship.through_class_related_column_name,
        relationship.through_class_self_column_name]
    insert_sql = 'insert into {through_table} ({through_table_columns}) {select_query}'.format(
        through_table=relationship.through_class._meta.db_table,
        through_table_columns=','.join(through_table_columns),
        select_query=queryset.query.sql if isinstance(queryset, RawQuerySet) else queryset.query
    )
    logger.info(
        "Populating through table {through_table} between {feature_class_table} and {related_class_table}".format(
            through_table=relationship.through_class._meta.db_table,
            feature_class_table=destination_feature_class._meta.db_table,
            related_class_table=relationship.related_class._meta.db_table
        ))
    logger.info("Using insert sql: {insert_sql}".format(insert_sql=insert_sql))
    conn = psycopg2.connect(**pg_connection_parameters(settings.DATABASES['default']))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    result = cursor.execute(insert_sql)


def create_and_populate_associations_from_clone_source(config_entity, db_entity, source_db_entity=None, source_queryset=None, no_populate=False):
    """
        Creates all association classes and tables and populates the tables according to the DbEntity feature_class_configuration.
        Note that this is only needed for ManyToMany fields, since ForeignKey fields have no association table.
        ForeignKey fields are filled during the clone process
    :param config_entity
    :param db_entity: The DbEntity whose feature_class associations are to be populated
    :param source_db_entity: An optional source DbEntity for the case of a peer_import or clone. This will serv
    :param source_queryset: Optional queryset of the source_feature_class used to limit the associations created.
    :param no_populate: Default False, if True do not fill the table, just create it
        This defaults to all features (source_feature_class.objects.all())
    :return:
    """
    destination_feature_class_creator = FeatureClassCreator(config_entity, db_entity)
    destination_feature_class = destination_feature_class_creator.dynamic_model_class()

    # For a destination feature table is a primary geography and gets its data from a parent ConfigEntity
    # (e.g. Project from Region) we need to create the Geography table for the scope of this feature table
    # (e.g. for the Project scope) and populate it with the destination feature table's geographies
    is_primary_geography = get_property_path(db_entity, 'feature_class_configuration.primary_geography')
    if is_primary_geography:
        create_and_populate_geography_associations(db_entity, destination_feature_class)

    source_feature_class_creator = FeatureClassCreator(config_entity, source_db_entity)
    source_feature_class = source_feature_class_creator.dynamic_model_class()

    # Force modeling of the geography classes if not already
    source_feature_class_creator.dynamic_geography_class()
    destination_feature_class_creator.dynamic_geography_class()

    # Find all scopes between the destination feature table and the source feature table, inclusively.

    # For the destination feature table, we create an geography association table for each scope that has
    # up to but not including GlobalConfig. Skip tables scopes with no primary geography and thus no geography table.
    # The association table is named [destination feature table name]_geography_[scope id], where
    # the scope id is that of the config_entity of that scope.
    destination_config_entity_geography_scopes = destination_feature_class_creator.geography_scopes(with_existing_tables_only=True)

    def geography_association(scope):
        """
            Defines our geography relationships for a certain geography scope
            The relationship being defined is:
            destination_feature_table <- destination_feature_table_geography_[scope_id] -> scope_geography_table
            The destination_feature_table_geography_[scope_id] is an association between the other two tables.
            It's columns are a foreign key to the destination_feature_table and a foreign key to the
            scope_geography_table.
            How the rows are filled depends on the geography scope. If the scope is that of the source_feature_class
            or higher then we can simply copy the rows from the source_feature_class's corresponding geography
            association table. However if the scope is lower than the source's geography_scope we have to fill
            the destination's geography association as if the source didn't exist
        """
        scope_feature_class_configuration = FeatureClassCreator(scope, no_ensure=True)
        return [
            'geographies_%s' % scope.id,
            dict(source=
                dict(
                    # Join this scope's geography.wkb_geometry table/column joined to the primary geography
                    # feature class for that scope's table's geometry column
                    # Notice that we don't use the source_feature_class because it won't have a relationship
                    # to geography tables at scopes below it
                    related_class_name=scope_feature_class_configuration.dynamic_geography_class_name(),
                    related_class_join_field_name='wkb_geometry',
                    # Indicate that we can use the source_feature_class if the scope is at or above
                    # that of the source feature class. Otherwise leave None to indicate that we
                    # have to populate the geography association table as if no source existed
                    source_class=source_feature_class if\
                        scope in source_feature_class_creator.geography_scope.ascendants() else\
                        None,
                    source_class_join_field_name='geometry',
                ),
                destination=
                dict(
                    # Join this scope's geography.wkb_geometry table/column joined to the
                    # destination_feature_class
                    # table's geometry column
                    related_class_name=destination_feature_class_creator.dynamic_geography_class_name(scope.id),
                    related_class_join_field_name='wkb_geometry',
                    source_class=destination_feature_class,
                    source_class_join_field_name='geometry',
                ),
                # We need this below if the source_class is None above
                scope=scope
            )]
    # Copies any _geography association tables from the source's _geography table(s) to the destination's
    # Also copies any other manyToMany association tables
    # Note that no population of ForeignKey fields happens here, since that data is stored in the feature_class rel table
    # Note that for primary geographies we've already populated the feature table's geographies table, so we don't
    # need to do it here.
    for related_field_name, related_field_configuration in merge(
            # Defines the [destination's feature table name]_geographies association table,
            # which associates the destination's features with geography table at its scope.
            # If the source table is the same scope, we simply pull rows from the source's geographies association
            # table and insert them into the destination's geographies association table.
            # If the source table is a higher scope (it can't be lower) then we'll create another geographies
            # association table for that higher scope and all scopes in between.
            map_to_dict(
                geography_association,
                destination_config_entity_geography_scopes
            ),
            # Non-geo ManyToMany relationships
            map_dict_to_dict(
                lambda related_field_name, source_related_field_configuration:
                    [related_field_name,
                     dict(source=merge(
                             source_related_field_configuration,
                             dict(source_class=source_feature_class)),
                          destination=merge(
                             source_related_field_configuration,
                             dict(source_class=destination_feature_class)))
                     ],
                filter_dict(
                    lambda related_field_name, related_field_configuration: not related_field_configuration.get('single', None),
                    db_entity.feature_class_configuration.related_fields or {}
                )
            )
    ).items():

        if related_field_configuration['source']['source_class']:
            # If we defined a source_class we can safely fill the geography association from the source's corresponding
            # geography association table
            fill_geography_association_from_source(
                source_feature_class,
                destination_feature_class,
                related_field_configuration,
                related_field_name,
                no_populate)
        else:
            # We have to fill the geography association table directly because the source doesn't have a corresponding
            # geography association table at this geography scope (because the scope is below the source's geography
            # scope). Just use the normal populate_geography_association as if no source exists
            populate_geography_association(related_field_configuration['scope'], db_entity, destination_feature_class)


def _get_default_columns_and_values(feature_class, columns=[], skip_primary_key=False):
    """
        Retrieves the default values for the given columns.
    :param feature_class:
    :param columns:
    :return: Two strings. The first is the list of columns, the second is the defaults of those columns
    """
    default_django_fields = filter(
                                 lambda field: field.column not in columns and
                                               field.model == feature_class and
                                               not (skip_primary_key and field.primary_key),
                                 feature_class._meta.fields)
    default_columns = ''
    column_defaults = ''
    for field in default_django_fields:
        if field.null:
            continue
        default_columns += field.column + ", "
        if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            column_defaults += "'" + str(datetime.now()) + "', "
        else:
            column_defaults += "'" + str(field.default) + "', "

    default_column_string = default_columns[:-2]
    column_default_string = column_defaults[:-2]
    return default_column_string, column_default_string


class DeleteImportProcessor(ImportProcessor):
    """
        Processes every db_entity equally by dropping its feature and layer_selection table data
    """
    def _call_delete_function(self, config_entity, db_entity):
        if self.kwargs.get('drop_rel_only', False):
            # Just drop the rel table so the values can be recreated by the importer
            return self.drop_data(config_entity, db_entity, drop_rel_only=True)
        elif self.kwargs.get('drop_all', False):
            # Drop the base table and rel table, requiring a full reimport after
            return self.drop_data(config_entity, db_entity)

    def importer(self, config_entity, db_entity):
        self._call_delete_function(config_entity, db_entity)

    def peer_importer(self, config_entity, db_entity, filter_query=None):
        self._call_delete_function(config_entity, db_entity)

    def cloner(self, config_entity, db_entity):
        self._call_delete_function(config_entity, db_entity)

    def drop_data(self, config_entity, db_entity, drop_rel_only=False):
        """
            Drop all feature tables related to the db_entity in order to reimport, remove the db_entity, etc.
        :param config_entity:
        :param db_entity:
        :param drop_rel_only: Default False, drop just the rel table and not the base table or geo tables
        :return:
        """
        feature_class_configuration = db_entity.feature_class_configuration
        if not feature_class_configuration:
            return

        try:
            feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()

            related_field_through_classes = map_dict(
                lambda name, related_descriptor: related_descriptor.through,
                filter_dict(lambda name, related_descriptor:
                            isinstance(related_descriptor, ReverseManyRelatedObjectsDescriptor),
                            FeatureClassCreator(config_entity, db_entity).related_descriptors()))

            # If True don't drop in geo tables
            if drop_rel_only:
                geographic_classes_to_drop = []
            else:
                # Drop geographic association classes. We never drop the primary Geogrpahy tables
                feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
                geographic_classes_to_drop = geography_associations_to_drop(db_entity, feature_class)

            # Drop geo tables and related field through class tables
            drop_tables_for_dynamic_classes(*
                geographic_classes_to_drop +
                related_field_through_classes
            )

            # Drop the main (optionally) and the rel feature table
            drop_tables_for_dynamic_classes(*
                [feature_class] +
                ([feature_class.__base__] if not drop_rel_only else [])
            )
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            readable_exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logger.warn("Failed to drop class/table: %s" % readable_exception)


def on_config_entity_pre_delete_data_import(sender, **kwargs):
    """
        Delete data for removing or reimporting
        :param kwargs: db_entity_keys - optional filter to limit deletes
    """
    process_db_entities(
        **merge(
            dict(import_processor=DeleteImportProcessor, drop_all=True, deleted=True),
            kwargs))


def geography_associations_to_drop(db_entity, feature_class):
    """
        Only for unit tests deletes. Returns association tables between the Feature class table
        and its primary Geography tables. This has no effect on Primary geography
        Feature class tables
    :param db_entity:
    :param feature_class:
    :return:
    """
    feature_class_creator = FeatureClassCreator(feature_class.config_entity, db_entity)

    # First, if the db_entity is a primary_geography we need to fill the geography
    # table for this db_entity's geography_scope with the features of this db_entity
    if db_entity.feature_class_configuration.primary_geography:
        logger.error("Cannot delete geography associations of a primary Geogrpahy Feature class")
        return

    # Ensure dynamic models are loaded in memory
    feature_class_creator.dynamic_geography_classes

    logger.info("Finding geography association tables to drop for the following geography scopes: %s" %
                '.'.join(map(lambda config_entity: str(config_entity.id), feature_class_creator.geography_scopes())))
    return map(
        lambda config_entity_geography_scope: geography_association_to_drop(config_entity_geography_scope, db_entity, feature_class),
        feature_class_creator.geography_scopes())

def geography_association_to_drop(config_entity_geography_scope, db_entity, feature_class):
    """
        Used only in unit tests to delete association tables between a Feature class
        and its Primary geographies
    :param config_entity_geography_scope:
    :param db_entity:
    :param feature_class:
    :return:
    """

    geography_class = FeatureClassCreator(config_entity_geography_scope, no_ensure=True).dynamic_geography_class()
    if db_entity.feature_class_configuration.primary_geography:
        logger.error("Cannot delete association tables of Primary geography Feature class")
        return

    related_field_configuration = dict(
            source_class_join_field_name='wkb_geometry',
            related_class_join_field_name='geometry'
    )
    related_field_name = 'geographies_%s' % config_entity_geography_scope.id
    relationship = ManyJoinRelationship(feature_class, related_field_name, related_field_configuration)
    return relationship.through_class
