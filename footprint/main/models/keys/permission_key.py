
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

from inflection import camelize, pluralize, dasherize, underscore
from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'

class PermissionKey(Keys):
    """
        Mirrors the built-in django permissions and adds new ones that we have defined in the models
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return None

    @classmethod
    def permission_keys(cls, key, clazz):
        """
            Get all the keys for the given key and class. This will be a single item array unless
            the key is ALL or similar
        :param key:
        :param clazz:
        :return:
        """
        return map(lambda key: '%s_%s' % (key, clazz.__name__.lower()),
                   cls._COMBOS.get(key, [key]))

    CHANGE = 'change'
    ADD = 'add'
    DELETE = 'delete'
    # Ours
    VIEW = 'view'
    # Combinations
    ALL = 'all'
    _COMBOS = {
        ALL: [CHANGE, ADD, DELETE, VIEW]
    }

class DbEntityPermissionKey(PermissionKey):
    """
        Adds the approve permission, the permission to approval feature updates
    """

    ALL = 'db_entity_all'  # The key must match the superclass, the value must differ
    APPROVE = 'approve'
    _COMBOS = {
        PermissionKey.ALL: PermissionKey._COMBOS[PermissionKey.ALL],
        ALL: PermissionKey._COMBOS[PermissionKey.ALL] + [APPROVE]
    }

class ConfigEntityPermissionKey(PermissionKey):
    """
        Adds the merge permission, the permission to merge DbEntity Features from another ConfigEntity
    """

    ALL = 'config_entity_all'  # The key must match the superclass, the value must differ
    MERGE = 'merge'
    _COMBOS = {
        PermissionKey.ALL: PermissionKey._COMBOS[PermissionKey.ALL],
        ALL: PermissionKey._COMBOS[PermissionKey.ALL] + [MERGE]
    }
