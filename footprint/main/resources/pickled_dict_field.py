
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

import string
from tastypie.fields import DictField, NOT_PROVIDED, ApiField
from footprint.main.lib.functions import map_dict_to_dict, deep_copy_dict_structure, my_deep_copy

__author__ = 'calthorpe_analytics'

class ObjectField(ApiField):
    """
    Handles any object by turning it into a dict by recursively using each object's __dict__ attribute
    Arrays are left as arrays
    Since class data is removed a reference instance would be needed to rehydrate it
    """
    dehydrated_type = 'dict'
    help_text = "A dictionary of data. Ex: {'price': 26.73, 'name': 'Daniel'}"

    def convert(self, value):
        if value is None:
            return None

        return my_deep_copy(value, True)

class PickledObjField(ObjectField):
    """
        For read-only configurations, dehydration of arbitrary object graphs. Hydration isn't possible without having a reference instance to know the classes
    """

    def dehydrate(self, bundle):
        """
            Handles the object dehydration
        :param bundle:
        :return:
        """

        # Deep copy the structure to create new dict instance so we don't mutilate the source
        obj = super(PickledObjField, self).dehydrate(bundle)
        return my_deep_copy(obj, True)


class PickledDictField(ApiField):

    def dehydrate(self, bundle):
        """
        :param bundle:
        :return:
        """

        # Deep copy the structure to create new dict instance so we don't mutilate the source
        try:
            if not isinstance(getattr(bundle.obj, self.attribute), dict):
                return {}
            value = super(PickledDictField, self).dehydrate(bundle)
            return my_deep_copy(value)
        except:
            setattr(bundle.obj, self.attribute, None) # value got deformed--clear it
            return my_deep_copy(super(PickledDictField, self).dehydrate(bundle))

    def hydrate(self, bundle):
        """
            Hydrates a dict of resource URI to the corresponding instances by resolving the URIs. Like dehydrate_selections, this could be generalized
        :param bundle:
        :return:
        """
        value = super(PickledDictField, self).hydrate(bundle)
        return value
