
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

from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.client.configuration.fixture import UserFixture

__author__ = 'calthorpe_analytics'

class DefaultUserFixture(DefaultMixin, UserFixture):
    def groups(self, **kargs):
        return []

    # There are no default users, but global_user.py has global-level users
    def users(self, **kargs):
        return []
