
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from footprint.client.configuration.fixture import ConfigEntitiesFixture
from footprint.main.models.config.scenario import BaseScenario, FutureScenario
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.utils.fixture_list import FixtureList
from django.contrib.gis.geos import MultiPolygon, Polygon
__author__ = 'calthorpe_analytics'

class SacogConfigEntitiesFixture(ConfigEntitiesFixture):
    def project_key(self):
        return None

    def region_key(self):
        return 'sac_cnty'

    def regions(self, region_keys=None, class_scope=None):
        return FixtureList([
            {
                'key': 'sac_cnty',
                'name': 'Sacramento County',
                'description': 'Sacramento County',
                'bounds': MultiPolygon([Polygon((
                    (-122.719, 37.394),  # bottom left
                    (-122.719, 38.059),  # top left
                    (-121.603, 38.059),  # top right
                    (-121.603, 37.394),  # bottom right
                    (-122.719, 37.394),  # bottom leftsample_config_entities
                ))])
            },
        ]).matching_keys(key=region_keys).matching_scope(class_scope=class_scope)


    def projects(self, region=None, region_keys=None, project_keys=None, class_scope=None):
        return FixtureList([
            {
                'key': 'elk_grv',
                'import_key': 'elk_grove',
                'name':  'City of Elk Grove',
                'description':  "City of Elk Grove",
                'base_year': 2013,
                'region_key': 'sac_cnty',
                'media': [],
            }
        ]).matching_keys(region_keys=region_keys, key=project_keys).matching_scope(class_scope=class_scope)

    def scenarios(self, project=None, region_keys=None, project_keys=None, scenario_keys=None, class_scope=None):

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return FixtureList([
            {
                'class_scope': BaseScenario,
                'key': 'base_condition',
                'scope': project.schema(),
                'name': 'Base Condition',
                'description': '{0} Base Scenario {1}'.format('2012', project.name),
                'year': 2012,
                 # Used on the front-end only.
                'behavior': get_behavior('base_scenario')
            },
            {
                'class_scope': FutureScenario,
                'key': 'scenario_a',
                'scope': project.schema(),
                'name': 'Scenario A',
                'description': 'Future Scenario for {0}'.format(project.name),
                'year': 2050,
                # Used on the front-end only
                'behavior': get_behavior('future_scenario')
            }]).matching_keys(
                    region_key=region_keys,
                    project_key=project.key if project else None,
                    key=scenario_keys).\
                matching_scope(class_scope=class_scope)
