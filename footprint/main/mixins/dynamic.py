
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

from footprint.main.utils.model_utils import classproperty
from footprint.main.utils.utils import resolve_module_attr

__author__ = 'calthorpe_analytics'


class Dynamic(object):

    # Set this in the implementor
    # The string name of the class that is used to create dynamic subclasses for the implementor
    dynamic_model_class_creator_class = None

    @classproperty
    def dynamic_model_class_creator(cls):
        """
            Resolve the DynamicModelClass creator subclass instance that created this class
        :return:
        """
        if cls.Meta.abstract:
            raise Exception("Cannot resolve a DynamicModelClassCreator instance for an abstract class.")
        return resolve_module_attr(cls.dynamic_model_class_creator_class).from_dynamic_model_class(cls)
