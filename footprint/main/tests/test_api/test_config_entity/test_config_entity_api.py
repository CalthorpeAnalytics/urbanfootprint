
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

from django.contrib.auth.models import Group
from nose.tools import assert_is_none, assert_is_not_none

from footprint.main.lib.functions import map_to_dict, map_to_dict_with_lists, \
    get_first_value_or_none, flatten, unique, compact_dict, merge_dict_list_values
from footprint.main.tests.test_api.api_test import ApiTest
from footprint.main.tests.test_models.test_config_entity.test_config_entity_permissions import \
    TestConfigEntityPermissions


__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class TestConfigEntityApi(ApiTest):

    def test_config_entity_api__permissions(self):
        """
            Make sure that users only get ConfigEntity's that match their permission settings
        :return:
        """

        permission_configuration = TestConfigEntityPermissions.config_entity_configuration()
        resource_name = 'config_entity'

        # Iterate through the test_configurstions and extract a user for each group_key
        # Make a dict with the user as the key and all the instances from the test_config that the
        # user corresponds to. This gives a lookup of a user to the config_entities that we expect
        # the user to be able to view
        # Create a user->instances dict
        # Combine our {user1:instances, user2:instances,...} dicts
        user_to_expected_instances = merge_dict_list_values(
            *map(
                lambda test_configuration:\
                    # Combine our [user, instance] pairs into {user1:instances, user2:instances,...}
                    # Remove null keys (owing to groups with no users)
                    compact_dict(map_to_dict_with_lists(
                        # Each test_configuration has several groups.
                        # For each group resolve a user and return [user, instance]
                        lambda group_key: [
                            get_first_value_or_none(Group.objects.get(name=group_key).user_set.all()),
                            test_configuration['instance']],
                        test_configuration['groups'].keys())),
                permission_configuration.test_configuration)
        )

        all_instances = set(unique(flatten(user_to_expected_instances.values())))
        for user, instances in user_to_expected_instances.items():
            other_instances = all_instances - set(instances)
            # Fetch all instances with this user and create a lookup so we can test
            # that the resulting instances are present or not present as expected according to
            # the permissions
            response = self.get(resource_name, user=user)
            result_instance_lookup = map_to_dict(
                lambda instance_dict: [int(instance_dict['id']), instance_dict],
                self.deserialize(response)['objects'])

            for instance in instances:
                matching_instance = result_instance_lookup.get(instance.id)
                assert_is_not_none(matching_instance,
                                   "User %s should have view permission to instance %s with id %s and key %s but does." % \
                                   (user.username,
                                    instance,
                                    instance.id,
                                    permission_configuration.key_class.Fab.remove(
                                        permission_configuration.instance_key_lambda(instance))))

            for instance in other_instances:
                assert_is_none(matching_instance,
                                   "User %s should not have view permission to instance %s with id %s and key %s but does." % \
                                   (user.username,
                                    instance,
                                    instance.id,
                                    permission_configuration.key_class.Fab.remove(
                                        permission_configuration.instance_key_lambda(instance))))
