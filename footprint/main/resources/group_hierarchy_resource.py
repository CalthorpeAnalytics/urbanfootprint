# coding=utf-8

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



from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from footprint.main.models import GroupHierarchy
from footprint.main.resources.group_resource import GroupResource
from footprint.main.resources.user_authentication import UserAuthentication
from tastypie import fields

__author__ = 'calthorpe_analytics'


class GroupHierarchyResource(ModelResource):

    group = fields.ToOneField(GroupResource, 'group')
    superiors = fields.ToManyField(GroupResource, 'superiors')

    class Meta:
        always_return_data = True
        queryset = GroupHierarchy.objects.all()
        resource_name = 'group_hierarchy'
        authentication = UserAuthentication()
        authorization = DjangoAuthorization()
