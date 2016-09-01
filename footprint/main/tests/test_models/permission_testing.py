
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

from django.contrib.auth.models import Group, User
import pprint
from django.contrib.contenttypes.models import ContentType
from guardian.core import ObjectPermissionChecker
from guardian.models import GroupObjectPermission
from nose.tools import assert_equal
from footprint.main.lib.functions import get_list_or_if_empty, merge
from footprint.main.models.keys.permission_key import PermissionKey

__author__ = 'calthorpe_analytics'

class PermissionTesting(object):
    def __init__(self, test_configuration, key_class, all_groups=[], instance_key_lambda=lambda instance: instance.key):
        """
            Tests one or more instances' permsission
        :param test_configuration: a list of dicts in the following format:
            [
            dict(
                instance=instance_to_test,
                groups={
                    // format GroupKey key: PermissionKey key
                    GroupKey.ADMIN: PermissionKey.ALL
                    GroupKey.DIRECTOR: PermissionKey.View
                    ...
                    // planners have no permission
                    GroupKey.Planner: None
                }
            ),
            ...
            ]
            All permission keys should be specified as an array, since the ALL permission is an array
        :param key_class: Optional key_class used to build instance keys
        :param all_groups: Optionally pass all the groups that will be tested
        :return:
        """
        self.test_configuration = test_configuration
        self.key_class = key_class
        self.instance_key_lambda = instance_key_lambda
        self.all_groups = all_groups


    def test_permissions(self):

        for configuration in self.test_configuration:
            instance = configuration['instance']
            for group_name, permission_key in configuration['groups'].items():
                group = Group.objects.get(name=group_name)
                class_permissions_keys = PermissionKey.permission_keys(permission_key, instance.__class__) if permission_key else []
                for permission in class_permissions_keys:
                    # See if the group has all of the expected permissions to the instance
                    assert ObjectPermissionChecker(group).has_perm(permission, instance), \
                        "Group %s expected to have %s permission to instance %s with id %s and key %s but doesn't. %s" % \
                        (group.name,
                         permission,
                         instance,
                         instance.id,
                         self.key_class.Fab.remove(self.instance_key_lambda(instance)),
                         get_list_or_if_empty(
                             ObjectPermissionChecker(group).get_perms(instance),
                             lambda: 'It has no permissions',
                             lambda lisst: 'It has permissions: %s' % ', '.join(lisst)
                         ))
                for nopermission in set(PermissionKey.permission_keys(PermissionKey.ALL, instance.__class__)) - set(class_permissions_keys):
                # Make sure the other permissions are not set
                    assert not ObjectPermissionChecker(group).has_perm(nopermission, instance), \
                        "Group %s should not have %s permission to instance %s with id %s and key %s but does. %s" % \
                        (group.name,
                         nopermission,
                         instance,
                         instance.id,
                         self.key_class.Fab.remove(self.instance_key_lambda(instance)),
                         'It has permissions: %s' % ', '.join(ObjectPermissionChecker(group).get_perms(instance))
                        )

            # Test that any configured users are in the expected group
            for group_name, user_name in configuration.get('users', {}).items():
                user = User.objects.get(username=user_name)
                group = Group.objects.get(name=group_name)
                assert_equal(user.groups.filter(name=group).count(), 1,
                             "Expected user %s to be in group %s, but it wasn't. User is in the following groups %s" %
                             (user_name, group_name, ', '.join(user.groups.values_list('name', flat=True))))
