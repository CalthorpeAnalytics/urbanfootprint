
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
from tastypie.fields import ToOneField, CharField, DateField, ToManyField
from footprint.main.models.analysis_module.analysis_module import AnalysisModule
from footprint.main.resources.analysis_tool_resource import AnalysisToolResource
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class AnalysisModuleResource(FootprintResource):

    config_entity = ToOneField('footprint.main.resources.config_entity_resources.ConfigEntityResource', attribute='config_entity', full=False, null=False, readonly=True)
    analysis_tools = ToManyField(AnalysisToolResource, attribute='analysis_tools')

    started = DateField(readonly=True)
    completed = DateField(readonly=True)
    failed = DateField(readonly=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True,
        excludes = ('creator', 'updater')
        filtering = {
            "config_entity": ALL_WITH_RELATIONS
        }
        queryset = AnalysisModule.objects.all()
        resource_name = 'analysis_module'

    def hydrate(self, bundle):
        if not bundle.obj.id:
            bundle.obj.creator = self.resolve_user(bundle.request.GET)
        bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return bundle
