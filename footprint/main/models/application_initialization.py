# coding=utf-8

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

from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon, GEOSGeometry

from footprint.client.configuration.fixture import ConfigEntitiesFixture, InitFixture, region_fixtures, \
    AttributeGroupFixture, BehaviorFixture
from footprint.client.configuration.utils import resolve_fixture
from footprint.main.models.built_form.placetype_component import PlacetypeComponentCategory
from footprint.main.models.built_form.urban.building_use_definition import BuildingUseDefinition
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.interest import Interest
from footprint.main.models.config.project import Project
from footprint.main.models.database.information_schema import SouthMigrationHistory
from footprint.main.models.geospatial.attribute_group import update_or_create_attribute_group
from footprint.main.models.geospatial.behavior import update_or_create_behavior
from footprint.main.models.geospatial.intersection import JoinTypeKey, JoinType, GeographicType, GeographicKey
from footprint.main.models.keys.keys import Keys
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.models.sort_type import SortType
from footprint.main.publishing.config_entity_initialization import update_or_create_scenarios, update_of_create_regions, update_or_create_projects
from footprint.main.publishing.config_entity_publishing import post_save_config_entity_initial
from footprint.utils.utils import create_media_subdir

# TODO Move this to publishers/application_publishing.py
from footprint.main.publishing.policy_initialization import initialize_policies
from footprint.main.publishing.user_initialization import update_or_create_user, update_or_create_group

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

def update_or_create_config_entities(**kwargs):
    # Creating the precooked scenarios will cause everything else to be created.
    update_or_create_scenarios(**kwargs)
    recalculate_project_bounds()

def application_initialization(**kwargs):
    """
        Initialize or sync the application
        :param kwargs:
            'limit_to_classes' as an array of ConfigEntity classes to limit processing to those
            'no_post_save_publishing' set True to prevent the GlobalConfig save from starting publishers
    """

    # Initialize lookup table data
    if SouthMigrationHistory.objects.filter(app_name='main').exists():
        initialize_table_definitions()
        initialize_client_data()

        # Bootstrap the GlobalConfig. We'll fill it out later
        GlobalConfig._no_post_save_publishing = True
        global_config = GlobalConfig.objects.update_or_create(
            key=Keys.GLOBAL_CONFIG_KEY,
            defaults=dict(bounds=GEOSGeometry('MULTIPOLYGON EMPTY'))
        )[0]
        GlobalConfig._no_post_save_publishing = False

        # Bootstrap the admin group and user so we can use them beforehand
        update_or_create_group(name=UserGroupKey.SUPERADMIN, config_entity=global_config)
        # These users have the same name as their group
        update_or_create_user(username=UserGroupKey.SUPERADMIN, password='super_admin@uf', groups=[UserGroupKey.SUPERADMIN], is_super_user=True)

        # Bootstrap the global config Behaviors
        behavior_fixture = resolve_fixture("behavior", "behavior", BehaviorFixture, 'global', **kwargs)
        for behavior in behavior_fixture.behaviors():
            update_or_create_behavior(behavior)
        # Boot strap the global config AttributeGroups
        attribute_group_fixture = resolve_fixture("behavior", "attribute_group", AttributeGroupFixture, 'global', **kwargs)
        for attribute_group in attribute_group_fixture.attribute_groups():
            update_or_create_attribute_group(attribute_group)

        # Cartocss template storage
        create_media_subdir('styles')
        create_media_subdir('cartocss')

        # Sync the DBEntities to tables in the global schema
        global_config = initialize_global_config(**kwargs)

        for region_fixture in region_fixtures():
            # Create the Behavior instances.
            # These can be defined at the Region scope, but most
            # are simply defined at default_behavior.py
            behavior_fixture = resolve_fixture("behavior", "behavior", BehaviorFixture, region_fixture.schema, **kwargs)
            return map(
                lambda behavior: update_or_create_behavior(behavior),
                behavior_fixture.behaviors())

def minimum_initialization(**kwargs):
    """
        A minimum initialization for unit tests
        :param kwargs: 'limit_to_classes' as an array of ConfigEntity classes to limit processing to those
    :return:
    """

    from footprint.main.publishing.built_form_publishing import on_config_entity_post_save_built_form
    # Disable built_forms
    post_save_config_entity_initial.disconnect(
        on_config_entity_post_save_built_form,
        GlobalConfig,
        True,
        "built_form_publishing_on_config_entity_post_save")
    application_initialization(**kwargs)

    # Get access to the ConfigEntity fixtures for the configured client
    config_entities_fixture = resolve_fixture(
        "config_entity",
        "config_entities",
        ConfigEntitiesFixture,
        settings.CLIENT)

    key_lambda = lambda config_entity: config_entity['key']
    region_key = map(key_lambda, config_entities_fixture.regions())[0]
    update_of_create_regions(region_keys=[region_key])
    project_key = map(key_lambda, config_entities_fixture.projects())[0]
    project = update_or_create_projects(region_keys=[region_key], project_keys=[project_key])[0]
    project_fixture = resolve_fixture(
        "config_entity",
        "config_entities",
        ConfigEntitiesFixture,
        project.schema())
    scenario_key = map(key_lambda, project_fixture.scenarios(project=project))[0]
    update_or_create_scenarios(region_keys=[region_key], project_keys=[project_key], scenario_keys=[scenario_key])

