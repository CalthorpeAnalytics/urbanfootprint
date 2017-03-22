
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
from footprint.main.models.config.project import Project
from footprint.main.models.analysis_module.analysis_module import AnalysisModuleConfiguration, AnalysisModuleKey
from footprint.main.models.analysis_module.analysis_tool import AnalysisToolKey
from footprint.main.models.config.scenario import FutureScenario, Scenario
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'

class SacogAnalysisModuleFixture(AnalysisModuleFixture):
    def default_analysis_module_configurations(self, **kwargs):
        config_entity = self.config_entity
        uf_analysis_module = lambda module: 'footprint.main.models.analysis_module.%s' % module

        behavior_key = BehaviorKey.Fab.ricate
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return map(
            lambda configuration:
            AnalysisModuleConfiguration.analysis_module_configuration(config_entity, **configuration), FixtureList([
                dict(
                    class_scope=Project,
                    key=AnalysisModuleKey.ENVIRONMENTAL_CONSTRAINT,
                    name='Environmental Constraints',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('environmental_constraint_module.environmental_constraint_union_tool.EnvironmentalConstraintUnionTool'),
                            key=AnalysisToolKey.ENVIRONMENTAL_CONSTRAINT_UNION_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                ),

                dict(
                    class_scope=FutureScenario,
                    key=AnalysisModuleKey.SCENARIO_BUILDER,
                    name='Scenario Builder',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('core_module.scenario_updater_tool.ScenarioUpdaterTool'),
                            key=AnalysisToolKey.SCENARIO_UPDATER_TOOL,
                            behavior=get_behavior('scenario_editor_tool')
                        )
                    ],
                    task_name=uf_analysis_module('core_module.core.execute_core'),
                    ),

                dict(
                    class_scope=FutureScenario,
                    key=AnalysisModuleKey.ENVIRONMENTAL_CONSTRAINT,
                    name='Environmental Constraints',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('environmental_constraint_module.environmental_constraint_updater_tool.EnvironmentalConstraintUpdaterTool'),
                            key=AnalysisToolKey.ENVIRONMENTAL_CONSTRAINT_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                            )
                    ],
                    ),
                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.ENERGY,
                    name='Energy Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('energy_module.energy_updater_tool.EnergyUpdaterTool'),
                            key=AnalysisToolKey.ENERGY_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ],
                    ),
                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.WATER,
                    name='Water Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('water_module.water_updater_tool.WaterUpdaterTool'),
                            key=AnalysisToolKey.WATER_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                ),
                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.VMT,
                    name='Vehicle Miles Traveled',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('vmt_module.vmt_updater_tool.VmtUpdaterTool'),
                            key=AnalysisToolKey.VMT_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                ),
                dict(
                    class_scope=FutureScenario,
                    key=AnalysisModuleKey.FISCAL,
                    name='Fiscal Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('fiscal_module.fiscal_updater_tool.FiscalUpdaterTool'),
                            key=AnalysisToolKey.FISCAL_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                ),

                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.PUBLIC_HEALTH,
                    name='Public Health Analysis Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('public_health_module.public_health_updater_tool.PublicHealthUpdaterTool'),
                            key=AnalysisToolKey.PUBLIC_HEALTH_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                ),

                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.AGRICULTURE,
                    name='Agriculture',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('agriculture_module.agriculture_updater_tool.AgricultureUpdaterTool'),
                            key=AnalysisToolKey.AGRICULTURE_UPDATER_TOOL,
                            behavior=get_behavior('update_tool')
                        )
                    ]
                ),
                dict(
                    class_scope=Scenario,
                    key=AnalysisModuleKey.AGRICULTURE_ANALYSIS,
                    name='RUCS Analysis Module',
                    analysis_tools=[
                        dict(
                            class_name=uf_analysis_module('agriculture_module.agriculture_updater_tool.AgricultureUpdaterTool'),
                            key=AnalysisToolKey.AGRICULTURE_UPDATER_TOOL,
                            behavior=get_behavior('analysis_tool')
                        )
                    ]
                )
            ]).matching_scope(class_scope=config_entity and config_entity.__class__)
        )
