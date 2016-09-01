
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

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group, UserManager
from tastypie.models import ApiKey
from django.conf import settings
from footprint.client.configuration.fixture import UserFixture
from footprint.main.lib.functions import get_single_value_or_create
from footprint.main.models.group_hierarchy import GroupHierarchy


__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)


def update_or_create_users():
    from footprint.client.configuration.utils import resolve_fixture
    init_fixture = resolve_fixture("user", "user", UserFixture, settings.CLIENT)
    for user_configuration in init_fixture.users():
        update_or_create_user(**user_configuration)


def update_or_create_group(name, config_entity=None, superiors=None):
    """
        Create a group and GroupHierarchy instance. Group is the Django Group model, whereas
        GroupHierarchy is a Footprint model that associates a Group to superior Groups and to
        a ConfigEntity
    :param name: Required name of the group
    :param config_entity: Optional. Required for config_entity scoped groups. Always null
    for the default groups (e.g. Admin, Directory)
    :param superiors: Optional superiors to the group. All groups should have superiors except
    for the Admin group
    :return:
    """
    group = get_single_value_or_create(
        Group.objects.filter(name=name),
        lambda: Group.objects.get_or_create(name=name)[0])
    # Make sure the group has full permission to every model
    # We limit permission on individual instances
    new_permissions = set(Permission.objects.all())-set(group.permissions.all())
    group.permissions.add(*new_permissions)
    # Track the superiors in our special class
    try:
        superior_groups = map(lambda superior: Group.objects.get(name=superior), superiors or [])
    except:
        raise Exception("Expected groups %s to exist but only these exist: %s" %\
              (superiors, Group.objects.values_list('name')))
    group_hierarchy, created, updated = GroupHierarchy.objects.update_or_create(
        group=group,
        defaults=dict(config_entity=config_entity)
    )
    if not created:
        group_hierarchy.superiors.clear()
    for superior_group in superior_groups:
        group_hierarchy.superiors.add(superior_group)
    return group

def update_or_create_user(username=None, password=None, email=None, api_key=None, groups=None, is_super_user=False, first_name=None, last_name=None):
    """
        Update/Create the user matching the username
    :param username: the User.username
    :param password: the password
    :param email: the user email
    :param api_key: the optional api_key, it will be generated otherwise
    :param groups: The names of the groups that this user belongs to
    :param is_super_user: Default false, True to make a superuser
    :param first_name: the user first name
    :param last_name: the user last name
    :return:
    """

    from footprint.main.publishing.user_publishing import on_user_post_save

    logger.info("Updating or creating user %s" % username)
    user_manager = get_user_model().objects
    user = get_single_value_or_create(
        user_manager.filter(username=username),
        lambda: user_manager.create_user(username, email, password) if \
            not is_super_user else \
            user_manager.create_superuser(username, email, password))


    # Update these in case the configuration was updated
    user.email = UserManager.normalize_email(email)
    if password:
        user.set_password(password)
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if is_super_user:
        user.is_superuser = True

    user.save()

    # Add the user to the groups.
    # Sometimes the users will reference Groups of sibling scenarios that
    # haven't been created yet. In this case just create a name-only
    # instance of the group.
    if groups:
        user.groups.clear()
        for group in groups:
            user.groups.add(Group.objects.get_or_create(name=group)[0])
        logger.info("Assigned user %s to groups %s",
            user.email,
            ', '.join(groups)
        )

    # Make sure the user has permission to update every class
    # We limit permissions on individual instances
    new_permissions = set(Permission.objects.all())-set(user.user_permissions.all())
    user.user_permissions.add(*new_permissions)
    api_key_instance = ApiKey.objects.get_or_create(user=user)[0]
    if api_key and api_key_instance.key != api_key:
        api_key_instance.key = api_key
        api_key_instance.save()

    # Invoke post-save publishing outside of footprint_init. footprint_init has a ConfigEntity-
    # centric way of publishing that this would clash with
    if not settings.FOOTPRINT_INIT:
        on_user_post_save(sender=get_user_model(), instance=user)

    return {'user': user, 'api_key': api_key_instance}
