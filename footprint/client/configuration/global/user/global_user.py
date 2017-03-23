
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from django.conf import settings
from footprint.client.configuration.fixture import UserFixture
from footprint.main.models.keys.user_group_key import UserGroupKey

__author__ = 'calthorpe_analytics'

class GlobalUserFixture(UserFixture):
    def groups(self, **kargs):
        """
        :param kargs:
        :return:
        """
        return [
            dict(name=UserGroupKey.SUPERADMIN),
            dict(name=UserGroupKey.ADMIN, superiors=[UserGroupKey.SUPERADMIN]),
            dict(name=UserGroupKey.MANAGER, superiors=[UserGroupKey.ADMIN]),
            dict(name=UserGroupKey.USER, superiors=[UserGroupKey.MANAGER]),
            dict(name=UserGroupKey.GUEST, superiors=[UserGroupKey.USER]),
        ]

    def users(self, **kargs):
        """
        Here we define admin-level users based on settings.ADMINS.
        Custom users at other permission levels should be
        declared in the UserFixture of the appropriate ConfigEntity. For example,
        users with Region permission should be declared in that region's UserFixture, unless
        the user needs permission to multiple regions, in which case it should probably go here

        :param kwargs:
        :return: A list of dicts representing Users
        """
        def create_admin_dict(admin_tuple):
            first_name, last_name = admin_tuple[0].rsplit(' ', 1)
            username = first_name.lower()
            return dict(groups=[UserGroupKey.SUPERADMIN],
                        username=username,
                        # Default pw is name@uf
                        # The software should force this to be changed immediately
                        password='%s@uf' % username,
                        email=admin_tuple[1])

        return map(lambda admin_tuple: create_admin_dict(admin_tuple),
                   settings.ADMINS)
