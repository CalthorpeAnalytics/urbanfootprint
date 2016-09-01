
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


from django.contrib.auth.models import User
from footprint.client.configuration.fixture import ConfigEntitiesFixture, PolicyConfigurationFixture, InitFixture
from footprint.client.configuration.utils import resolve_fixture
from footprint.main.lib.functions import remove_keys, merge, flat_map, map_to_dict
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.category import Category
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.config.global_config import global_config_singleton
from django.conf import settings

__author__ = 'calthorpe_analytics'

client_name = settings.CLIENT
config_entities_fixture = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, client_name)
policy_fixture = resolve_fixture("policy", "policy", PolicyConfigurationFixture, settings.CLIENT)
init_fixture = resolve_fixture(None, "init", InitFixture, settings.CLIENT)

import logging
logger = logging.getLogger(__name__)


class SQLImportError(Exception):
    def __init__(self, value):
        super(SQLImportError, self).__init__(value)


def update_of_create_regions(region_fixtures=config_entities_fixture.regions(), **kwargs):
    """
    Create test regions according to the sample
    :return:
    """

    def update_or_create_region(region_dict):
        if kwargs.get('limit_to_classes') and Region not in kwargs['limit_to_classes']:
            if Region.objects.filter(key=region_dict['key']).count() != 1:
                raise Exception("Trying to get Region %s, which hasn't been created" % region_dict['key'])
            region_tuple = Region.objects.get(key=region_dict['key']), False, False
        else:
            region_tuple = Region.objects.update_or_create(
                key=region_dict['key'],
                defaults=merge(
                    dict(
                        behavior=get_behavior('default_config_entity'),
                    ),
                    remove_keys(region_dict, ['key', 'media']),
                    dict(
                        creator=User.objects.get(username=UserGroupKey.SUPERADMIN),
                        parent_config_entity=global_config_singleton() if \
                            region_dict['key'] == settings.CLIENT else \
                            update_or_create_region(dict(key=settings.CLIENT, name=settings.CLIENT_NAME))[0]
            )))

        logger.info("{update_or_create} Region {config_entity}".format(update_or_create='Created' if region_tuple[1] else 'Updated', config_entity=region_tuple[0]))


        media = map(lambda medium_config:
                    Medium.objects.update_or_create(
                        key=medium_config.key,
                        defaults=remove_keys(medium_config.__dict__['kwargs'], 'key'))[0],
                    region_dict.get('media', []))

        existing_media = region_tuple[0].media.filter(id__in=map(lambda medium: medium.id, media))
        media_to_add = set(media) - set(existing_media)
        if len(media_to_add) > 0:
            region_tuple[0].media.add(*media_to_add)
        return region_tuple

    regions_tuple = map(
        lambda region_dict: update_or_create_region(region_dict),
        region_fixtures)

    return map(lambda region_tuple: region_tuple[0], regions_tuple)


def update_or_create_scenarios(projects=[], **kwargs):
    """
        Initializes scenarios using fixture data. The fixture data is expected in the form
        dict(BaseScenario=[dict(),...], FutureScenario=[dict()....]) where the dicts in the former are used
        to create BaseScenario instances and those in the latter to create FutureScenario instances.
        Use kwargs to limit class processing to one model class with e.g. class=FutureScenario
    :param scenario_fixtures:
    :return:
    """
    projects = projects or update_or_create_projects(**kwargs)

    # Get the scenario fixtures for each Project instance and build the Scenario instances.
    # Flatten the results and return them
    # scenario_fixtures may be a function that accepts the current project in order to filter the fixtures
    return flat_map(
        lambda project: scenarios_per_project(
            project,
            # Resolve as the scenarios as specific to the project scope as available
            resolve_fixture("config_entity",
                            "config_entities",
                            ConfigEntitiesFixture,
                            project.schema()).scenarios(project), **kwargs),
        projects
    )

def get_behavior(key):
    # The Behavior keyspace
    behavior_key = BehaviorKey.Fab.ricate
    # Used to load Behaviors defined elsewhere
    return Behavior.objects.get(key=behavior_key(key))

