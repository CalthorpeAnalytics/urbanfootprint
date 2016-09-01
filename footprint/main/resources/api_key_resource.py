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


from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.models import ApiKey
from tastypie.resources import ModelResource

__author__ = 'calthorpe_analytics'

class ApiKeyResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = ApiKey.objects.all()
        resource_name = 'api_key'
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
