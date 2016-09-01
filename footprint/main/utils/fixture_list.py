
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

from footprint.main.lib.functions import all_existing_classes_subclass, all_existing_keys_match, remove_keys

__author__ = 'calthorpe_analytics'

class FixtureList(object):

    def __init__(self, fixtures):
        """
            An iterable class to filter fixtures by their properties. You can use one or more of the methods in a chain
            Example filterFunction(fixtures).matching_scope(fixture_scope=SomeClass).matching_keys(fixture_key=keys)
            where fixture_scope and fixture_key are both attributes of the fixtures
            :param fixtures: a list of dicts or objs representing configuration fixtures
        """
        self.fixtures = fixtures

    def __iter__(self):
        return self.fixtures.__iter__()

    def __add__(self, other):
        return FixtureList(self.fixtures+(other.fixtures if isinstance(other, FixtureList) else other))

    # Delegate all unknown methods to the fixtures
    def __getattr__(self, name):
        return getattr(self.fixtures, name)

    def matching_scope(self, delete_scope_keys=False, **kwargs):
        """
            Filters fixtures by given matching_dict. All keys specified in the matching_dict that are present
            in the fixture must match using isSubclass, where the matching_dict value must be a subclass of the
            fixture's value.
        :param delete_scope_keys: False by default, if true deletes any key specified in kwargs from the fixtures
        after testing the kwarg value against the fixture
        :param kwargs key/values whose values are classes.
        :return:
        """
        kwarg_keys = kwargs.keys()
        return self.__class__(map(lambda fixture: remove_keys(fixture, kwarg_keys) if delete_scope_keys else fixture,
                                  filter(lambda fixtures: all_existing_classes_subclass(fixtures, **kwargs),
                                         self.fixtures)))

    def matching_keys(self, **kwargs):
        """
            Filters fixtures by given matching_dict_obj. All keys specified in the matching_dict that are present
            in the fixture must match
        :param kwargs: key/values that are used to filter the fixtures. If the value is an array, the fixture is
        evaluated as values in fixture[key]. Otherwise it is evaluated as value==fixture[key]
        You may optionally specify a special 'non_matches' with a subset list of keys that should not match
        :return: The fixtures that pass the filter
        """
        return self.__class__(filter(lambda fixtures: all_existing_keys_match(fixtures, **kwargs), self.fixtures))