def scenarios_per_project(project, scenario_fixtures, **kwargs):

    # Create the Scenarios from the fixtures
    # The fixtures are dict keyed by the Scenario subclass (BaseScenario and FutureScenario) with a list of
    # Scenario fixtures for each
    scenarios_created_updated = map(
        lambda scenario_fixture:
        scenario_fixture['class_scope'].objects.update_or_create(
            key=scenario_fixture['key'],
            defaults=merge(
                dict(behavior=get_behavior('default_config_entity')),
                remove_keys(scenario_fixture,
                            ['class_scope', 'key', 'project_key', 'categories', 'year']),
                dict(
                    parent_config_entity=project,
                    year=scenario_fixture.get('year', project.base_year),
                    creator=User.objects.get(username=UserGroupKey.SUPERADMIN))
           )),
        # If kwargs['limit_to_classes'] is specified, only do Scenario subclasses that match it, if any
        filter(lambda scenario_fixture:
               scenario_fixture['class_scope'] in kwargs.get('limit_to_classes', [scenario_fixture['class_scope']])
               or [scenario_fixture['class_scope']],
               scenario_fixtures))


    for scenario_tuple in scenarios_created_updated:
        logger.info("{update_or_create} Scenario {config_entity}".format(update_or_create='Created' if scenario_tuple[1] else 'Updated', config_entity=scenario_tuple[0]))

    # Apply the categories, and other simple many-to-many attributes as needed
    for i, scenario_dict in enumerate(scenario_fixtures):
        for category in scenario_dict.get('categories', []):
            category, created, updated = Category.objects.update_or_create(key=category.key, value=category.value)
            scenario = scenarios_created_updated[i][0]
            scenario.add_categories(category)
            scenario._no_post_save_publishing=True
            scenario.save()
            scenario._no_post_save_publishing=False

    return map(lambda scenario_created_updated: scenario_created_updated[0], scenarios_created_updated)

def update_or_create_projects(region_fixtures=config_entities_fixture.regions(), **kwargs):
    """
    Create test projects according to the samples
    :param project_fixtures:
    :return:
    """

    regions = update_of_create_regions(region_fixtures, **kwargs)
    regions_by_key = map_to_dict(lambda region: [region.key, region], regions)
    project_fixtures = config_entities_fixture.projects()

    def update_or_create_project(project_dict):
        if kwargs.get('limit_to_classes') and Project not in kwargs['limit_to_classes']:
            if Project.objects.filter(key=project_dict['key']).count() != 1:
                raise Exception("Trying to get Project %s, which hasn't been created" % project_dict['key'])
            project_tuple = Project.objects.get(key=project_dict['key']), False, False
        else:
            project_tuple = Project.objects.update_or_create(
                key=project_dict['key'],
                defaults=merge(
                    dict(
                        behavior=get_behavior('default_config_entity'),
                    ),
                    remove_keys(project_dict, ['key', 'base_table', 'region_key', 'media']),
                    dict(
                        parent_config_entity=regions_by_key[project_dict['region_key']],
                        creator=User.objects.get(username=UserGroupKey.SUPERADMIN)
                    )
            ))

        logger.info("{update_or_create} Project {config_entity}".format(update_or_create='Created' if project_tuple[1] else 'Updated', config_entity=project_tuple[0]))

        media = map(lambda medium_config:
                    Medium.objects.update_or_create(
                        key=medium_config.key,
                        defaults=remove_keys(medium_config.__dict__['kwargs'], 'key'))[0],
                    project_dict.get('media', []))

        existing_media = project_tuple[0].media.filter(id__in=map(lambda medium: medium.id, media))
        media_to_add = set(media) - set(existing_media)
        if len(media_to_add) > 0:
            project_tuple[0].media.add(*media_to_add)
        return project_tuple

    projects_created_updated = map(
        lambda project_fixture: update_or_create_project(project_fixture),
        project_fixtures)

    return map(lambda project_created_updated: project_created_updated[0], projects_created_updated)
