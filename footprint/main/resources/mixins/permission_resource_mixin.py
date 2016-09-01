
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

from django.contrib.auth.models import Permission
from tastypie import fields
from tastypie.resources import ModelResource
from footprint.main.resources.caching import using_bundle_cache


__author__ = 'calthorpe_analytics'


# This is used only be PermissionResourceMixin.
# TODO Direct requests must be blocked
class PermissionResource(ModelResource):
    class Meta(object):
        abstract = False
        always_return_data = True
        # Only show the permission name
        excludes = ['name', 'content_type_id', 'id'],
        queryset = Permission.objects.filter()
        resource_name = 'permission'


class PermissionResourceMixin(ModelResource):

    def dehydrate_permissions(self, bundle):
        """
            Return the simple version of the permission (without the instance name)
        :param bundle:
        :return:
        """
        return map(lambda permission: permission.data.get('codename', '').split('_')[0], bundle.data['permissions'])

    # Returns the permissions of the bundle obj for the username.
    @using_bundle_cache
    def permission_query(bundle):
        return bundle.obj.permissions_for_user(bundle.request.GET['username'])

    permissions = fields.ToManyField(PermissionResource, attribute=permission_query, full=True, null=True, readonly=True)

    def permission_get_object_list(self, request, object_list):
        """
            Filter by our Permissions
        :param request:
        :param object_list:
        :return:
        """
        model = self._meta.queryset.model
        # Find all the groups of this user
        groups = request.user.groups.all()
        permitted_ids = model.permitted_ids(groups, object_list)

        # Filter by permitted ids
        return object_list.filter(id__in=map(lambda id: int(id), permitted_ids))
