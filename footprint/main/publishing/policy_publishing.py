
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

#from memory_profiler import profile
from footprint.main.models.config.policy_set import PolicySet
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.policy import Policy
from footprint.main.models.config.scenario import Scenario
from footprint.main.publishing.instance_bundle import InstanceBundle

__author__ = 'calthorpe_analytics'


def update_or_create_policy_sets(config_entity, **kwargs):
    """
        Creates a ResultLibrary and its Result instances upon saving a config_entity if they do not yet exist.
    :param config_entity
    :param kwargs
    :return:
    """

    # Create top-level policy if needed.
    global_policy = Policy.objects.update_or_create(
        key='global',
        schema=None,
        defaults=dict(
            name='Global',
            description='The parent policy of all',
            values={}
        ))[0]

    if isinstance(config_entity, GlobalConfig):

        from footprint.client.configuration.utils import resolve_fixture
        from footprint.client.configuration.fixture import PolicyConfigurationFixture
        client_policy = resolve_fixture(
            "policy",
            "policy",
            PolicyConfigurationFixture,
            config_entity.schema(),
            config_entity=config_entity)

        # Create each policy set and store them as a dict keyed by their key
        for policy_set_config in client_policy.policy_sets():
            policy_set = PolicySet.objects.update_or_create(
                key=policy_set_config['key'],
                defaults=dict(
                    name=policy_set_config['name'],
                    description=policy_set_config.get('description', None)
                )
            )[0]
            policies = map(lambda policy_config: global_policy.update_or_create_policy(policy_config), policy_set_config.get('policies', []))
            policy_set.policies.add(*policies)
            config_entity.add_policy_sets(policy_set)

#@profile
def on_config_entity_post_save_policy(sender, **kwargs):
    """
        Sync a ConfigEntity's ResultPage presentation
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    update_or_create_policy_sets(config_entity, **kwargs)


def on_db_entity_save():
    """
    respond to whenever a db entity is added or updated
    :return:
    """
    pass


def on_layer_style_save():
    """
    respond to any changes in style (
    :return:
    """
    pass


#@profile
def on_config_entity_post_save(sender, **kwargs):
    """
        Sync tilestache to a ConfigEntity class after the latter is saved
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)


def on_config_entity_pre_delete_results(sender, **kwargs):
    """
        Sync geoserver to a ConfigEntity class after the latter is saved
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
