
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

import logging
from django.db import models
from django.db.models import OneToOneField, ManyToManyField, ForeignKey
from footprint.main.lib.functions import flat_map, unique
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.keys.user_group_key import UserGroupKey

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class GroupHierarchy(models.Model):
    """
        Simple class to relate Group instances
    """
    group = OneToOneField('auth.Group', related_name='group_hierarchy')
    # The corresponding global Group of this Group (e.g. Manager for Foo_Manager) and
    # The parent ConfigEntity Groups of this Group (e.g. Foo_Manager and Foo_User for Bar_User if Bar is Foo's child
    # ConfigEntity
    superiors = ManyToManyField('auth.Group', related_name='subordinates', null=True)
    # Used for Groups scoped to ConfigEntities. Each ConfigEntity has one or more Groups
    # automatically created for it, except for GlobalConfig which uses the the global Admin Group
    config_entity = ForeignKey('main.ConfigEntity', related_name='group_hierarchies', null=True)

    def all_superiors(self):
        """
            Recursively returns all unique superiors. For a ConfigEntity Group the superiors are the corresponding
            global Group (e.g. Foo_Manager Group of Project Foo's global superior is the global Manager) as well
            as all ConfigEntity Groups of the parent ConfigEntity. For example, if Project Foo has a Foo_Manager
            and a Foo_User, and it's child Scenario Bar has a Bar_User, then Foo_Manager and Foo_User are
            the superiors of Bar_User. If a Bar_Manager existed its superiors would also be Foo_Manager and Foo_User,
            although the case of Bar_Manager having a Foo_User superior should probably be avoided (We could
            prevent this with code if such a configuration were ever desired)
        :return:
        """
        superiors = self.superiors.all()
        return unique(
            flat_map(
                lambda superior: [superior]+superior.group_hierarchy.all_superiors(), superiors),
            lambda obj: obj.id)

    def globalized_group(self):
        """
            Resolve self.group to a global group, meaning one of the groups in UserGroupKey.GLOBAL
        :return:
        """
        return self.group if self.group.name in UserGroupKey.GLOBAL else \
            self.superiors.get(name__in=UserGroupKey.GLOBAL)

    @property
    def global_subordinate(self):
        """
            Returns the subordinate of the group, or its global group equivalent that is also global
            For instance a variant of the UserGroupKey.DIRECTOR group or that exact group would return
            UserGroupKey.MANAGER. This is used to find a matching group in a group permission lookup
        :return:
        """
        global_group = self.globalized_group()
        subordinates = global_group.subordinates.all()
        for subordinate in subordinates:
            if subordinate.group.name in UserGroupKey.GLOBAL:
                return subordinate.group
        raise Exception("No global subordinate found for global group: %s" % global_group.name)

    objects = GeoInheritanceManager()

    class Meta:
        app_label = 'main'