def initialize_client_data():
    # Initialize client-specific models
    logger.info("importing client fixtures for {client}".format(client=settings.CLIENT))
    client_init = resolve_fixture(None, "init", InitFixture, settings.CLIENT)
    client_init.populate_models()



def recalculate_project_bounds():
    for project in Project.objects.all():
        project.recalculate_bounds()


def initialize_table_definitions():
    """
        Initialize any definition tables with constant values
    """

    # Only INTEREST_OWNER is currently used. Interests might go away some day
    Interest.objects.update_or_create(key=Keys.INTEREST_OWNER)
    Interest.objects.update_or_create(key=Keys.INTEREST_DEPENDENT)
    Interest.objects.update_or_create(key=Keys.INTEREST_FOLLOWER)

    JoinType.objects.update_or_create(key=JoinTypeKey.GEOGRAPHIC)
    JoinType.objects.update_or_create(key=JoinTypeKey.ATTRIBUTE)
    GeographicType.objects.update_or_create(key=GeographicKey.POLYGON)
    GeographicType.objects.update_or_create(key=GeographicKey.CENTROID)

    for building_use_subcategory, building_use in Keys.BUILDING_USE_DEFINITION_CATEGORIES.items():
        BuildingUseDefinition.objects.update_or_create(
            name=building_use_subcategory,
            type=building_use)

    for component in Keys.COMPONENT_CATEGORIES:
        PlacetypeComponentCategory.objects.update_or_create(
            name=component,
            contributes_to_net=True if component in Keys.NET_COMPONENTS else False
        )

    # Ways to sort PresentationMedia QuerySets
    SortType.objects.update_or_create(
        key=Keys.SORT_TYPE_PRESENTATION_MEDIA_DB_ENTITY_KEY,
        defaults={'order_by': 'db_entity_key'})
    SortType.objects.update_or_create(
        key=Keys.SORT_TYPE_PRESENTATION_MEDIA_MEDIUM_KEY,
        defaults={'order_by': 'medium__key'})
    SortType.objects.update_or_create(
        key=Keys.SORT_TYPE_PRESENTATION_MEDIA_MEDIUM_NAME,
        defaults={'order_by': 'medium__name'})
    # Ways to sort Key-ed QuerySets
    SortType.objects.update_or_create(
        key=Keys.SORT_TYPE_KEY,
        defaults={'order_by': 'key'})
    SortType.objects.update_or_create(
        key=Keys.SORT_TYPE_NAME,
        defaults={'order_by': 'name'})


def initialize_global_config(**kwargs):
    global_bounds = MultiPolygon(
        [Polygon((
            (settings.DEFAULT_SRID_BOUNDS[1], settings.DEFAULT_SRID_BOUNDS[1]),  # bottom left
            (settings.DEFAULT_SRID_BOUNDS[0], settings.DEFAULT_SRID_BOUNDS[3]),  # top left
            (settings.DEFAULT_SRID_BOUNDS[2], settings.DEFAULT_SRID_BOUNDS[3]),  # top right
            (settings.DEFAULT_SRID_BOUNDS[2], settings.DEFAULT_SRID_BOUNDS[1]),  # bottom right
            (settings.DEFAULT_SRID_BOUNDS[1], settings.DEFAULT_SRID_BOUNDS[1]),  # bottom left
        ))],
        srid=settings.DEFAULT_SRID
    )

    # Initialize global policy configuration. TODO, this needs to be more sophisticated
    initialize_policies()

    limit_to_classes = kwargs.get('limit_to_classes', [GlobalConfig]) \
        if kwargs.get('limit_to_classes', [GlobalConfig]) else [GlobalConfig]
    # Optionally disable post-save presentation
    if kwargs.get('no_post_save_publishing'):
        GlobalConfig._no_post_save_publishing = True
    # Create and persist the singleton GlobalConfig
    global_config, created, updated = GlobalConfig.objects.update_or_create(
        key=Keys.GLOBAL_CONFIG_KEY,
        defaults=dict(
            name=Keys.GLOBAL_CONFIG_NAME,
            bounds=global_bounds
        )
    ) if \
        GlobalConfig in limit_to_classes else \
        (GlobalConfig.objects.get(), False, False)
    if kwargs.get('no_post_save_publishing'):
        GlobalConfig._no_post_save_publishing = False

    return global_config
