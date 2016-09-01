
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
import random

from django.contrib.auth.models import User, Group
from django.db import reset_queries
from guardian.core import ObjectPermissionChecker
from django.dispatch import Signal

from footprint.main.lib.functions import compact, map_to_dict, unique, flat_map
from footprint.main.models.config.global_config import global_config_singleton, GlobalConfig
from footprint.main.models.keys.permission_key import PermissionKey, ConfigEntityPermissionKey, DbEntityPermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.user_initialization import update_or_create_group, update_or_create_user
from footprint.main.models.group_hierarchy import GroupHierarchy
from footprint.main.utils.utils import resolvable_module_attr_path
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.models.config.scenario import Scenario
from footprint.client.configuration.fixture import UserFixture
from footprint.client.configuration.utils import resolve_fixture


__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


def dependent_signal_paths(signal_path):
    """
        Gives the hierarchy of publisher signal calling order based on the given signal
        Signals are given as strings instead of paths for serialization ease
        param: signal_path. The signal path for which the dependent signals are returned
        return: An array of signal_paths or an empty array
    """
    return []

# Very wild guess about layer saving proportional times to send to the client
# These represent the parsed signal names sent to the client after the dependencies of
# the signal finish running
signal_proportion_lookup = dict(
    # initial signal after save
    post_save_user_initial=1
)


def on_user_post_save_process_user(sender, **kwargs):
    from footprint.main.publishing import tilestache_publishing

    scenario = kwargs['scenario']
    tilestache_publishing.on_config_entity_post_save_tilestache(None, instance=scenario, ignore_raster_layer=True)


post_save_user_initial = Signal(providing_args=[])
post_save_user_initial.connect(on_user_post_save_process_user)


def on_user_post_save(sender, **kwargs):
    user = kwargs['instance']
    groups = user.groups.all()
    if not groups:
        raise Exception('User %s is not in any groups', user)

    config_entities = set()
    for group in groups:
        config_entity = group.group_hierarchy.config_entity
        if not config_entity and group.name in UserGroupKey.GLOBAL:
            # Each of the GLOBAL groups are a special case--both a global Group and a ConfigEntity Group
            # It purposely doesn't resolve its config_entity but we need it here
            config_entity = global_config_singleton()

        if config_entity:
            config_entities.add(config_entity)

    # We should always have at least one ConfigEntity
    if not config_entities:
        raise Exception('No config entity for user {user}'.format(user=user))

    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_user_initial')

    scenarios = set()
    for config_entity in config_entities:
        scenarios |= set(config_entity.descendants_by_type(Scenario))

    # randoming order b/c we've had problems with
    # post-save processing of admin-level users causing
    # the machine to run out of available memory, which
    # prevented scenarios later in the list from being processed.
    scenarios = list(scenarios)
    random.shuffle(scenarios)

    for scenario in scenarios:
        post_save_publishing(
            starting_signal_path,
            scenario,
            user,
            instance=user,
            instance_class=User,
            instance_key=user.username,
            signal_proportion_lookup=signal_proportion_lookup,
            dependent_signal_paths=dependent_signal_paths,
            signal_prefix='post_save_user',
            scenario=scenario
        )


def _update_or_create_config_entity_groups(config_entity):
    """
        Updates/Creates all the ConfigEntity-specific groups of the given ConfigEntity.
    :param config_entity:
    :return:
    """
    from footprint.client.configuration.fixture import ConfigEntityFixture

    # Each ConfigEntity class has its own groups according to the configuration
    # global groups listed in its configuration
    # Iterate through the configured global groups and create ConfigEntity-specific versions
    # The exception is GlobalConfig, whose ConfigEntity Group is the SuperAdmin Group
    # It returns nothing here since SuperAdmin is a global Group as well, it doesn't need to be
    # treated as a ConfigEntity Group
    client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(config_entity)
    return map(
        lambda global_group_name: _update_or_create_config_entity_group(config_entity, global_group_name),
        client_fixture.default_config_entity_groups())


