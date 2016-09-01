
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
from picklefield import PickledObjectField
from picklefield.fields import dbsafe_decode, PickledObject, _ObjectWrapper
from footprint.main.lib.functions import map_dict_to_dict
from footprint.main.utils.utils import resolvable_model_name, resolve_model

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)


class ModelPickledObjectField(PickledObjectField):
    """
        Simplifies pickling of model instances by just storing the class name
        and id, since the models are obviously stored elsewhere in the database
    """

    def pre_save(self, model_instance, add):
        """
            Simplify the model instance to an id and class name to avoid
            expensive pickling
        """
        if model_instance.id == 0:
            raise Exception("Attempt to pickle unsaved model instance: %s" % model_instance)
        simple_dict = dict(
            class_name=resolvable_model_name(model_instance.__class__),
            id=model_instance.id
        )
        return super(ModelPickledObjectField, self).pre_save(simple_dict, add)

    def to_python(self, value):
        """
            Resolve the model from the class name and id
        """
        simple_dict = super(ModelPickledObjectField, self).to_python(value)
        if simple_dict:
            return resolve_model(simple_dict['class_name']).objects.get(id=simple_dict['id'])
        return simple_dict


class SelectionModelsPickledObjectField(PickledObjectField):
    """
        Simplifies pickling of model instances by just storing the class name
        and id, since the models are obviously stored elsewhere in the database
        This expects a dict in the form
        dict(sets=dict(policy_set=model, built_form_set=model),
             db_entities=dict(foo_db_entity_key=foo_db_entity_model, ...))
    """

    @staticmethod
    def pk_of_model(model_instance):
        if not model_instance:
            return model_instance
        if model_instance.pk == 0:
            raise Exception("Can't pickle unsaved model instance: %s" % model_instance)
        return model_instance.pk

    def get_db_prep_value(self, value, connection=None, prepared=False):
        """
            Simplify the model instance to an id and class name to avoid
            expensive pickling
        """
        mapped_dict = map_dict_to_dict(lambda key, inner_dict:
            [key, map_dict_to_dict(lambda inner_key, model_instance:
                [inner_key, dict(
                    class_name=resolvable_model_name(model_instance.__class__),
                    pk=self.pk_of_model(model_instance)
                )] if model_instance else None, # Should never be null, but sometimes i
                inner_dict
            )],
            value)
        return super(SelectionModelsPickledObjectField, self).get_db_prep_value(mapped_dict, connection, prepared)

    _model_cache = {}

    def model_from_class_name_and_pk(self, model_dict):
        try:
            model_class = self.__class__._model_cache.get(model_dict['class_name'], None)
            if not model_class:
                model_class = self.__class__._model_cache[model_dict['class_name']] = resolve_model(model_dict['class_name'])
            return model_class.objects.get(pk=model_dict['pk'])
        except:
            logger.warn("pk %s of model class %s not found. This should not happen unless the model is being deleted" % (model_dict['pk'], model_dict['class_name']))
            return None

    def to_python(self, value):
        """
            Resolve the model from the class name and id
        """
        if value is not None:
            try:
                value = dbsafe_decode(value, self.compress)
            except:
                # If the value is a definite pickle; and an error is raised in
                # de-pickling it should be allowed to propogate.
                if isinstance(value, PickledObject):
                    raise
            else:
                # If the value was encoded (not from cache, convert it here back to our
                # desired format)
                if value:
                    if isinstance(value, _ObjectWrapper):
                        unwrapped_value = value._obj
                    else:
                        unwrapped_value = value

                    return map_dict_to_dict(lambda key, inner_dict:
                        [key, map_dict_to_dict(lambda inner_key, model_dict:
                            [inner_key,
                             self.model_from_class_name_and_pk(model_dict)],
                            inner_dict
                        )],
                        unwrapped_value)
        # Value from cache, leave alone
        return value
