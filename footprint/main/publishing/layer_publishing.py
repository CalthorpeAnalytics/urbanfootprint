
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

# from memory_profiler import profile
import copy
import logging

from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError, reset_queries
from django.db.models.signals import post_save
from django.dispatch import Signal

from footprint.client.configuration import resolve_fixture
from footprint.client.configuration.fixture import LayerConfigurationFixture
from footprint.main.lib.functions import map_to_dict, merge, remove_keys, unique, one_or_none, filter_keys
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.model_utils import model_dict
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.keys.permission_key import DbEntityPermissionKey
from footprint.main.models.presentation.presentation_configuration import LayerConfiguration
from footprint.main.publishing import tilestache_publishing
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.layer_initialization import LayerLibraryKey
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.models.config.scenario import Scenario, FutureScenario, BaseScenario
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer, \
    drop_layer_selection_table
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.utils.utils import resolvable_module_attr_path
from footprint.main.utils.subclasses import receiver_subclasses

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

# All initial signals. They can run without dependencies
# All signals that can run after layers
post_save_layer_initial = Signal(providing_args=[])


def dependent_signal_paths(signal_path):
    """
        Gives the hierarchy of publisher signal calling order based on the given signal
        Signals are given as strings instead of paths for serialization ease
        param: signal_path. The signal path for which the dependent signals are returned
        return: An array of signal_paths or an empty array
    """
    return []

# Very wild guess about layer saving proportional times to send to the client
# These represent the parsed signal names sent to the client after the dependencies of
# the signal finish running
signal_proportion_lookup = dict(
    # initial signal after save
    post_save_layer_initial=1
)


