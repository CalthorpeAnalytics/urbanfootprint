
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

from tastypie.fields import ToManyField
from tastypie.resources import ModelResource
from footprint.main.models.config.policy_set import PolicySet
from footprint.main.models.config.policy import Policy
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.tag_resource import TagResource

__author__ = 'calthorpe_analytics'

class PolicyResource(FootprintResource):
    policies = ToManyField('self', 'policies')
    tags = ToManyField(TagResource, 'tags')
    class Meta:
        always_return_data = True
        queryset = Policy.objects.all()

class PolicySetResource(ModelResource):
    policies = ToManyField(PolicyResource, 'policies')

    class Meta:
        always_return_data = True
        queryset = PolicySet.objects.all()
        resource_name = 'policy_set'
