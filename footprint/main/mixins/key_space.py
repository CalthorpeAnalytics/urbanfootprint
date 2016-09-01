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

from footprint.main.utils.subclasses import best_matching_subclass

__author__ = 'calthorpe_analytics'

class KeySpace(object):
    """
        Creates key spaces that are optionally unique by defining a Fab.prefix method which returns the
        prefix for the key space. Prefixes are rarely required, but are useful for quickly understanding
        what subclass an instance belongs to that has a key attribute. For BuiltForms, they are mandatory
        because of the FlatBuiltForm class (which probably needs refactoring)
    """

    model_class = None
    @classmethod
    def for_model(cls, model_class):
        """
            Return the KeySpace subclass matching the model_class
        :param model_class:
        :return:
        """
        def model_class_is_subclass(subclass):
            try:
                return issubclass(model_class, subclass.model_class)
            except Exception:
                raise Exception("subclass %s's model_class is not a model_class: %s" % (subclass, subclass.model_class))

        return best_matching_subclass(
            cls,
            model_class_is_subclass
        )

    class Fab(object):
        """
            This inner class is declared on all Keys subclasses (which inherit from this class.)
            It allows constant key definitions in the form FOO = Fab.ricate('foo'), leading to FOO == 'class_prefix__foo'
            The subclasses is needed only because a class can't reference itself in its declaration
        """
        _keys = {}

        @classmethod
        def reg(cls, raw_key):
            """
                Registers a new raw_key, returning the raw_key
                Keys only need to be registered if they need to be returned by the keys property
            :param raw_key:
            :return: The raw_key
            """
            if not cls._keys.get(cls):
                cls._keys[cls] = []

            keys = cls._keys[cls]
            if raw_key in keys:
                raise Exception("Key %s already registered for cls %s" % (raw_key, cls))
            keys.append(raw_key)
            return raw_key

        @classmethod
        def keys(cls):
            """
                Returns all registered keys with their prefixes
            :return:
            """
            return cls._keys

        @classmethod
        def ricate(cls, key):
            """
                Creates the key by joining the prefix to the given key.
            :param cls:
            :param key:
            :return:
            """
            return "__".join(cls.prefixes() + [key])

        @classmethod
        def remove(cls, fabricated_key):
            """
                Removes the prefix from a Fab.ricate'd key
            """
            return fabricated_key.split('__')[-1]

        @classmethod
        def prefixes(cls):
            prefix = cls.prefix()
            return super(KeySpace.Fab, cls).prefixes() if hasattr(super(KeySpace.Fab, cls), 'prefixes') else [] + [
                prefix] if prefix else []

        @classmethod
        def prefix(cls):
            """
                Prepends a prefix to a key value. This will use super to join parent prefixes with an '__'. If no
                prefix is specified the class will not contribute one
            :return:
            """
            return None

    @classmethod
    def prefix(cls):
        """
            Returns the prefix of the KeySpace subclass
        :return:
        """
        return cls.Fab.prefix()