def on_layer_post_save_process_layer(sender, **kwargs):
    """
        For layer create/update/clone, this updates the saved layer
    """
    from footprint.client.configuration.fixture import LayerConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture

    layer = InstanceBundle.extract_single_instance(**kwargs)

    logger.info("Handler: No Post Save Publising %s" % layer._no_post_save_publishing)
    if layer._no_post_save_publishing:
        return

    db_entity_interest = layer.db_entity_interest
    db_entity = db_entity_interest.db_entity
    config_entity = db_entity_interest.config_entity.subclassed

    logger.info("Handler: Layer Publishing. on_layer_post_save_process_layer %s for config entity %s and db_entity %s" %
                (layer.full_name, config_entity.name, db_entity.key))

    layer_configuration_fixture = resolve_fixture(
        "presentation",
        "layer",
        LayerConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    # Update the layer via the layer library update_or_create
    # Find LayerLibraries matching the ConfigEntity class schope
    for layer_library_configuration in layer_configuration_fixture.layer_libraries():

        logger.info("Handler: Layer Configuration: %s" % layer_library_configuration)
        # Update/Create the layer library and layers
        _update_or_create_layer_library_and_layers(
            config_entity,
            layer_library_configuration,
            db_entity_keys=[db_entity.key])


def on_layer_post_save_db_entity_process_layer(sender, **kwargs):
    """
        For db_entity create/update/clone, this creates or updates the layer
    """
    from footprint.client.configuration.fixture import LayerConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture

    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    config_entity = db_entity_interest.config_entity.subclassed
    db_entity = db_entity_interest.db_entity

    logger.info("Handler: on_layer_post_save_db_enitty_process_layer for DbEntity: key %s, id %s" % (db_entity.key, db_entity.id))
    # Return if the db_entity was not created from an user imported feature
    # Configured layer saving is handled by after saving the ConfigEntity
    if not db_entity.feature_class_configuration.generated:
        return

    layer_configuration_fixture = resolve_fixture(
        "presentation",
        "layer",
        LayerConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    # Update the layer via the layer library update_or_create
    # Find LayerLibraries matching the ConfigEntity class schope
    for layer_library_configuration in layer_configuration_fixture.layer_libraries():

        logger.info("Handler: Layer Library Configuration: %s" % layer_library_configuration)
        # Update/Create the layer library and layers
        _update_or_create_layer_library_and_layers(
            config_entity,
            layer_library_configuration,
            db_entity_keys=[db_entity.key])


def post_save_layer_initial_publishers(cls):
    """
        Run layer processing and then tilestache
    """
    post_save_layer_initial.connect(on_layer_post_save_process_layer, cls, True, "process_on_layer_post_save")
    post_save_layer_initial.connect(tilestache_publishing.on_layer_post_save_tilestache, cls, True,
                                    "tilestache_on_layer_post_save")


# Register receivers for just Scenarios, since they are the only ones that have layers
# This is the config_entity of the layer's DbEntityInterest
for cls in [FutureScenario, BaseScenario, Project, Region, GlobalConfig]:
    post_save_layer_initial_publishers(cls)


def _update_or_create_child_layers(config_entity, db_entity_key):
    # TODO this code is all out of date and will hopefully be replaced with something cleaner
    if not isinstance(config_entity, Scenario):
        logger.debug("_update_or_create_child_layers: db_entity_key %s, config_entity %s" % (db_entity_key, config_entity.name))

        # If our DbEntityInterest.config_entity is not a Scenario, we need to do a bit of trickery
        # to find the Scenario that created the layer. Then we need to clone the layer to the other Scenarios
        some_layers = Layer.objects.filter(
            presentation__config_entity__in=config_entity.children(),
            db_entity_interest__db_entity__key=db_entity_key)
        if len(some_layers) == 0:
            # We have a problem. The layer should exist for at least one scenario
            raise Exception("Layer expected to exist for db_entity %s, but does not" % db_entity_key)
        template_layer = some_layers[0]
        # Create layers that don't exist
        Layer._no_post_save_publishing = True
        logger.info("Updating layer for children of %s" % config_entity.name)

        def update_layer_of_scenario(scenario):
            logger.info("Updating layer of db_entity_key %s, Scenario %s" % (db_entity_key, scenario.name))
            db_entity_interest = DbEntityInterest.objects.get(config_entity=scenario, db_entity__key=db_entity_key)
            return Layer.objects.update_or_create(
                db_entity_interest=db_entity_interest,
                defaults=merge(
                    remove_keys(model_dict(template_layer), ['db_entity_key']),
                )
            )[0]

        layers = map(
            update_layer_of_scenario,
            config_entity.children())

        Layer._no_post_save_publishing = False
    else:
        layers = Layer.objects.filter(
            presentation__config_entity=config_entity,
            db_entity_key=db_entity_key)
        if len(layers) != 1:
            # We have a problem. The layer should exist
            raise Exception("Layer expected to exist for db_entity %s, but does not" % db_entity_key)
    return layers


def on_db_entity_post_save_layer(sender, **kwargs):

    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    if db_entity_interest.db_entity.source_db_entity_key:
        # No layers related to DbEntity results, so just quit
        return
    config_entity = db_entity_interest.config_entity.subclassed

    scoped_config_entities = [config_entity] if isinstance(config_entity, Scenario) else config_entity.children()
    layer_exists = Layer.objects.filter(
        db_entity_interest=db_entity_interest,
        presentation__config_entity__in=scoped_config_entities
    ).exists()
    logger.info(
        "Handler: on_db_entity_post_save_layer for config_entity {config_entity}, db_entity {db_entity}, and user {username}.".format(
            config_entity=config_entity,
            db_entity=db_entity_interest.db_entity,
            username=db_entity_interest.db_entity.updater.username,
        ))
    if not layer_exists:
        return


@receiver_subclasses(post_save, Layer, "layer_post_save")
def on_layer_post_save(sender, **kwargs):
    """
        Called after a Layer saves, but not when a config_entity is running post_save publishers
        In other words, this is only called after a direct Layer save/update.
        This does the same as on_config_entity_post_save_layer, but starts with the 'post_save_es'
        signal to do only DbEntity dependent publishing.
    """
    layer = kwargs['instance']
    if layer._no_post_save_publishing:
        return
    config_entity = layer.config_entity

    db_entity_interest = \
        config_entity.computed_db_entity_interests(db_entity__key=layer.db_entity_key, with_deleted=True)[0]

    if db_entity_interest.deleted:
        # If the db_entity_interest is deleted, make sure the layer is deleted.
        layer.deleted = True
        layer._no_post_save_publishing = True
        layer.save()
        layer._no_post_save_publishing = False
        return

    db_entity = db_entity_interest.db_entity
    user = layer.updater if layer.updater else get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)
    # post_save_db_entity publishing should always be disabled if we are saving a ConfigEntity
    logger.info(
        "Handler: post_save_layer for config_entity {config_entity}, db_entity {db_entity}, and user {username}.".format(
            config_entity=config_entity,
            db_entity=db_entity,
            username=user.username,
        ))

    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_layer_initial')

    try:
        # Make sure no transactions are outstanding
        transaction.commit()
    except Exception, e:
        pass

    return post_save_publishing(
        starting_signal_path,
        config_entity,
        user,
        instance=layer,
        instance_key=db_entity.key,
        signal_proportion_lookup=signal_proportion_lookup,
        dependent_signal_paths=dependent_signal_paths,
        signal_prefix='post_save_layer'
    )


def on_config_entity_post_save_layer(sender, **kwargs):
    """
        Sync tilestache to a ConfigEntity class after the latter is saved
        :param **kwargs: optional "db_entity_keys" to limit the layers created to those DbEntities
    """
    from footprint.client.configuration.fixture import LayerConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture
    # Disable post save publishing on individual layers. The ConfigEntity is controlling publishing
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_save_layer for %s" % config_entity.full_name)

    #    Create LayerLibrary instances based on each LayerLibrary configuration if the configuration's scope
    #    matches that of config_entity
    client_layer_fixture = resolve_fixture(
        "presentation",
        "layer",
        LayerConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    layer_library_configurations = FixtureList(client_layer_fixture.layer_libraries()).matching_scope(
        class_scope=config_entity.__class__
    )
    logger.info("Processing LayerLibrary Configurations %s" % ', '.join(map(
        lambda layer_library_configuration: layer_library_configuration.key,
        layer_library_configurations)))

    for layer_library_configuration in layer_library_configurations:
        _update_or_create_layer_library_and_layers(config_entity, layer_library_configuration, **kwargs)

    reset_queries()


def update_or_create_layer_library_and_layers(config_entity, **kwargs):
    #    Create LayerLibrary instances based on each LayerLibrary configuration if the configuration's scope
    #    matches that of config_entity
    client_layer_fixture = resolve_fixture(
        "presentation",
        "layer",
        LayerConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    layer_library_configurations = FixtureList(client_layer_fixture.layer_libraries()).matching_scope(
        class_scope=config_entity.__class__
    )
    logger.info("Processing LayerLibrary Configurations %s" % ', '.join(map(
        lambda layer_library_configuration: layer_library_configuration.key,
        layer_library_configurations)))

    for layer_library_configuration in layer_library_configurations:
        _update_or_create_layer_library_and_layers(config_entity, layer_library_configuration, **kwargs)


def _update_or_create_layer_library_and_layers(config_entity, layer_library_configuration, **kwargs):
    """
        Update or create the LayerLibrary for the given config_entity and configuration.
        Also create update or create all layers of that library unless limited by kwargs['db_entity_keys']
        :param kwargs: 'db_entity_keys': Optional list to limit layer update/create to those DbEntities
    """

    logger.info("Update/Create LayerLibrary %s for %s" % (layer_library_configuration.key, config_entity.full_name))
    layer_library, updated, created = LayerLibrary.objects.update_or_create(
        key=layer_library_configuration.key,
        scope=config_entity.schema(),
        config_entity=config_entity,
        defaults=dict(
            configuration=layer_library_configuration,
            name=layer_library_configuration.name.format(config_entity.full_name),
            description=layer_library_configuration.description.format(config_entity.name)
        )
    )
    logger.info("Updated/Created LayerLibrary %s for %s" % (layer_library_configuration.key, config_entity.full_name))

    db_entity_key_to_layer_configuration = map_to_dict(
        lambda configuration: [configuration.db_entity_key, configuration],
        layer_library_configuration.data.presentation_media_configurations)

    db_entity_keys = kwargs.get('db_entity_keys', None)

    if layer_library_configuration.key != LayerLibraryKey.DEFAULT:
        # The DEFAULT LayerLibrary has already created the layers needed by this LayerLibrary,
        # We only add Layers to this Library if the configuration Layer specifies this Library in its library_keys AND
        # only if adopted Layers are present in the donor's Library. For instance, if a Region level Layer is
        # excluded from the Region's APPLICATION LayerLibrary, it will also be excluded from the Project's
        # APPLICATION LayerLibrary

        # Get all possible layers from the DEFAULT library, and filter out layers that explicitly don't list
        # this LayerLibrary. If a layer's configuration doesn't specify library_keys, assume we want it in all
        # libraries
        layers = filter(
            lambda layer: not layer.configuration.get('library_keys') or layer_library_configuration.key in layer.configuration.get('library_keys'),
            config_entity.presentation_set.filter(key=LayerLibraryKey.DEFAULT).select_subclasses().get().layers_of_owned_db_entities())

    elif db_entity_keys:

        layers = map(
            lambda db_entity_key: update_or_create_layer(
                layer_library,
                db_entity_key_to_layer_configuration.get(db_entity_key),
                db_entity_key=db_entity_key),
            db_entity_keys
        )
    else:
        if not config_entity.origin_instance:
            # Non-cloned ConfigEntity case. Grab
            # Update or create the Layers of the layer_library_configuration
            # TODO does this deal with uploaded layers? Doesn't seem to. Perhaps there's nothing we
            # can do for uploaded layers here
            owned_db_entities = filter(
                lambda db_entity: db_entity_key_to_layer_configuration.has_key(db_entity.key),
                config_entity.owned_db_entities()
            )
            logger.info("Computed DbEntityInterests: %s" % ', '.join(
                map(lambda db_entity_interest: ':'.join([db_entity_interest.db_entity.key, db_entity_interest.db_entity.schema]),
                    config_entity.computed_db_entity_interests())))
            logger.info("Owned DbEntityInterests: %s" % ', '.join(
                map(lambda db_entity_interest: ':'.join([db_entity_interest.db_entity.key, db_entity_interest.db_entity.schema]),
                    filter(
                        lambda db_entity_interest: db_entity_interest.db_entity.schema == config_entity.schema(),
                        config_entity.computed_db_entity_interests()))))

            logger.info("Processing Configured DbEntities: %s" % ', '.join(
                map(lambda db_entity: db_entity.key, owned_db_entities)) if owned_db_entities else 'None'
            )

            layers = map(
                lambda db_entity: update_or_create_layer(
                    layer_library,
                    db_entity_key_to_layer_configuration[db_entity.key]),
                owned_db_entities
            )
        else:
            # If this is a cloned config_entity, create layers based on those of the origin config_entity
            # TODO, once a config_entity is fully cloned it should stop doing this operation based on the
            # origin config_entity
            owned_db_entities = filter(
                lambda db_entity: db_entity_key_to_layer_configuration.has_key(db_entity.key),
                config_entity.owned_db_entities()
            )
            logger.info("Processing Layers of Configured DbEntities: %s" % ', '.join(
                map(lambda db_entity: db_entity.key, owned_db_entities)) if owned_db_entities else 'None'
            )
            # Update or create each Layer by mapping the DbEntity to the LayerConfigurationFixture
            # Uploads won't map to anything and will be null. We'll use a layer upload configuration for them

            layers = map(
                lambda db_entity: update_or_create_layer(
                    layer_library,
                    db_entity_key_to_layer_configuration.get(db_entity.key)),
                owned_db_entities
            )
    logger.info("Updating layers in layer library: %s" % layer_library.key)
    # Add Layers to the Library if not present
    key_to_layer_lookup = map_to_dict(
        lambda layer: [layer.db_entity_key, layer],
        layer_library.layers.all())
    layers_to_add = filter(lambda layer: layer.db_entity_key not in key_to_layer_lookup, layers)
    layer_library.add_presentation_media(*layers_to_add)

    return layer_library


def update_or_create_layer(layer_library, layer_configuration=None, db_entity_key=None, skip_layer_selection=False):
    """
        Create a Layer for each DbEntity in the LayerConfiguration, These instances constitute the default
        LayerLibrary of the config_entity, which is a library of all DbEntities. The media of these instances can be set
        to style media.
    :param layer_configuration: Optional. A full configuration
    :param db_entity_key. Optional. Use instead of full configuration to generate defaults
    :return:
    """

    # Turn off all layer post_save_publishing, otherwise saving the layer below would infinitely recurse
    # The only layer save that triggers on_layer_post_save is an independent save of a layer.
    # The code here is called by that or by the on_config_entity_post_save layer
    Layer._no_post_save_publishing = True

    db_entity_key = db_entity_key or layer_configuration.db_entity_key
    owning_db_entity_interest = DbEntityInterest.objects.get(
        config_entity=layer_library.config_entity,
        db_entity__key=db_entity_key)

    existing_layer = one_or_none(
        Layer.objects.filter(
            db_entity_interest=owning_db_entity_interest)
    )

    if not layer_configuration:
        layer_configuration = resolve_layer_configuration(
                layer_library.config_entity_subclassed,
                db_entity_key, existing_layer)

        logger.info("Layer configuration %s" % layer_configuration)

    # Resolve the active DbEntity of the ConfigEntity based on the key of the LayerConfiguration
    db_entity_key = layer_configuration.db_entity_key
    logger.info("Layer Publishing DbEntity Key: %s" % db_entity_key)

    try:
        db_entity = layer_library.config_entity_subclassed.computed_db_entities().get(key=db_entity_key)
    except Exception, e:
        raise Exception(
            "db_entity_key {0} does not exist for config_entity {1}. Did you configure the LayerConfiguration for the wrong scope? Original exception: {2}".format(
                db_entity_key, layer_library.config_entity_subclassed, e.message))

    # The key is based on the base class of the db_entity_key if one exists
    # If no matching layer style is found use the default Medium
    config_entity = layer_library.config_entity_subclassed
    # This serves as the default LayerStyle of the Layer, which can later be customized (e.g. a user can specify
    # specific colors and other stylistic data)
    layer_style = layer_configuration.layer_style
    logging.debug("Layer Style: %s" % layer_style)
    # Customize the  medium_context to have a class that refers specifically to this db_entity_key
    # This class name must match the style applied to the mml

    owning_db_entity_interest = DbEntityInterest.objects.get(
        config_entity=config_entity,
        db_entity__key=db_entity_key)

    dummy_user = get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)

    layer, created, updated = Layer.objects.update_or_create(
        db_entity_interest=owning_db_entity_interest,
        defaults=dict(
            # The name by default matches the DbEntity
            name=db_entity.name,
            configuration=dict(
              built_form_set_key=layer_configuration.built_form_set_key,
              sort_priority=layer_configuration.sort_priority if layer_configuration.sort_priority > 0 else 100,
              attribute_sort_priority=layer_configuration.attribute_sort_priority,
              column_alias_lookup=layer_configuration.column_alias_lookup,
              library_keys=layer_configuration.library_keys
            ),
            visible=layer_configuration.visible,
            creator=dummy_user,
            updater=layer_configuration.creator if hasattr(layer_configuration, 'creator') else get_user_model().objects.filter()[0],
        )
    )
    # this will update or create the layer style and assign it to the layer
    update_or_create_layer_style_from_configuration(layer_library.config_entity, db_entity, layer, layer_configuration)

    if not skip_layer_selection:
        # Update or create the LayerSelection tables and instances for this layer
        update_or_create_layer_selections_for_layer(layer)

    Layer._no_post_save_publishing = False

    layer.invalidate()

    return layer


def on_layer_style_save():
    """
    respond to any changes in style
    :return:
    """


def on_scenario_feature_save(sender, **kwargs):
    """
    this method will call the layer invalidation after a scenario has been edited
    :param sender:
    :param kwargs:
    :return:
    """
    scenario = kwargs['instance']
    changed_layers = scenario.layers.filter(db_entity_key__in=1)


def update_or_create_layer_selections(layer_libraries=None, config_entity=None, layers=None, users=None):
    """
        Update or create the LayerSelection subclass for each Layer, or for Layers of the
        given LayerLibrary, or for the Layers explicitly specified. Each Layer has its
        own LayerSelection subclass so that the subclass can easily point at the Feature
        subclass specific to the Layer. If users are specified, create a LayerSelection instance
        for each specified user. If a user does not have permission to view the Layer's DbEntity or ConfigEntity,
        an exception will be thrown
    :param layer_libraries: Optional. Limit work Layers in these LayerLibraries
    :param config_entity: Optional. Limit Layers to those of LayerLibraries in this config_entity
    :param layers: Optional. Limit Layers those specified here
    :param users: Optional. The permitted users for which to create LayerSelection instances.
    By default none are created.
    :par
    :return:
    """
    if not layers:
        layer_libraries_of_config_entity = layer_libraries if layer_libraries else LayerLibrary.objects.filter(
            config_entity=config_entity)
        # For all unique layers (they might be shared by libraries) configure layer_selection tables
        layers = Layer.objects.filter(presentation__in=layer_libraries_of_config_entity)
    # Create a layer_selection class for the layer if it is selectable
    for layer in layers:
        update_or_create_layer_selections_for_layer(layer, users=users)


def update_or_create_layer_selections_for_layer(layer, users=None):
    """
        Create LayerSelections for all users for this layer.
        :param layer: The Layer instance
        :param users: Optional users for which to create LayerSelection instances. These
        users must have permission to read the DbEntity and ConfigEntity of the Layer, or
        an exception will be thrown
    """

    # Do nothing if the layer doesn't have features, such as background imagery
    if not layer.db_entity_interest.db_entity.feature_class_configuration:
        return

    layer_selection_class = get_or_create_layer_selection_class_for_layer(layer)
    if layer_selection_class and users:
        logger.info("Getting/Creating LayerSelection instances for Layer of DbEntity Key: %s" % layer.full_name)
        for authorizable_instance in [layer.config_entity.subclassed,
                                      layer.db_entity_interest.db_entity]:
            # This will raise an Exception if there any unauthorized users
            authorizable_instance.validate_permissions(users, permission_key_class=DbEntityPermissionKey)

        # Create an instance for each user in the list
        for user in users:
            if not layer_selection_class.objects.filter(user=user).count():
                layer_selection_class.objects.create(user=user)

def resolve_layer_configuration(config_entity, db_entity_key, layer):
    """
        Creates a LayerConfiguration for imported layers using the template
        LayerConfigurations designed in the LayerConfigurationFixture.import_layer_configurations
    """
    from footprint.client.configuration.fixture import LayerConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture

    # if a layer exists and it has a layer configuration update it
    if layer and layer.configuration:
        layer_configuration = LayerConfiguration(
            **merge(
                dict(
                    db_entity_key=layer.db_entity_key,
                    layer_library_key=layer.key,
                    visible=layer.visible,
                    # Convert the LayerStyle to a dict, which is what a LayerConfiguration expects, and wipe out the ids
                    layer_style=model_dict(layer.medium)
                ),
                dict(
                    built_form_set_key=layer.configuration.get('built_form_key', None),
                    sort_priority=layer.configuration.get('sort_priority', None),
                    attribute_sort_priority=layer.configuration.get('attribute_sort_priority', None),
                    column_alias_lookup=layer.configuration.get('column_alias_lookup', None),
                ) if layer.configuration else dict()
            )
        )
    # if the the layer configuration doesn't exist, utilize the default layer configuration
    else:
        client_layer_configuration = resolve_fixture(
            "presentation",
            "layer",
            LayerConfigurationFixture,
            config_entity.schema(),
            config_entity=config_entity)

        geometry_type = config_entity.db_entity_by_key(db_entity_key).geometry_type
        layer_configuration = copy.copy(list(client_layer_configuration.import_layer_configurations(geometry_type))[0])
        # Update the template LayerConfiguration to our db_entity_key
        layer_configuration.db_entity_key = db_entity_key

    return layer_configuration


def on_post_save_built_form_layer(sender, **kwargs):
    """
        A signal handler to redo styles on relevant layers after a BuiltForm instances is created or updated.

    """
    built_forms = kwargs['instance']
    # Assume all are the same class
    built_form_class_name = built_forms[0].__class__.__name__
    if built_form_class_name in ['CropType', 'LandscapeType']:
        built_form_dependent_db_entity_keys = [DbEntityKey.FUTURE_AGRICULTURE, DbEntityKey.BASE_AGRICULTURE]
    elif built_form_class_name in ['BuildingType', 'PlaceType']:
        built_form_dependent_db_entity_keys = [DbEntityKey.END_STATE, DbEntityKey.BASE_CANVAS]
    else:
        built_form_dependent_db_entity_keys = []

    # Find all DbEntities that reference built_form.
    layer_libraries = LayerLibrary.objects.filter(deleted=False)
    for layer_library in layer_libraries:
        # Find the corresponding layers of all LayerLibrary instances
        existing_layers = layer_library.layers.filter(db_entity_key__in=built_form_dependent_db_entity_keys)
        # Turn off post save publishing for layers. The built_form_publisher will do tilestache saves explicitly
        # The only purpose of this is to get better progress indicators. It won't be needed when we redo progress signals later
        # Invalidate these layers
        for existing_layer in existing_layers:
            update_or_create_layer(layer_library, db_entity_key=existing_layer.db_entity_key, skip_layer_selection=True)


def delete_layer_selections(layers):
    for config_entity in unique(map(lambda layer: layer.config_entity, layers)):
        FeatureClassCreator(config_entity).ensure_dynamic_models()
    for selection_layer in layers:
        try:
            # Drop the table
            layer_selection_class = get_or_create_layer_selection_class_for_layer(selection_layer, no_table_creation=True)

            if layer_selection_class:
                if hasattr(layer_selection_class.features, 'through'):
                    layer_selection_features_class = layer_selection_class.features.through
                    drop_layer_selection_table(layer_selection_features_class)
                drop_layer_selection_table(layer_selection_class)

        except DatabaseError, e:
            logger.warning(
                "Couldn't destroy LayerSelection tables. Maybe the public.layer table no longer exists: %s" % e.message)


def create_layer_selections(layers):
    """
        Create LayerSelection classes and instances for the given Scenario subclasses among the
        classes in limit_to_classes. Also filters by db_entity_key if they are specified
    :return:
    """
    for config_entity in unique(map(lambda layer: layer.config_entity, layers)):
        FeatureClassCreator(config_entity).ensure_dynamic_models()
    for selection_layer in layers:
        # Recreate
        get_or_create_layer_selection_class_for_layer(selection_layer)
    update_or_create_layer_selections(config_entity=None)


def update_or_create_layer_style_from_configuration(config_entity, db_entity, layer, layer_configuration):
    """
        Iterates through the LayerConfiguration and creates LayerStyle instances for each that contain default
        styling for the configured attributes
    :return:
    """

    # Find the corresponding config_entity_fixture, or parent fixture if it doesn't exist
    layer_fixture = resolve_fixture(
        "presentation",
        "layer",
        LayerConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    logger.info("Configuring Layer Media for %s. Processing Layer Configurations" % config_entity.full_name)
    logger.info("Config Entity %s. layer_configuration %s. layer %s" % (config_entity, layer_configuration.__dict__, layer))

    layer_fixture.update_or_create_layer_style(config_entity, layer_configuration, layer)
