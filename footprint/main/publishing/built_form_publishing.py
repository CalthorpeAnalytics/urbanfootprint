
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


#from memory_profiler import profile
import os
from django.core.management import call_command
from django.db import reset_queries
from django.dispatch import Signal
from footprint.main.initialization.built_form.built_form_importer import BuiltFormImporter
import logging
from footprint.main.lib.functions import remove_keys, flatten, map_property
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.placetype import Placetype
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.models.built_form.agriculture.crop import Crop
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.models.built_form.urban.building import Building
from footprint.main.models.built_form.urban.building_type import BuildingType
from footprint.main.models.built_form.urban.urban_placetype import UrbanPlacetype
from footprint.main.models.built_form.agriculture.landscape_type import LandscapeType
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.region import Region
from footprint.main.models.built_form.built_form_set import BuiltFormSet
from django.conf import settings
from footprint.main.publishing import tilestache_publishing, layer_publishing
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.utils.utils import resolvable_module_attr_path

logger = logging.getLogger(__name__)

# Signal for all initial publishers. They can run without dependencies
post_save_built_form_initial = Signal(providing_args=["agriculture"])
post_save_built_form_layer = Signal(providing_args=["agriculture"])


def post_save_built_form_publishers(cls):
    """
        DbEntity presentation, Analysis Module presentation, and BuiltForm presentation can happen in parallel as soon
        as a config_entity is saved
    """
    post_save_built_form_initial.connect(layer_publishing.on_post_save_built_form_layer, cls,
                                         True, "layer_publishing_on_built_form_post_save")
    post_save_built_form_layer.connect(tilestache_publishing.on_post_save_built_form_tilestache, cls,
                                       True, "tilestache_publishing_on_built_form_post_save")


for cls in [Placetype, PlacetypeComponent, PrimaryComponent, UrbanPlacetype, BuildingType, Building, LandscapeType,
            CropType, Crop]:
    post_save_built_form_publishers(cls)

signal_proportion_lookup = dict(
    post_save_built_form_initial=.5,
    post_save_built_form_layer=.5,
)


def dependent_signal_paths(signal_path):
    if signal_path == resolvable_module_attr_path(__name__, 'post_save_built_form_initial'):
        return [resolvable_module_attr_path(__name__, 'post_save_built_form_layer')]
    return []


# This is started from BuiltForm.post_save
def add_built_forms_to_built_form_sets(built_forms):
    for built_form in built_forms:
        if len(built_form.builtformset_set.all()) == 0 and built_form.origin_instance:
            # If a clone occurred copy the clone into the same BuiltFormSets
            for built_form_set in built_form.origin_instance.builtformset_set.filter(deleted=False):
                logger.info("Adding built_form %s to built_form_set %s" % (built_form.key, built_form_set.key))
                built_form_set.built_forms.add(built_form)


def on_built_form_post_save(sender, **kwargs):

    built_forms = kwargs['instance']

    # For tastypie calls this will already be complete
    # so that built_form_sets come back in the dehydration
    add_built_forms_to_built_form_sets(built_forms)

    built_form_save_aggregates_and_publishing(built_forms)


def built_form_save_aggregates_and_publishing(built_forms):
    """
        Post save starts a chain of asynchronous publishers that run according to a dependency tree.
        First publishers that are wired to the post_save_built_form_initial signal
        run, followed by publishers dependent on signals that are dependent on that signal
        :param built_forms: The BuiltForms
    """

    # Send a message to publishers to configure after creation or update of the config_entity
    # This is executed through a Celery task so that it can run asynchronously
    non_deleted_built_forms = filter(lambda built_form: not built_form.deleted, built_forms)

    # Update or create the flat built form
    for built_form in non_deleted_built_forms:
        built_form.on_instance_modify()

    return _on_built_form_post_save(non_deleted_built_forms)


def _on_built_form_post_save(built_forms):

    logger.info("Handler: post_save_built_form for {built_forms}".format(
        built_forms=', '.join(map_property(built_forms, 'name')))
    )
    user = built_forms[0].updater
    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_built_form_initial')

    return post_save_publishing(
        starting_signal_path,
        None,
        user,
        instance=built_forms,
        signal_proportion_lookup=signal_proportion_lookup,
        dependent_signal_paths=dependent_signal_paths,
        signal_prefix='post_save_built_form')