def _update_or_create_config_entity_group(config_entity, global_group_name):
    # ConfigEntity group name is created by combining it's schema with the global
    # group's name. The exception is GlobalConfig, whose ConfigEntity Group is simply the global admin group
    if not config_entity.schema_prefix:
        # GlobalConfig case, nothing to do here
        return Group.objects.get(name=global_group_name)

    config_entity_group_name = '__'.join(compact([config_entity.schema_prefix, global_group_name]))

    # The superiors of this group are our global Group and
    # the parent ConfigEntity's groups whose global Group is equal or greater than ours
    # (e.g. foo__user's superior is user and and bar_user and bar_manager if bar is the parent ConfigEntity of foo)

    # Get the name of all groups of the parent ConfigEntity
    all_parent_config_entity_group_hierarchies = config_entity.parent_config_entity.group_hierarchies.all()

    # Only accept Groups that are at least at our global Group level
    eligible_global_groups_names = UserGroupKey.GLOBAL[0:UserGroupKey.GLOBAL.index(global_group_name)+1]

    # Given a minimum eligible permission level (e.g. above Manager),
    # find all of the parent ConfigEntity's Groups that have at least that permission level (e.g. Manager and Admin).
    # These logically deserve all the permissions of the child ConfigEntity Group.
    # It's unlikely that a parent ConfigEntity Group would be a lower permission level (e.g. User), so this will normally accept all parent ConfigEntity Groups
    config_entity_groups_matching_eligible_global_groups = []
    for group_hierarchy in all_parent_config_entity_group_hierarchies:
        if group_hierarchy.globalized_group().name in eligible_global_groups_names:
            config_entity_groups_matching_eligible_global_groups.append(group_hierarchy)

    # Sort by ascending permission. This probably doesn't matter--
    # it just means we process the lower permission first for consistent logging. (There is typically only one Group anyway)
    group_hierarchies = sorted(
        config_entity_groups_matching_eligible_global_groups,
        key=lambda group_hierarchy: eligible_global_groups_names.index(group_hierarchy.globalized_group().name))

    # Combine our global Group name with the parent ConfigEntity Groups
    superior_group_names = unique(
        [global_group_name] +
        map(lambda group_hierarchy: group_hierarchy.group.name, group_hierarchies)
    )

    # Update or create the Group
    return update_or_create_group(
        name=config_entity_group_name,
        config_entity=config_entity,
        superiors=superior_group_names)


def sync_config_entity_group_permissions(obj, config_entity_groups, permission_lookup, permission_key_class=PermissionKey, **kwargs):
    """
        Syncs ConfigEntity Group permissions for a ConfigEntity or DbEntity
        All superior Groups will also receive permissions. Superior groups to a ConfigEntity Group
        are the ConfigEntity Group of the parent ConfigEntity (if one exists) and the global Group
        to which the ConfigEntity Group corresponds. For instance, for a Project ConfigEntity Group,
        the superiors are the parent Region ConfigEntity Group and the UserGroupKey.MANAGER group (the
        global Group used for Projects)
    :param obj: A ConfigEntity or DbEntity
    :param config_entity_groups: ConfigEntity Groups
    :param permission_lookup, a mapping of user groups to PermissionKeys. When giving permission to
    a ConfigEntity group, this lookup will be consulted. The user group that closest matches the
    ConfigEntity group will be used. Only a direct match or global version will be accepted. For instance
    if the ConfigEntity group is a User ConfigEntity group, then group in the permission_lookup must
    be the same group or the global UserGroupKey.USER group
    :param permission_key_class: Default PermissionKey. Specify a PermissionKey subclass when the obj class
    defines extra permissions. (This is only needed to resolve keys that map to multiple permissions)
    :param kwargs:
    :return:
    """

    def _resolve_permission(group, permission_lookup):
        """
            Matches the group to a key in the permission_lookup.
            The group name and it's immediate superiors will be checked for a match,
            but only superiors that are global Groups. It's unlikely that we'd
            have a permission_lookup specific to a ConfigEntity Group. They will normally
            contain only global groups (UserGroupKey.SUPERADMIN, UserGroupKey.USER, etc)
        :param group: The group to test
        :param permission_lookup: keyed by group names, valued by a PermissionKey strings
        :return:
        """

        # Get the global superior, which exists except for ADMIN
        global_superior = GroupHierarchy.objects.get(group=group).superiors.get(
            name__in=UserGroupKey.GLOBAL
        ) if group.name != UserGroupKey.SUPERADMIN else None
        # See if we have a permission matching the group or global superior
        for check_group in [group] + ([global_superior] if global_superior else []):
            if permission_lookup.get(check_group.name):
                return permission_lookup[check_group.name]
        # No match, no problem. Recurse on the next Global group or its subordinate
        subordinates = filter(
            lambda subordinate: subordinate.group.name in UserGroupKey.GLOBAL,
            (group if group.name in UserGroupKey.GLOBAL else global_superior).subordinates.all())
        if len(subordinates) == 1:
            return _resolve_permission(subordinates[0].group, permission_lookup)
        else:
            raise Exception(
                "For group {group_name} no permission in permission_lookup matches: {permission_lookup} \
                and not exactly one global subordinate exists: {subordinates}".format(
                    group_name=group.name,
                    permission_lookup=permission_lookup,
                    subordinates=subordinates
                )
            )

    # Sync ConfigEntity groups permissions
    # Give full permission to the ConfigEntity Group(s) to access this object
    # TODO this might change in the future if we define subordinate ConfigEntity Groups on the object
    config_entity_group_permissions = map_to_dict(
        lambda group: [group.name, _resolve_permission(group, permission_lookup)],
        config_entity_groups)
    obj.sync_permissions(
        additional_permissions=config_entity_group_permissions,
        permission_key_class=permission_key_class,
        superior_permission_lookup=permission_lookup
    )

    # TODO this is for debugging/logging. It can be commented out
    for group_name, permission_key in config_entity_group_permissions.items():
        logger.info("User Publishing. For %s %s gave %s permission(s) to ConfigEntity UserGroup: %s" %
                    (obj.__class__.__name__, obj.name, permission_key, group_name))
        for class_permission_key in permission_key_class.permission_keys(permission_key, obj.__class__):
            perm_checker = ObjectPermissionChecker(Group.objects.get(name=group_name))
            assert perm_checker.has_perm(class_permission_key, obj), \
                "No permission for Group %s, Permission %s, ConfigEntity %s. It has permissions %s" % \
                (group_name, class_permission_key, obj.name, perm_checker.get_perms(obj))

    return config_entity_group_permissions


