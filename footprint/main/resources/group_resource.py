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


from django.contrib.auth.models import Group
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from footprint.main.resources.user_authentication import UserAuthentication
from footprint.main.resources.caching import using_bundle_cache

__author__ = 'calthorpe_analytics'


class GroupResource(ModelResource):

    # Fold the config_entity into the GroupResource from it's GroupHierarchy
    @using_bundle_cache
    def group_hierarchy_config_entity(bundle):
        bundle.obj.group_hierarchy.config_entity

    config_entity = fields.ToOneField('footprint.main.resources.config_entity_resources.ConfigEntityResource',
                                      attribute=group_hierarchy_config_entity, readonly=True, null=True)

    class Meta:
        always_return_data = True
        queryset = Group.objects.all()
        resource_name = 'group'
        authentication = UserAuthentication()
        authorization = DjangoAuthorization()
