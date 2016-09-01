
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
import pprint
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.db import models
from footprint.main.lib.functions import map_to_dict, merge, flat_map
from footprint.main.models.group_hierarchy import GroupHierarchy
from footprint.main.models.keys.permission_key import PermissionKey
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import remove_perm, assign_perm, get_groups_with_perms, get_users_with_perms
from picklefield import PickledObjectField

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


def _all_subclasses(cls):
    """Returns all known (imported) subclasses for `cls`."""
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in _all_subclasses(s)]


class Permissions(models.Model):
    class Meta(object):
        abstract = True
        app_label = 'main'

    # Dict with keys corresponding to a GroupKey string and values corresponding to a PermissionKey string.
    # When a group permission is specified, all superior groups will be assigned that permission as
    # well if they are not specifically specified here
    # Example {GroupKey.Admin:PermissionKey.ALL, GroupKey.Planner:PermissionKey.VIEW} means that all
    # groups superior to Planner, but not Admin, will get VIEW permission as well
    group_permission_configuration = PickledObjectField(null=True)

    def clear_permissions(self):
        # Remove all previously assigned permissions
        user_and_perms_sets = get_groups_with_perms(self, attach_perms=True)
        for user, perms in user_and_perms_sets.items():
            for perm in perms:
                remove_perm(perm, user, self)

    def sync_permissions(self, additional_permissions=None, permission_key_class=PermissionKey, superior_permission_lookup={}):
        """
            Syncs the instance permissions using the current values of group_permission_configuration.
            The superior groups of the object's and additional_permissions are also synced to have
            equal or higher permissions. They only get higher permissions if they match an entry
            in superior_permissions
        :param created: True if the instance was just created.
        :param additional_permissions: A dict representing permissions to use in additions
            to any stored in self.group_permission_configuration. This is used for groups that
            are dynamically created for the ConfigEntity
        :param permission_key_class: Default PermissionKey, pass a subclass to if a Permissions implementer
            implements extra permissions
        :param superior_permission_lookup: When the superior Group permissions are set, this is checked
        to see if the group should receive higher permissions than those of the subordinates. If a key match
        is found, the permission value is used. Otherwise the subordinate value is used
        :return:
        """

        # Add the permissions given in group_permissions_configuration
        configuration = merge(self.group_permission_configuration or {}, additional_permissions or {})

        if configuration:
            # Get all GroupHierarchy instances to save making extra queries
            group_hierarchy_lookup = map_to_dict(
                lambda group_hierarchy: [group_hierarchy.group.name, group_hierarchy],
                GroupHierarchy.objects.filter(group__name__in=configuration.keys()))
            for group_name, permission_key in configuration.items():
                # Assign the permission to the group to the AttributeGroupConfiguration object
                # We can have multiple permission_keys if the permission_key is PermissionKey.ALL
                try:
                    subordinate_group_hierarchy = group_hierarchy_lookup[group_name]
                except:
                    raise Exception("Couldn't find group %s among group_hierarcy_lookup, which has keys %s" %
                                    (group_name, ', '.join(group_hierarchy_lookup.keys())))
                subordinate_group = subordinate_group_hierarchy.group
                # Remove any permissions this group has on the object, in case we changed
                # the configuration
                for class_permission_key in permission_key_class.permission_keys(permission_key_class.ALL, self.__class__):
                    remove_perm(class_permission_key, subordinate_group, self)
                logger.info("Setting permissions for %s and its superiors that don't have their own configurations", subordinate_group.name)
                # Find superior groups that aren't explicitly listed in the configuration.
                # These get the same permissions as the subordinate group, unless a higher
                # permission is specified in superior_permission_lookup
                groups = set([subordinate_group]) | set(subordinate_group_hierarchy.all_superiors())
                report = {}
                for group in filter(lambda group: group == subordinate_group or group.name not in configuration.keys(), groups):
                    permission = self.best_matching_permission(group, superior_permission_lookup)
                    self.assign_permission_to_groups([group], permission, permission_key_class=permission_key_class)
                    if permission not in report:
                        report[permission] = []
                    report[permission].append(group.name)
                # Log the results
                for permission, group_names in report.iteritems():
                    logger.info("For class %s, instance %s assigned permission key %s to groups %s",
                                self.__class__.__name__, self.key, permission, ', '.join(group_names))

    def best_matching_permission(self, group, permission_lookup):
        """
            Given a group and a permission_lookup (keyed by permission name, valued by permission key)
            find the best match for the given group. Try to find a direct match for the group or it's
            global group equivalent, and then recurse on the subordinate group until a match is found
        :param group:
        :param permission_lookup:
        :return:
        """
        global_group = GroupHierarchy.objects.get(group=group).globalized_group()
        if permission_lookup.get(global_group.name):
            return permission_lookup[global_group.name]
        return self.best_matching_permission(GroupHierarchy.objects.get(group=global_group).global_subordinate, permission_lookup)

    def assign_permission_to_groups(self, groups, permission_key, permission_key_class=PermissionKey):
        """
            Assigns the given permission key to the given groups for this instance
        :param groups: UserGroup instances
        :param permission_key:
        :param permission_key_class: Default PermissionKey. The PermissionKey subclass of the mixin implementor
        :return:
        """
        for group in groups:
            for attribute_group_permission_key in permission_key_class.permission_keys(permission_key,
                                                                                       self.__class__):
                #logger.debug("For %s %s adding permission %s to group %s",
                #    self.__class__.__name__, self, attribute_group_permission_key, group.name)
                assign_perm(
                    attribute_group_permission_key,
                    group,
                    self
                )
                # ObjectPermissionChecker(group).get_perms(self)

    def validate_permission(self, user_or_group, class_permission_key):
        def name(user_or_group):

            if isinstance(user_or_group, Group):
                return "Group {group_name}".format(group_name=user_or_group.name)

            else:
                user_groups = [g.name for g in user_or_group.groups.all()]
                if user_groups:
                    user_groups_string = ', '.join()
                else:
                    user_groups_string = '(No groups)'
                return "User {username} of groups {groups}".format(username=user_or_group.username, groups=user_groups_string)

        if not user_or_group.has_perm(class_permission_key, self):
            raise Exception(
                "%s lacks expected permission key %s to instance %s.\nThe user has permission to the following \
                instances %s.\nThe user is a member of the following groups: %s.\nThe object permits the \
                following groups: %s,\nand the following users: %s" % (
                    name(user_or_group),
                    class_permission_key,
                    self.name,
                    ', '.join(ObjectPermissionChecker(user_or_group).get_perms(self)),
                    ', '.join(map(lambda group: group.name, user_or_group.groups.all() if not isinstance(user_or_group, Group) else [])),
                    ', '.join(map(lambda user_group: name(user_group),
                                  list(get_groups_with_perms(self)))),
                    ', '.join(map(lambda user_group: name(user_group),
                                  list(get_users_with_perms(self)))))
            )

    def validate_permissions(self, users_or_groups, permission_key=PermissionKey.VIEW, permission_key_class=PermissionKey):
        """
            Validate that the given users have view permission, or the given permission
            key's Permission to this instance
        :param users_or_groups: Users or groups to check
        :param permission_key: Default PermissionKey.View. Check that the user had the
        given permission_key, or all permission keys of PermissionKey.ALL or similar
        :return:
        """
        permission_keys = permission_key_class.permission_keys(permission_key, self.__class__)
        for user_or_group in users_or_groups:
            for permission_key in permission_keys:
                self.validate_permission(user_or_group, permission_key)

    def pretty_print_instance_permissions(self):
        return self.__class__.pretty_print_permissions(instance=self)

    @classmethod
    def pretty_print_permissions(cls, instance=None):
        """
            Dump and pretty print permissions for a class, and optionally limit to an instance
        :param instance:
        :return:
        """
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(cls.dump_permissions(instance=instance))

    def permissions_for_user(self, username):
        """
            Returns the permissions for the given username
            This is currently hacked to convert Scenarios to Base|Master Scenarios
            but that code can go away when we get rid of base and master Scenario subclasses
        :param username:
        :return:
        """
        return Permission.objects.filter(codename__in=ObjectPermissionChecker(
            get_user_model().objects.get(username=username)
        ).get_perms(self.subclassed if self.__class__.__name__ == 'Scenario' else self))

    def user_has_permission(self, username, permission_key):
        """
            Return true if the given user has the given permission
        :param username:
        :param permission_key:
        :return:
        """
        return permission_key in self.permissions_for_user(username)

    @classmethod
    def permitted_ids(cls, groups, objects, permission_key=PermissionKey.VIEW):
        """
            Given one or more groups and list of instances return the ids of the objects
            to which the groups have permission.
        :param groups: Typically user.groups
        :param objects: The instances of the cls to test
        :param objects: The key to check permission for, defaults to View
        :return:
        """
        # Find the content_type_ids of the resource model and subclass models
        # Then find the corresponding view ids
        # This stuff almost never changes, so cache at the model class level it for speed

        # Get all classes
        content_type_dict = ContentType.objects.get_for_models(cls, *_all_subclasses(cls))
        # split keys/values into two matching lists
        models_with_content_types, models_content_types = zip(*content_type_dict.iteritems())

        content_type_ids = [content_type.id for content_type in models_content_types]

        perm_ids = Permission.objects.filter(
            codename__in=flat_map(
                lambda model: PermissionKey.permission_keys(permission_key,
                                                            model),
                models_with_content_types
            )).values_list('id', flat=True)

        group_ids = [group.id for group in groups]
        obj_ids = [unicode(obj.id) for obj in objects]

        from guardian.models import GroupObjectPermission
        # Find all the objects of this type that this group has permission to access.
        group_objects = GroupObjectPermission.objects.filter(
            content_type_id__in=content_type_ids,
            group__in=group_ids,
            permission_id__in=perm_ids,
            object_pk__in=obj_ids)

        return group_objects.values_list('object_pk', flat=True)

    def is_permitted(self, groups, permission_key=PermissionKey.VIEW):
        """
            Returns True if the any of the given groups have the given permission to self
        :param self
        :param groups:
        :param permission_key:
        :return:
        """
        return len(self.__class__.permitted_ids(groups, [self], permission_key)) == 1

    def dump_instance_permissions(self):
        return self.__class__.dump_permissions(instance=self)

    @classmethod
    def dump_permissions(cls, instance=None):
        """
            Dump all the instance permissions for a class, or if instance is specified, just for that instance
        :param cls:
        :return:
        """

        # This import causes problems on top of the file
        from guardian.models import GroupObjectPermission
        content_type_id = ContentType.objects.get_for_model(cls)
        return map(lambda dct: merge(dct,
                                     dict(instance=cls.objects.get(id=dct['object_pk']))),
                   GroupObjectPermission.objects.filter(
                       **merge(dict(content_type_id=content_type_id),
                               dict(object_pk=instance.id) if instance else dict())
        ).values('group__name', 'permission__name', 'object_pk'))
