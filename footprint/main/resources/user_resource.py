
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


__author__ = 'calthorpe_analytics'

from tastypie import fields
from tastypie.exceptions import NotFound
from footprint.main.resources.api_key_resource import ApiKeyResource
from footprint.main.resources.group_resource import GroupResource
from footprint.main.resources.user_authentication import UserAuthentication
from tastypie.models import create_api_key, ApiKey
from django.db import models
from django.contrib.auth import get_user_model
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource


class UserResource(ModelResource):

    # Include the ApiKey so that the user can make authenticated calls
    api_key = fields.ToOneField(ApiKeyResource, 'api_key', full=True)
    # Just for debugging for now
    groups = fields.ToManyField(GroupResource, 'groups')

    def dehydrate_api_key(self, bundle):
        """
            Expose only the ApiKey.key via the API.
        :param bundle:
        :return:
        """
        return bundle.data['api_key'].data['key']

    def hydrate_api_key(self, bundle):
        """
            Convert the api key into a full instance if it matches
        :param bundle:
        :return:
        """
        try:
            bundle.obj.api_key = ApiKey.objects.filter(key=bundle.data['api_key'])
        except NotFound:
            bundle.obj.api_key = None
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(UserResource, self).build_filters(filters)

        if orm_filters.get('password__exact', None):
            orm_filters.pop('password__exact')
        if "api_key__exact" in orm_filters:
            if orm_filters['api_key__exact']:
                orm_filters['api_key__key__exact'] = orm_filters['api_key__exact']
            orm_filters.pop('api_key__exact')

        return orm_filters

    class Meta:
        filtering = {
            "id": ('exact',),
            "username": ('exact',),
            "password": ('exact',),
            "api_key": ('exact',),
            "email": ('exact',),
        }
        always_return_data = True
        queryset = get_user_model().objects.all()
        resource_name = 'user'
        excludes = ['is_superuser', 'is_staff', 'last_login', 'date_joined', 'password']
        authentication = UserAuthentication()
        authorization = DjangoAuthorization()

models.signals.post_save.connect(create_api_key, sender=get_user_model())
class ApiTokenResource(ModelResource):
    class Meta(object):
        queryset = ApiKey.objects.all()
        resource_name = "token"
        include_resource_uri = False
        fields = ["key"]
        list_allowed_methods = []
        detail_allowed_methods = ["get"]
        authentication = BasicAuthentication()

    def obj_get(self, request=None, **kwargs):
        if kwargs["pk"] != "auth":
            raise NotImplementedError("Resource not found")

        user = request.user
        if not user.is_active:
            raise NotFound("User not active")

        api_key = ApiKey.objects.get(user=request.user)
        return api_key
