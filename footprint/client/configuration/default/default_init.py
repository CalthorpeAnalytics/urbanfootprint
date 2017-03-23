
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

from footprint.client.configuration.fixture import InitFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.models.keys.user_group_key import UserGroupKey


class DefaultInitFixture(DefaultMixin, InitFixture):
    def model_class_modules(self):
        return []
