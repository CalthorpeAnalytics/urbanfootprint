
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


from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_updater_tool import EnvironmentalConstraintUpdaterTool
from tastypie.constants import ALL
from tastypie.fields import CharField
from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_updater_tool import EnvironmentalConstraintUpdaterTool
from footprint.main.models.analysis_module.environmental_constraint_module.environmental_constraint_percent import \
    EnvironmentalConstraintPercent
from footprint.main.resources.analysis_module_resource import AnalysisToolResource
from footprint.main.resources.db_entity_resources import DbEntityResource
from footprint.main.resources.footprint_resource import FootprintResource
from tastypie import fields
from footprint.main.resources.mixins.mixins import ToManyCustomAddField

__author__ = 'calthorpe_analytics'


class EnvironmentalConstraintUpdaterToolResource(AnalysisToolResource):

    def add_environmental_constraint_percents(bundle, *environmental_constraint_percents):
        for environmental_constraint_percent in environmental_constraint_percents:
            environmental_constraint_percent.save()

    def remove_environmental_constraint_percents(bundle, *environmental_constraint_percents):
        for environmental_constraint_percent in environmental_constraint_percents:
            environmental_constraint_percent.delete()

    environmental_constraint_percent_query = lambda bundle: bundle.obj.environmentalconstraintpercent_set.all()
    environmental_constraint_percents = ToManyCustomAddField(
        'footprint.main.resources.environmental_constraint_resources.EnvironmentalConstraintPercentResource',
        attribute=environmental_constraint_percent_query,
        add=add_environmental_constraint_percents,
        remove=add_environmental_constraint_percents,
        full=True,
        null=True)

    class Meta(AnalysisToolResource.Meta):
        queryset = EnvironmentalConstraintUpdaterTool.objects.all()
        resource_name = 'environmental_constraint_updater_tool'


class EnvironmentalConstraintPercentResource(FootprintResource):

    db_entity = fields.ToOneField(DbEntityResource, 'db_entity', full=True, null=False, readonly=True)
    analysis_tool = fields.ToOneField(
        EnvironmentalConstraintUpdaterToolResource,
        'analysis_tool', full=False, null=False)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = EnvironmentalConstraintPercent.objects.all()
        resource_name = 'environmental_constraint_percent'
