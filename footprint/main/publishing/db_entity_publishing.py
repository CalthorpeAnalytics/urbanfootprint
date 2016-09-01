
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

from django.contrib.auth import get_user_model
from django.db import reset_queries, connections
from django.db.models.signals import post_save
from django.dispatch import Signal

from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.config.scenario import FutureScenario, BaseScenario
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.model_utils import model_dict
from footprint.main.publishing import data_import_publishing, layer_publishing, result_publishing, analysis_module_publishing, user_publishing, tilestache_publishing
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.publishing.crud_key import CrudKey
from footprint.main.publishing.data_import_publishing import DefaultImportProcessor
from footprint.main.publishing.geo_json_processor import GeoJsonProcessor
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.origin_db_entity_processor import OriginDbEntityProcessor
from footprint.main.publishing.zipped_sql_file_processor import ZippedSqlFileProcessor
from footprint.main.utils.subclasses import receiver_subclasses
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.database.information_schema import PGNamespace
from footprint.main.lib.functions import  merge, remove_keys, filter_keys
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.config.interest import Interest
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.utils import resolvable_module_attr_path, full_module_path


__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

# All initial signals. They can run without dependencies
# All signals that can run after db_entities run
post_save_db_entity_initial = Signal(providing_args=[])
# All signals that can run after data imports run
post_save_db_entity_import = Signal(providing_args=[])


def dependent_signal_paths(signal_path):
    """
        Gives the hierarchy of publisher signal calling order based on the given signal
        Signals are given as strings instead of paths for serialization ease
        param: signal_path. The signal path for which the dependent signals are returned
        return: An array of signal_paths or an empty array
    """
    if signal_path == resolvable_module_attr_path(__name__, 'post_save_db_entity_initial'):
        # DataImport dependent publishers are run after DbEntity dependent publishers
        return [
            resolvable_module_attr_path(__name__, 'post_save_db_entity_import'),
        ]
    return []

# All signals that can run after data imports run
# Very wild guess about db_entity_interest saving proportional times to send to the client
# These represent the parsed signal names sent to the client after the dependencies of
# the signal finish running
signal_proportion_lookup = dict(
    # initial signal after save
    post_save_db_entity_initial=.50,
    # layers and dataImports run in parallel
    post_save_db_entity_import=.50
)

def post_save_db_entity_initial_publishers(cls):
    """
        Data Import and User Configuration can happen after the Initial save
    """
    post_save_db_entity_initial.connect(data_import_publishing.on_db_entity_post_save_data_import, cls, True, "data_import_on_db_entity_post_save")
    post_save_db_entity_initial.connect(user_publishing.on_db_entity_post_save_user, cls, True, "user_on_db_entity_post_save")

def post_save_db_entity_import_publishers(cls):
    """
        Layer and Result presentation depend on data import
    """
    post_save_db_entity_import.connect(result_publishing.on_db_entity_post_save_result, cls, True, "result_on_db_entity_post_save")
    # this will handled in layer_publishing and tilestache publishing post save
    post_save_db_entity_import.connect(layer_publishing.on_layer_post_save_db_entity_process_layer, cls, True, "layer_on_db_entity_post_save")
    post_save_db_entity_import.connect(tilestache_publishing.on_db_entity_post_save_tilestache, cls, True, "tilestache_on_db_entity_post_save")
    post_save_db_entity_import.connect(analysis_module_publishing.on_db_entity_post_save_analysis_modules, cls, True, "analysis_module_on_db_entity_post_save")

# Register receivers for all ConfigEntity classes.
# This is the config_entity of the DbEntityInterest
for cls in [FutureScenario, BaseScenario, Project, Region, GlobalConfig]:
    post_save_db_entity_initial_publishers(cls)
    post_save_db_entity_import_publishers(cls)

