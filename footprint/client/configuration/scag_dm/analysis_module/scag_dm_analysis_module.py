
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

from footprint.client.configuration.fixture import AnalysisModuleFixture
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.analysis_module.analysis_module import AnalysisModuleKey, AnalysisModuleConfiguration
from footprint.main.models.analysis_module.analysis_tool import AnalysisToolKey
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'

class ScagDmAnalysisModule(AnalysisModuleFixture):

    def default_analysis_module_configurations(self, class_scope=None):

        config_entity = self.config_entity

        uf_analysis_module = lambda module: 'footprint.main.models.analysis_module.%s' % module
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return map(
            lambda configuration:
                AnalysisModuleConfiguration.analysis_module_configuration(config_entity, **configuration),FixtureList([
                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.MERGE_MODULE,
                    name='Merge Feature Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('merge_module.merge_updater_tool.MergeUpdaterTool'),
                            key=AnalysisToolKey.MERGE_UPDATER_TOOL,
                            behavior=get_behavior('update_tool')
                        )
                    ]
                )
            ]).matching_scope(class_scope=config_entity and config_entity.__class__)
        )
