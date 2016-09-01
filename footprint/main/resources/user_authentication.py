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


from django.contrib.auth import authenticate, get_user_model, login
from tastypie.authentication import Authentication

__author__ = 'calthorpe_analytics'


class UserAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        params = request.GET
        user_model = get_user_model()

        if 'password' in params and 'email' in params:
            email = params['email']
            password = params['password']

            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:
                return False
            except user_model.MultipleObjectsReturned:
                return False

            authenticated_user = authenticate(username=user.username, password=password)

            if authenticated_user and authenticated_user.is_active:
                login(request, authenticated_user)
                return True

        elif params.get('api_key', None):
            return len(get_user_model().objects.filter(api_key__key=params['api_key'])) == 1

    # Optional but recommended
    def get_identifier(self, request):
        return request.GET.get('username', None)