def on_config_entity_post_save_db_entity(sender, **kwargs):
    """
        CRUD a ConfigEntity's DbEntities. Called when creating, clone, updating, or syncing a scenario
        Create (kwargs['created']==True). Relies on the client configuration of its DbEntity instance
        Clone (kwargs['created']==True and kwargs['instance'].origin_instance). Relies on the origin instance clone DbEntities
        Update. For now don't do anything. We only expose primitive attributes to the user
        Sync (kwargs['sync']==True). Iterate through the client configuration and update DbEntities according to the configuration.
            For clones sync will sync to the origin instance.
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_save_db_entity. ConfigEntity: %s" % config_entity.name)
    crud_db_entities(config_entity, kwargs.get('crud_type'))

    reset_queries()

@receiver_subclasses(post_save, DbEntityInterest, "db_entity_interest_post_save")
def on_db_entity_interest_post_save(sender, **kwargs):
    """
        Called after a DbEntityInterest saves, but not when a config_entity is running post_save publishers
        In other words, this is only called after a direct DbEntityInterest save/update.
        This does the same as post_save_config_entity, but starts with the 'post_save_config_entity_db_entities'
        signal to do only DbEntity dependent presentation.
    """
    db_entity_interest = kwargs['instance']
    config_entity = ConfigEntity._subclassed(db_entity_interest.config_entity)
    db_entity = db_entity_interest.db_entity
    # TODO The default user should be the admin
    user = db_entity.updater if db_entity.updater else get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)
    # post_save_db_entity presentation should always be disabled if we are saving a ConfigEntity
    logger.info("Handler: post_save_db_entity_interest for config_entity {config_entity}, db_entity {db_entity}, "
                "and user {username}.".format(
        config_entity=config_entity,
        db_entity=db_entity_interest.db_entity,
        username=user.username
    ))

    if kwargs.get('created', None):
        db_entity = db_entity_interest.db_entity
        # TODO
        # While we test upload, just delete the previous DbEntitys with the same key name
        # in the ConfigEntity.
        db_entity_interest.config_entity.db_entities.filter(key=db_entity.key).exclude(id=db_entity.id).delete()

        # Make sure the db_entity's schema matches the config_entity's if not set
        # TODO we assume that the schema should match the config_entity, rather than
        # an ancestor or the config_entity (like the project or a scenario). There
        # are many cases where the schema should not be that of the config_entity, so
        # we might want to remove this default and force the saver to set it
        if not db_entity.schema or not db_entity.table:
            db_entity.schema = db_entity.schema or db_entity_interest.config_entity.schema()
            # Always base the table name on the key
            db_entity.table = db_entity.key
            db_entity_interest.db_entity.save()

    if db_entity_interest.config_entity.deleted:
        # Do nothing for deleted config_entities
        return

    # Define the data_importer if not already set
    if not (db_entity.feature_class_configuration and db_entity.feature_class_configuration.data_importer):
        feature_class_configuration = db_entity.feature_class_configuration = db_entity.feature_class_configuration or FeatureClassConfiguration()
        # Choose the correct importer, if any, to set up the feature_class_configuration and features
        if db_entity.origin_instance:
            # Import from the origin_instance. This could be a full copy or from the current layer selection features
            feature_class_configuration.data_importer = full_module_path(OriginDbEntityProcessor)
        elif '.json' in db_entity.url.lower():
            # Import it using the geojson importer
            feature_class_configuration.data_importer = full_module_path(GeoJsonProcessor)
            # Indicate that the feature class configuration was generated not fixture based
            feature_class_configuration.generated = True
        elif '.zip' in db_entity.url.lower():
            feature_class_configuration.data_importer = full_module_path(ZippedSqlFileProcessor)
            # Indicate that the feature class configuration was generated not fixture based
            feature_class_configuration.generated = True
        elif not db_entity.no_feature_class_configuration:
            feature_class_configuration.data_importer = full_module_path(DefaultImportProcessor)
        previous = DbEntityInterest._no_post_save_publishing
        DbEntityInterest._no_post_save_publishing = True
        db_entity.feature_class_configuration = feature_class_configuration
        db_entity.save()
        DbEntityInterest._no_post_save_publishing = previous

    # Post save presentation section
    # Quit if the publishers were turned off outside this method
    if DbEntityInterest._no_post_save_publishing or db_entity_interest._no_post_save_publishing:
        return

    # Use this to initialize the FeatureBehavior and other stuff that might not be set
    update_or_create_db_entity(config_entity, db_entity)

    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_db_entity_initial')

    return post_save_publishing(
        starting_signal_path,
        config_entity,
        user,
        instance=db_entity_interest,
        instance_class=DbEntity,
        client_instance_path='db_entity',
        instance_key=db_entity_interest.db_entity.key,
        signal_proportion_lookup=signal_proportion_lookup,
        dependent_signal_paths=dependent_signal_paths,
        signal_prefix='post_save_db_entity',
        # Update the setup_percent_complete instance attribute for new instances
        # of classes with this attribute (currently only DbEntity)
        update_setup_percent_complete=db_entity_interest.db_entity.setup_percent_complete == 0,
        **filter_keys(kwargs, ['created'])
    )

def crud_db_entities(config_entity, crud, db_entity_keys=None):
    """
        Creates or updates the db_entities of the ConfigEntity
    :param config_entity
    :param crud CrudKey.CREATE, CrudType.CLONE, CrudType.UPDATE, CrudType.SYNC, CrudType.DELETE (unimplemented)
    :return:
    """
    from footprint.client.configuration.fixture import ConfigEntityFixture
    # If not present, create the database schema for this ConfigEntity's feature table data
    PGNamespace.objects.create_schema(config_entity.schema())
    client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(config_entity)
    db_entity_filter = dict(key__in=db_entity_keys) if db_entity_keys else {}

    # Process the DbEntities from the origin_instance or the db_entity_configuration from the fixtures,
    # but only the first time this scenario is saved
    # We only get those scoped (owned) by the class of our config_entity. The scoped above will be adopted automatically
    # and need not be created. This means a Scenario creates DbEntities scoped to Scenario and adopts those scoped
    # to Project or Region. It does not clone the latter.
    if CrudKey.CLONE == crud:
        # CRUD the DbEntities to match the origin instance
        origin_instance = config_entity.origin_instance
        # Clone the DbEntities from the origin ConfigEntity.
        db_entities = map(
            lambda source_db_entity: clone_or_update_db_entity_and_interest(
                config_entity,
                source_db_entity,
                DbEntity(
                    schema=config_entity.schema(),
                    feature_class_configuration=FeatureClassConfiguration(
                        geography_scope=FeatureClassCreator(config_entity).resolved_geography_scope.id,
                        class_attrs={'config_entity__id': config_entity.id,
                                     'override_db': config_entity.db,
                                     'db_entity_key': source_db_entity.key}
                    )
                )
            ).db_entity,
            origin_instance.owned_db_entities(**db_entity_filter)
        )
    elif crud in [CrudKey.SYNC, CrudKey.CREATE]:
        #TODO examine the two conditions below more carefully. We want syncing to be the same for clones and non-clones
        if config_entity.origin_instance:
            # Syncing previously cloned instance
            db_entities = config_entity.owned_db_entities(**db_entity_filter)
            update_or_create_db_entities_and_interests(config_entity, *db_entities)
        else:
            # Create or Sync new instance
            # Get the default DbEntity configurations from the fixture
            default_db_entities = filter(lambda db_entity: db_entity.key in db_entity_keys if db_entity_keys else True, client_fixture.default_db_entities())
            # Find additional owned (not adopted) db_entities that aren't defaults, namely those that were created by the user
            additional_db_entities = filter(lambda db_entity: db_entity.key in db_entity_keys if db_entity_keys else True, client_fixture.non_default_owned_db_entities())
            # Combine the defaults with the additions
            db_entities = default_db_entities+list(additional_db_entities)
            update_or_create_db_entities_and_interests(config_entity, *db_entities)
    elif CrudKey.UPDATE == crud:
        # No complex updates are enabled for scenarios, so no post-save processing is needed
        return
    elif CrudKey.DELETE == crud:
        raise NotImplementedError("DELETE is not implemented")

    # Disable the post_post_save signal while saving to prevent an infinite loop
    previous = config_entity._no_post_save_publishing
    config_entity._no_post_save_publishing = True
    # Save post_create changes. This is just to store selected DbEntities
    config_entity.save()
    config_entity._no_post_save_publishing = previous

    reset_queries()

def update_or_create_db_entities_and_interests(config_entity, *db_entities):
    """
        Configures saved DbEntities by creating their subclass tables if needed and their DbEntityInterest. This
        is an extension of sync_default_db_entities but is also used by publishers to configure the DbEntities
        that they need that aren't part of the default sets.
        already in a post_config_entity save handler
        :param db_entities: A list of db_entity configurations or db_entities (the latter
        is used if creating a new DbEntity from another)
    :return:
    """

    # Getting ready to create or update DbEntityInterests. Tell the DbEntityInterest post_save handler
    # to NOT start the DbEntity presentation chain. We don't want to run the DbEntity dependent publishers
    # such as Layers and DataImport. The ConfigEntityPublisher will run these itself
    previous = DbEntityInterest._no_post_save_publishing
    DbEntityInterest._no_post_save_publishing = True

    # Do a forced adoption of DbEntityInterests from the parent ConfigEntity. This makes sure that ConfigEntity has
    # the parent's DbEntityInterests before adding any of its own. Otherwise the parent's are never adopted and
    # are created from the db_entity_configurations instead, which is minimally less efficient
    # See _adopt_from_donor docs for an explanation.
    config_entity._adopt_from_donor('db_entities', True)

    db_entity_interests_and_created = map(
        lambda db_entity: update_or_create_db_entity_and_interest(config_entity, db_entity),
        db_entities)

    # Now add the db_entities that were created.
    # They are already associated with the ConfigEntity on creation so this doesn't really do much
    created_db_entity_interests = map(
        lambda tup: tup[0], filter(
            lambda db_entity_interests_and_created: db_entity_interests_and_created[1], db_entity_interests_and_created
        )
    )
    config_entity.add_db_entity_interests(*created_db_entity_interests)

    DbEntityInterest._no_post_save_publishing = previous


def update_or_create_db_entity_and_interest(config_entity, config_db_entity):
    """
        Sync a single db_entity_configuration or db_entity and its db_entity_interest
        :return A tuple of the DbEntityInterest and the created flag
    """
    unique_key_combo = ['key', 'schema']

    db_entity, created, updated = DbEntity.objects.update_or_create(
        # key and schema uniquely identify the DbEntity
        key=config_db_entity.key,
        schema=config_db_entity.schema,
        defaults=remove_keys(model_dict(config_db_entity), unique_key_combo))

    db_entity.feature_behavior = config_db_entity.feature_behavior
    db_entity.save()

    logger.info("ConfigEntity/DbEntity Publishing. DbEntity: %s" % db_entity.full_name)

    # Create the DbEntityInterest through class instance which associates the ConfigEntity instance
    # to the DbEntity instance. For now the interest attribute is hard-coded to OWNER. This might
    # be used in the future to indicate other levels of interest
    interest = Interest.objects.get(key=Keys.INTEREST_OWNER)
    db_entity_interest, created, updated = DbEntityInterest.objects.update_or_create(
        config_entity=config_entity,
        db_entity=db_entity,
        interest=interest)

    #update the geography scope after the db_entity_interest saves as this is required to find 'owned' db_entites in a config entity
    if not db_entity.no_feature_class_configuration:
        feature_class_creator = FeatureClassCreator(config_entity, db_entity, no_ensure=True)
        db_entity.feature_class_configuration.geography_scope = config_entity.id if db_entity.feature_class_configuration.primary_geography \
            else feature_class_creator.resolved_geography_scope.id

        db_entity.save()

    return db_entity_interest, created

def full_name_of_db_entity_table(self, table):
    """
    :param table: the table name of the table that the DbEntity represents
    :return: The combined schema and table name of the given db_entity. This is used to name the dynamic class that is
    created to represent the table
    """
    return '"{0}"."{1}"'.format(self.schema(), table)

def clone_or_update_db_entity_and_interest(config_entity, source_db_entity, db_entity, existing_db_entity_interest=None, override_on_update=False):
    """
        Clones or updates the source_db_entity modified with the given kwargs (including possibly the key) into this ConfigEntity.
        This is used for a duplicate clone from one ConfigEntity (same DbEntity key) to another and also for
        creating a modified DbEntity for a Result from a non-Result DbEntity (different DbEntity key). A third case for this
        method is cloning a DbEntity within a ConfigEntity, which is not yet implemented.

        If the kwargs['override_on_update'] is True, the kwargs should override the target DbEntity attribute values on update.
        This is useful for the Result clone case where we want to pick up updates to the source DbEntity. But in the straight
        clone case we want to make the target DbEntity independent of the source once it is created.
        Returns the DbEntityInterest

        :param: config_entity. The config_entity of the DbEntities
        :param: Optional source_db_entity. The source of the clone
        :param: db_entity. DbEntity of attributes matching the DbEntity that need to override those of the source_db_entity. This might be the
        key, schema, etc.
        Also for db_entity.feature_class_owner, default None, is passed in for Results that are copying
        a reference DbEntity's feature_class_configuration with the db_entity key of the onwer. We don't want the result version of the feature_class_configuration
        to be used to create the feature_class tables, because that would make foreign key references point to the
        wrong feature class parents (which are named by the DbEntity id). phwewww!
        :param: existing_db_entity_interest: Optional DbEntityInterest if it already exists for the clone
        :param: override_on_update: Default False, optional and is described above.
    """

    # Do a forced adoption of DbEntityInterests from the parent ConfigEntity. This makes sure that ConfigEntity has
    # the parent's DbEntityInterests before adding any of its own. Otherwise the parent's are never adopted and
    # are created from the db_entity_configurations instead, which is minimally less efficient
    # See _adopt_from_donor docs for an explanation.
    config_entity._adopt_from_donor('db_entities', True)

    # TODO Update to newer cleaner configuration style
    # key is always resolved by the db_entity or else the source DbEntity key
    key = db_entity.key or source_db_entity.key

    feature_behavior = db_entity._feature_behavior
    if existing_db_entity_interest:
        # Merge existing DbEntity data, including the id. Manually merge feature_behavior since it's not a real
        # property
        db_entity.__dict__.update(
            merge(
                model_dict(existing_db_entity_interest.db_entity, include_primary_key=True),
                dict(_feature_behavior=existing_db_entity_interest.db_entity.feature_behavior)
            )
        )
    if not db_entity._feature_behavior:
        from footprint.main.publishing.config_entity_initialization import get_behavior
        # If we don't already have a feature_behavior get it from the source DbEntity but 0 the id to make a copy
        # We'll also 0 out the Intersection of the FeatureBehavior and pass it to the FeatureBehavior creator
        # If we don't have a source_db_entity then create a default FeatureBehavior
        feature_behavior = source_db_entity.feature_behavior if \
            source_db_entity else  \
            FeatureBehavior(
                behavior=get_behavior('reference')
            )
        feature_behavior.id = None

    # Prefer the db_entity values over those of the source_db_entity
    db_entity.__dict__.update(merge(
        # Start with the source attributes
        model_dict(source_db_entity) if source_db_entity else {},
        # Copy the feature_behavior by assigning it to the temp property _feature_behavior
        # Prefer the FeatureBehavior of the new DbEntity (for the Result case)
        dict(_feature_behavior=feature_behavior),
        # Override with the initial clone overrides or existing clone values.
        model_dict(db_entity),
        # If update_on_override then overwrite the clone with the source values
        # This is for the case of updating the source configuration and wanting to mirror changes to the Result DbEntities
        remove_keys(model_dict(source_db_entity), ['key', 'schema', 'name']) if source_db_entity and override_on_update else {},
        # Set the clone source key if different than the target key
        dict(source_db_entity_key=source_db_entity.key) if source_db_entity and source_db_entity.key != key else {},
        dict(
             # Override feature_class_configuration keys if specified in the kwargs and create_or_update_on_override is True
             feature_class_configuration=FeatureClassConfiguration(**merge(
                # start with the source's attributes
                source_db_entity.feature_class_configuration.__dict__ if source_db_entity else {},
                # override with all those present on the clone if create_or_update_on_override is false, if true add only those unspecified on the source
                # The only exception is abstract_class_name, which must always come from the source
                remove_keys(db_entity.feature_class_configuration.__dict__,
                            source_db_entity.feature_class_configuration.__dict__.keys() if \
                                source_db_entity and override_on_update else \
                                ['abstract_class_name']
                            ),
                # feature_class_owner is set to the owning db_entity key for a Result DbEntity creation so that
                # the result feature_class_configuration doesn't create feature classes/tables
                # We either copy this value from the source feature_class_configuration (clone case) or get it from the kwargs (create Result DbEntity case)
                dict(
                    feature_class_owner=source_db_entity.feature_class_configuration.feature_class_owner if \
                        source_db_entity else \
                        db_entity.feature_class_configuration.feature_class_owner,
                )
             ))
        )
    ))
    # There must be a creator of a new DbEntity. The updater is that of the source DbEntity or simply the creator
    try:
        db_entity.creator = db_entity.creator
    except:
        db_entity.creator = source_db_entity.creator
    logger.debug(db_entity.creator.__class__)
    try:
        db_entity.updater = db_entity.updater
    except:
        db_entity.updater = db_entity.creator
    # Persist the feature_behavior
    FeatureBehavior._no_post_save_publishing = True
    db_entity.update_or_create_feature_behavior(db_entity._feature_behavior)
    # # save to persist the db_entity's knowledge of its behavior
    # db_entity.save()
    FeatureBehavior._no_post_save_publishing = False

    # This will trigger DbEntity post-save publishing, but the only thing that actually
    # runs is UserPublishing in order to give users permission to the DbEntity
    # The other publishers detect that the DbEntity has a source_db_entity_key and quit
    db_entity_interest = update_or_create_db_entity_and_interest(config_entity, db_entity)[0]

    # Copy the categories from the source if it exists
    if source_db_entity:
        db_entity_interest.db_entity.categories.add(*source_db_entity.categories.all())

    return db_entity_interest
