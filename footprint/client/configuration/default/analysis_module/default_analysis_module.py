
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

from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.client.configuration.fixture import AnalysisModuleFixture
from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.analysis_module.analysis_module import AnalysisModuleConfiguration
from footprint.main.models.geospatial.behavior import BehaviorKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'

class DefaultAnalysisModule(DefaultMixin, AnalysisModuleFixture):

    def default_analysis_module_configurations(self, **kwargs):
        config_entity = self.config_entity
        uf_analysis_module = lambda module: 'footprint.main.models.analysis_module.%s' % module

        behavior_key = BehaviorKey.Fab.ricate
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return map(
            lambda configuration:
            AnalysisModuleConfiguration.analysis_module_configuration(config_entity, **configuration),
            FixtureList([]).matching_scope(class_scope=self.config_entity and self.config_entity.__class__)
        )