def on_config_entity_post_save_group(sender, **kwargs):
    """
        Syncs the user, groups, and permissions for the ConfigEntity
        Some ConfigEntity classes create their own Groups and default
        Users. This makes it easy to give a client-specific user permission
        to certain ConfigEntity by joining the latter's group
    :param sender:
    :param kwargs:
    :return:
    """

    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    if config_entity._no_post_save_publishing:
        return
    user = kwargs.get('user')
    logger.info("Handler: post_save_user for config_entity {config_entity} and user {username}".format(
        config_entity=config_entity.name,
        username=user.username if user else 'undefined'))

    if kwargs.get('created') and not config_entity.creator:
        # Set the ConfigEntity.creator to the default admin group user if it wasn't set by the API
        config_entity.creator = User.objects.get(username=UserGroupKey.SUPERADMIN)
        config_entity._no_post_save_publishing = True
        config_entity.save()
        config_entity._no_post_save_publishing = False

    # First update_or_create any default groups. This usually just applies to global_config
    from footprint.client.configuration.fixture import UserFixture
    from footprint.client.configuration.utils import resolve_fixture
    user_fixture = resolve_fixture("user", "user", UserFixture, config_entity.schema(),
                                   config_entity=config_entity)
    for group_fixture in user_fixture.groups():
        group = update_or_create_group(**group_fixture)
        logger.info("User Publishing. For ConfigEntity %s synced global UserGroup: %s" %
                    (config_entity.name, group.name))

    # Sync permissions for the ConfigEntity
    # Resolve the default ConfigEntity permissions for this config_entity
    # Update or Create the ConfigEntity Group(s) for this ConfigEntity
    config_entity_groups = _update_or_create_config_entity_groups(config_entity)
    # Get the mapping of groups to permission types for the config_entity's most relevant fixture
    # These group keys are generally all global groups.
    from footprint.client.configuration.fixture import ConfigEntitiesFixture
    config_entities_fixture = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture, config_entity.schema())
    permission_lookup = config_entities_fixture.default_config_entity_permissions()
    # Set the permissions for the config_entity groups. This will also set all superior group permissions
    # to the same permissions or greater is they match something in the permission_lookup
    config_entity_group_permissions = sync_config_entity_group_permissions(
        config_entity, config_entity_groups, permission_lookup, permission_key_class=ConfigEntityPermissionKey, **kwargs)

    # Give the groups read permissions on the ancestor config_entities
    # TODO restrict this access further for the UserGroupKey.DEMO group
    groups = Group.objects.filter(name__in=config_entity_group_permissions.keys())
    for config_entity in config_entity.ancestors:
        config_entity.assign_permission_to_groups(groups, PermissionKey.VIEW)

    # TODO tell children to add themselves to all ancestors (resync)
    # This will only be needed if the parent ConfigEntity group permission configuration changes

    reset_queries()


