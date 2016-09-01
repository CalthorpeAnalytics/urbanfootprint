
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

from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase
from footprint.main.lib.functions import map_dict
from footprint.main.tests.test_api.patch_patch import Client2

__author__ = 'calthorpe_analytics'

class ApiTest(ResourceTestCase):
    def setUp(self):
        self.client = Client2()
        super(ApiTest, self).setUp()
        self.base_uri = '/footprint/api/v1'

    def get_credentials(self, user):
        api_key = ApiKey.objects.get(user=user).key if user else None
        return self.create_apikey(username=user.username, api_key=api_key) if api_key else {}

    def patch(self, resource_name, data, user=None):
        return self.api_client.patch(
            path='%s/%s/' % (self.base_uri, resource_name),
            data=data,
            content_type='application/json',
            authentication=self.get_credentials(user)
        )

    def get(self, resource_name, ids=None, user=None, query_params=None, **kwargs):
        """
            Get all or the instances specified by ids
        :param resource_name:
        :param ids:
        :param user:
        :return:
        """
        if query_params:
            # The test framework takes care of the username unless query_params are specified,
            # apparently
            query_params.update(username=user.username)
        return self.api_client.get(
            '%s/%s/%s%s' % (
                self.base_uri,
                resource_name,
                ('set/%s' % ';'.join(ids)) if ids else '',
                ('?%s' % '&'.join(map_dict(lambda k, v: '%s=%s' % (k,v), query_params))) if query_params else ''),
            format='json',
            authentication=self.get_credentials(user),
            **kwargs)
