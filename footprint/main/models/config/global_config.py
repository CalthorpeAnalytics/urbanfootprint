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


from footprint.main.managers.geo_inheritance_manager import FootprintGeoManager
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'


class GlobalConfig(ConfigEntity):
    """
        A singleton whose adoptable attributes are adopted by other ConfigEntity instances
    """

    objects = FootprintGeoManager()

    def __init__(self, *args, **kwargs):
        super(GlobalConfig, self).__init__(*args, **kwargs)
        self.key = Keys.GLOBAL_CONFIG_KEY
        self.name = Keys.GLOBAL_CONFIG_NAME

    @property
    def full_name(self):
        """
            Overrides the default and return name
        """
        return self.name

    def db_entity_owner(self, db_entity):
        if self.schema() == db_entity.schema:
            return self
        raise Exception("Reached GlobalConfig without finding an owner for the db_entity {0}".format(db_entity))

    @classmethod
    def parent_classes(cls):
        """
            GlobalConfig can not have a parent
        """
        return []

    class Meta(object):
        permissions = (
            ('view_globalconfig', 'View GlobalConfig'),
            # merge is meaningless for a GlobalConfig, but the uniformity is useful
            ('merge_globalconfig', 'Merge GlobalConfig'),
        )
        app_label = 'main'


def global_config_singleton():
    """
        Returns the lone GlobalConfig, throwing an ObjectNotFound Exception if it hasn't yet been created
    :return:
    """
    return GlobalConfig.objects.get(key=Keys.GLOBAL_CONFIG_KEY)