def on_config_entity_post_save_user(sender, **kwargs):
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    if config_entity._no_post_save_publishing:
        return
    if kwargs.get('created') and not config_entity.creator:
        # Set the ConfigEntity.creator to the default admin group user if it wasn't set by the API
        config_entity.creator = User.objects.get(username=UserGroupKey.SUPERADMIN)
        config_entity._no_post_save_publishing = True
        config_entity.save()
        config_entity._no_post_save_publishing = False

    # TODO these should be importable on top. Something is messed up
    user_fixture = resolve_fixture("user", "user", UserFixture, config_entity.schema(),
                                   config_entity=config_entity)

    # Get the ConfigEntityGroups of the ConfigEntity. GlobalConfig uses SuperAdmin as its Group
    config_entity_groups = config_entity.config_entity_groups() if \
        not isinstance(config_entity, GlobalConfig) else \
        [Group.objects.get(name=UserGroupKey.SUPERADMIN)]

    # Find all existing users of all ConfigEntity Groups of the ConfigEntity
    # Note that we use values() instead of all() to get dicts with just needed fields instead of model instances
    # TODO remove username from here once all users have emails. update_or_create_user() checks username for uniquess presently
    existing_user_dicts = flat_map(
        lambda group: group.user_set.all().values('email', 'username'),
        config_entity_groups
    )

    # Combine the existing users with the fixtures, giving the former preference. We favor
    # what's in the database because the user might have updated their profile
    # Only accept fixture users not matching users in the db (by email)
    existing_emails = map(lambda existing_user_dict: existing_user_dict['email'], existing_user_dicts)
    logger.debug("Found existing users %s" % ', '.join(existing_emails))
    new_fixture_users = filter(lambda fixture_user: fixture_user['email'] not in existing_emails, user_fixture.users())
    if len(new_fixture_users) > 0:
        logger.debug("Found new fixture users %s" % ', '.join(map(lambda fixture_user: fixture_user['email'], new_fixture_users)))
    user_dicts = existing_user_dicts + new_fixture_users

    # Update or create each user. This will create users of new fixtures and run post-save processing
    # on both existing and new.
    for user_dict in user_dicts:
        update_or_create_user(**user_dict)

    reset_queries()


def on_config_entity_db_entities_post_save_user(sender, **kwargs):
    """
        Sync all ConfigEntity DbEntities permissions
    :param sender:
    :param kwargs:
    :return:
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    if config_entity._no_post_save_publishing:
        return
    for db_entity_interest in config_entity.computed_db_entity_interests():
        on_db_entity_post_save_user(sender, instance=db_entity_interest)

    reset_queries()


def on_db_entity_post_save_user(sender, **kwargs):
    """
        Give all ConfigEntities Groups in the hierarchy appropriate permissions
    :param sender:
    :param kwargs:
    :return:
    """
    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    if db_entity_interest.deleted:
        # Nothing to do for deleted instances
        return

    config_entity = db_entity_interest.config_entity.subclassed
    db_entity = db_entity_interest.db_entity
    logger.info("Handler: on_db_entity_post_save_user. DbEntity: %s" % db_entity.full_name)

    # Get the ConfigEntity Group(s) for the DbEntity's ConfigEntity
    # The groups are configured based on the subclass of ConfigEntity
    config_entity_groups = config_entity.config_entity_groups()

    # Sync permissions for the DbEntity

    # Resolve the default DbEntity permissions for the DbEntity's ConfigEntity
    from footprint.client.configuration.fixture import ConfigEntityFixture
    config_entity = db_entity_interest.config_entity.subclassed
    config_entity_fixture = ConfigEntityFixture.resolve_config_entity_fixture(config_entity)
    permission_lookup = config_entity_fixture.default_db_entity_permissions()
    logger.info("For ConfigEntity {config_entity} will apply DbEntity permission to groups {groups} based on permission_lookup {permission_lookup}".format(
        groups=', '.join(map(lambda group: group.name, config_entity_groups)),
        config_entity=config_entity.name,
        permission_lookup=permission_lookup
    ))
    sync_config_entity_group_permissions(
            db_entity,
            config_entity_groups,
            permission_lookup,
            permission_key_class=DbEntityPermissionKey,
            **kwargs)

    # Repeat the process for all descendant ConfigEntities, just giving their Groups view permission.
    # There's no obvious use case for a ConfigEntity Group of a child ConfigEntity having edit permission
    # to the DbEntity of a parent ConfigEntity.
    for descendant in config_entity.descendants():
        descendant_config_entity_groups = descendant.config_entity_groups()
        # The permission lookup maps the global version of each group to VIEW permission
        # Example: The Manager Group of Project Foo would just map to UserGroupKey.MANAGER
        descendant_permission_lookup = map_to_dict(
            lambda config_entity_group: [config_entity_group.group_hierarchy.globalized_group().name, PermissionKey.VIEW],
            descendant_config_entity_groups
        )

        logger.info(
            "For descendant ConfigEntity {config_entity} will apply DbEntity permission \
            to groups {groups} based on permission_lookup {permission_lookup}".format(
                groups=', '.join(map(lambda group: group.name, descendant_config_entity_groups)),
                config_entity=descendant.name,
                permission_lookup=descendant_permission_lookup
            )
        )

        # Apply view permissions to the ConfigEntity groups of each descendant ConfigEntity
        sync_config_entity_group_permissions(
            db_entity,
            descendant_config_entity_groups,
            descendant_permission_lookup,
            permission_key_class=DbEntityPermissionKey,
            process_parent_config_entity_groups=False,
            **kwargs)

    reset_queries()
