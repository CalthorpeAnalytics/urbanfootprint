
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

from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.fields import ToOneField
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.resources.behavior_resources import BehaviorResource
from footprint.main.resources.config_entity_resources import ConfigEntityResource
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class AnalysisToolResource(FootprintResource):

    config_entity = ToOneField(ConfigEntityResource, attribute='config_entity', full=False, null=False)
    behavior = ToOneField(BehaviorResource, attribute='behavior', full=False, null=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True,
        filtering = {
            "config_entity": ALL_WITH_RELATIONS
        }
        queryset = AnalysisTool.objects.all()
        resource_name = 'analysis_tool'
