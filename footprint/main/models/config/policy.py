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

from itertools import product
from django.db import models
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.key import Key
from footprint.main.mixins.scoped_key import ScopedKey
from footprint.main.mixins.shared_key import SharedKey
from footprint.main.mixins.tags import Tags
from footprint.main.mixins.name import Name
from footprint.main.models.config.model_pickled_object_field import ModelPickledObjectField

__author__ = 'calthorpe_analytics'


class PolicyLookup(object):

    def annualize_benchmark_years(self, base_year, future_year):
        yearly_efficiency_dict = {base_year: 1}
        increment = future_year - base_year
        benchmark_years = sorted(self.values.keys())

        previous_year = base_year
        for year in benchmark_years:
            previous_year_efficiency = self.values.get(previous_year, 0)
            current_year_efficiency = self.values.get(year)
            annual_efficiency_improvement = (current_year_efficiency - previous_year_efficiency) / (year-previous_year)

            yearly_efficiency_dict.update({
                y: (1 - previous_year_efficiency) - ((abs(previous_year - y)) * annual_efficiency_improvement)
                for y in range(previous_year, year)
            })

            previous_year = year
            yearly_efficiency_dict[year] = 1 - current_year_efficiency

        return yearly_efficiency_dict

    def get_building_efficiency_assumptions(self, types, uses=['commercial', 'residential']):
        """
        an abstracted form used by both energy and water engines that builds the dict of
        :param policy_set:
        :param types:
        :param uses:
        :return:
        """
        # todo: this would be easier if we were using the same keys in the analysis as we do in the policy set

        assumptions = {}
        get_policy = lambda key: self.policy_by_key(key)

        for type, use in product(types, uses):
            assumption = dict(type=type, use=use)
            assumption_dict = {

                # Use efficiency Assumptions
                "{use}_{type}_new_construction_efficiency".format(**assumption):
                get_policy('{use}_{type}_new_construction_efficiency'.format(**assumption)),

                '{use}_{type}_new_retrofit_efficiency'.format(**assumption):
                get_policy('{use}_{type}_new_retrofit_efficiency'.format(**assumption)),

                '{use}_{type}_base_retrofit_efficiency'.format(**assumption):
                get_policy('{use}_{type}_base_retrofit_efficiency'.format(**assumption)),

                # rates for building turnover
                '{use}_{type}_annual_new_retrofit_rate'.format(**assumption):
                float(get_policy('{use}_{type}_rates.annual_new_retrofit_rate'.format(**assumption))),

                '{use}_{type}_annual_base_retrofit_rate'.format(**assumption):
                float(get_policy('{use}_{type}_rates.annual_base_retrofit_rate'.format(**assumption))),

                '{use}_{type}_annual_base_replacement_rate'.format(**assumption):
                float(get_policy('{use}_{type}_rates.annual_base_renovation_rate'.format(**assumption)))
            }
            assumptions.update(assumption_dict)
        return assumptions

    def policy_by_key(self, key_path):
        """
            Retrieve a policy by key path. Recurses into the policies to match the given path.
        :param key_path:
        :return: The matching policy value or none
        """
        keys = key_path.split('.') if key_path else []

        if len(keys) == 0:
            # The path resolved to a policy or policy_set
            return self

        # Try to find a policy that matches the first key
        child_policies = self.policies.filter(key=keys[0])
        if len(child_policies) != 1:
            # If not found
            if len(keys) == 1:
                # Try to find a value that matches the key
                return self.values.get(keys[0], None)
            return None
        # If found, recurse on the remaining keys
        return child_policies[0].policy_by_key('.'.join(keys[1:]))


class Policy(SharedKey, Name, Tags, PolicyLookup):
    """
        A Policy is a loosely defined data structure. That represents a policy of a policy set. Policies may be shared
        across sets. Their semantic meaning may be determined by their shared key and they may be categorized by their
        tags. A policy has a range of possible values, anything from True/False to a number range or anything else that
        can be selected and have meaning. The range is serialized by the values attribute. Classes that have PolicySet
        attributes, namely ConfigEntity instances, should store the actual selected value of each Policy in a separate
        data structure ConfigEntity instances store policy settings in ConfigEntity.selections.policy_sets. See that
        attribute to understand how policy value selections are stored.

    """
    schema = models.CharField(max_length=100, null=True)
    objects = GeoInheritanceManager()
    policies = models.ManyToManyField('Policy', default=lambda: [])
    # Pickle the set of values into a single string field
    # The allowed values of the policy. This should be anything that can be serialized and represented on the client
    values = PickledObjectField()

    def update_or_create_policy(self, policy_config):
        child_policy = Policy.objects.update_or_create(
            key=policy_config['key'],
            schema='%s__%s' % (self.schema, policy_config['key']) if self.schema else policy_config['key'],
            defaults=dict(
                name=policy_config['name'],
                description=policy_config.get('description', None),
                values=policy_config.   get('values', {})
            ))[0]
        if policy_config.get('policies', None) and len(policy_config['policies']) > 0:
            child_policy.policies.add(*map(lambda child_policy_config:
                                           child_policy.update_or_create_policy(child_policy_config), policy_config['policies']))
        return child_policy

    class Meta(object):
        app_label = 'main'