def on_config_entity_post_save_built_form(sender, **kwargs):
    """
        Sync a ConfigEntity's BuiltFormSets
    """

    # Turn off BuiltForm instances own post-save presentation with this class scope flag
    # The ConfigEntity is managing creation and update, so we don't want to trigger publishers after every
    # BuiltForm is created/updated

    from footprint.client.configuration.fixture import ConfigEntitiesFixture
    from footprint.client.configuration.utils import resolve_fixture

    BuiltForm.no_post_save_publishing = True

    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_save_built_form. ConfigEntity: %s" % config_entity.name)

    if isinstance(config_entity, GlobalConfig) or isinstance(config_entity, Region):
        # For now only the GlobalConfig and Regions creates the sets
        config_entity.add_built_form_sets(*(set(built_form_sets(config_entity)) - set(config_entity.computed_built_form_sets())))

    BuiltForm.no_post_save_publishing = False

    reset_queries()


def built_form_sets(config_entity):
    """
    Constructs and persists buildings, buildingtypes, and placetypes and their associates and then returns them all
    as a persisted BuiltFormSet. One BuiltFormSet is returned in an array
    :param test: if test is set to true, a much more limited set of built forms is created
    """
    from footprint.client.configuration.fixture import BuiltFormFixture
    from footprint.client.configuration.utils import resolve_fixture

    json_fixture = os.path.join(settings.ROOT_PATH, 'built_form_fixture.json')
    built_form_fixture = resolve_fixture("built_form", "built_form", BuiltFormFixture, settings.CLIENT, config_entity=config_entity)

    if settings.IMPORT_BUILT_FORMS == 'CSV' or (not os.path.exists(json_fixture)):
        logger.info('Importing built forms from csv source')
        # Get the fixture scoped for the config_entity
        # Create any built_form class sets that are configured for the client at the config_entity's class scope
        built_forms_dict = built_form_fixture.built_forms()
        built_form_fixture.tag_built_forms(built_forms_dict)
        built_forms = flatten(built_forms_dict.values())

        return map(
            lambda built_form_set_config: update_or_create_built_form_set(built_form_set_config, built_forms),
            built_form_fixture.built_form_sets())

    elif settings.IMPORT_BUILT_FORMS == 'JSON' and not BuiltForm.objects.count():
        logger.info('Importing built forms from json fixture at ' + json_fixture)
        call_command('loaddata', json_fixture)
        return {}


def update_or_create_built_form_set(built_form_set_config, built_forms):
    filtered_built_form_set_dict = remove_keys(built_form_set_config, ['clazz', 'keys', 'client', 'scope', 'attribute'])
    built_form_set, created, updated = BuiltFormSet.objects.update_or_create(
        **dict(
            key=built_form_set_config['key'],
            defaults=dict(**filtered_built_form_set_dict)
        )
    )
    if not created:
        for key, value in filtered_built_form_set_dict.items():
            setattr(built_form_set, key, value)
        built_form_set.save()

    existing_built_forms = built_form_set.built_forms.all()

    # for the built_form_sets based on
    class_filter = lambda built_form: \
        built_form not in existing_built_forms and isinstance(built_form, built_form_set_config['clazz'])

    attribute_filter = lambda built_form: \
        built_form not in existing_built_forms and getattr(built_form, built_form_set_config['attribute'], None)

    importer = BuiltFormImporter()

    built_forms_for_set = built_forms

    if built_form_set_config['clazz']:
        built_forms_for_set = filter(class_filter, built_forms_for_set)

    if built_form_set_config['attribute']:
        built_forms_for_set = filter(attribute_filter, built_forms_for_set)

    if built_form_set_config['client']:
        client = built_form_set_config['client']
        client_built_form_names = [bf.name for bf in importer.load_buildings_csv(client)] + \
            [bf.name for bf in importer.load_buildingtype_csv(client)] + \
            [bf.name for bf in importer.load_placetype_csv(client)]

        client_filter = lambda built_form: \
            built_form not in existing_built_forms and \
            (not client_built_form_names or getattr(built_form, 'name', None) in client_built_form_names)
        built_forms_for_set = filter(client_filter, built_forms_for_set)

    built_form_set.built_forms.add(*built_forms_for_set)
    return built_form_set


def on_config_entity_pre_delete_built_form(sender, **kwargs):
    pass
