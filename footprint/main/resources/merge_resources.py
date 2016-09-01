
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
from footprint.main.models.analysis_module.merge_module.merge_updater_tool import MergeUpdaterTool
from footprint.main.resources.analysis_module_resource import AnalysisToolResource
from footprint.main.resources.config_entity_resources import ConfigEntityResource

__author__ = 'calthorpe_analytics'


class MergeUpdaterToolResource(AnalysisToolResource):

    target_config_entity = ToOneField(ConfigEntityResource, attribute='target_config_entity', full=False, null=True)

    class Meta(AnalysisToolResource.Meta):
        always_return_data = True,
        queryset = MergeUpdaterTool.objects.all()
        resource_name = 'merge_updater_tool'
