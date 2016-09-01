
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

from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'

class UserGroupKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return None

    # The are the default group names, which correspond to permission to change corresponding ConfigEntity
    # class. Guests don't currently correspond to a ConfigEntity class, they simply have view only
    # permission or less
    SUPERADMIN = 'superadmin'  # Global level
    ADMIN = 'admin'  # Region
    MANAGER = 'manager'  # Project
    USER = 'user'  # Scenario
    GUEST = 'guest'  # view
    GLOBAL = [SUPERADMIN, ADMIN, MANAGER, USER, GUEST]
