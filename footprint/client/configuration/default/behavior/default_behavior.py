
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

from django.contrib.auth import get_user_model
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.client.configuration.fixture import BehaviorFixture
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.config.global_config import global_config_singleton
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.intersection import Intersection, JoinTypeKey, GeographicIntersection, \
    GeographicKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'

class DefaultBehaviorFixture(DefaultMixin, BehaviorFixture):
    def behaviors(self, **kwargs):
        key = BehaviorKey.Fab.ricate
        # This doesn't fetch from the database, since the Behavior being sought might not exist quite yet
        polygon = GeographicKey.POLYGON

        # Create a special DbEntity used only by Behavior.feature_template_behavior instances
        dummy_user = get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)

        DbEntity.objects.update_or_create(key='template_feature_behavior', defaults=dict(
            creator=dummy_user,
            updater=dummy_user))

        return FixtureList([
            Behavior(
                key=key('environmental_constraint'),
                parents=[],
                # Environmental constraints always intersect primary features polygon to polygon
                intersection=GeographicIntersection.polygon_to_polygon
            ),
            # A behavior attributed to Features representing UrbanFootprint base data
            Behavior(
                key=key('reference'),
                parents=[]
            ),
            Behavior(
                key=key('tool'),
                parents=[]
            ),
            # A behavior attributed to a Tool that produces a result from one or more inputs
            Behavior(
                key=key('analysis_tool'),
                parents=['tool']
            ),
            # A behavior attributed to a Tool that performs updates
            Behavior(
                key=key('update_tool'),
                parents=['tool']
            ),
            # A behavior attributed to a Tool that edits features or similar
            Behavior(
                key=key('editor_tool'),
                parents=['tool']
            ),
            # A behavior attributed to Features representing UrbanFootprint base data
            Behavior(
                key=key('editable_feature'),
                parents=[]
            ),
            Behavior(
                key=key('base_feature'),
                parents=[]
            ),
            # The behavior of the Agriculture Builder tool
            Behavior(
                    key=key('agriculture_editor_tool'),
                    parents=['editor_tool']
            ),
            # The behavior of the Scenario Builder tool
            Behavior(
                    key=key('scenario_editor_tool'),
                    parents=['editor_tool']
            ),
            # agriculture_editor_tool is a parent so that this DbEntity with this behavior will run the
            # agriculture module when its features are updated
            Behavior(
                key=key('base_agriculture'),
                parents=['agriculture_editor_tool']
            ),
            # agriculture_editor_tool is a parent so that this DbEntity with this behavior will run the
            # agriculture module when its features are updated
            Behavior(
                key=key('scenario_end_state'),
                parents=['scenario_editor_tool']
            ),
            Behavior(
                key=key('scenario_increment'),
                parents=[]
            ),
            # agriculture_editor_tool is a parent so that this DbEntity with this behavior will run the
            # agriculture module when its features are updated
            Behavior(
                key=key('agriculture_scenario'),
                parents=['agriculture_editor_tool']
            ),
            Behavior(
                key=key('developable'),
                parents=[]
            ),
            Behavior(
                key=key('internal_analysis'),
                parents=[]
            ),
            Behavior(
                # Background imagery
                key=key('remote_imagery'),
                parents=[]
            ),
            Behavior(
                # results
                key=key('result'),
                parents=[]
            ),
            Behavior(
                # results
                key=key('master'),
                abstract=True,
                parents=[]
            ),
            Behavior(
                # results
                key=key('draft'),
                abstract=True,
                parents=[]
            ),
            Behavior(
                # results
                key=key('default_config_entity'),
                parents=[]
            ),
            Behavior(
                # results
                key=key('base_scenario'),
                parents=['default_config_entity']
            ),
            Behavior(
                # results
                key=key('future_scenario'),
                parents=['default_config_entity']
            ),
            Behavior(
                # results
                key=key('base_master_scenario'),
                parents=['base_scenario', 'master']
            ),
            Behavior(
                # results
                key=key('base_draft_scenario'),
                parents=['base_scenario', 'draft']
            ),
            Behavior(
                # results
                key=key('future_master_scenario'),
                parents=['future_scenario', 'master']
            ),
            Behavior(
                # results
                key=key('future_draft_scenario'),
                parents=['future_scenario', 'draft']
            )
        ])
