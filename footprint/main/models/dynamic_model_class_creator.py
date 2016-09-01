
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

from django.contrib.gis.db import models
from footprint.main.lib.functions import map_dict_to_dict, get_single_value_or_none, map_to_dict
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.utils.utils import resolve_module_attr

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class DynamicModelClassCreator(object):
    """
        Base class for creating dynamic model classes scoped to a ConfigEntity or something more specific.
    """

    config_entity = None
    configuration = None
    no_ensure = None

    def __init__(self, config_entity=None, configuration_or_container=None, no_ensure=False):
        """
            Initialize to the config_entity. This can be None if non-ConfigEntity specific config_entity
            classes are desired. The only thing that can be returned without a config_entity is the abstract
            model classes that are preconfigured.
            :param config_entity: The ConfigEntity
            :param configuration_or_container: The configuration describing the dynamic subclass,
            e.g. a FeatureClassConfiguration or AnalysisModuleConfiguration. A container to the configuration can
            be used instead in conjunction with the resolve_configuration function
            This is None to use methods that are only specific to the config_entity
        """
        from footprint.main.models.config.scenario import Scenario
        self.config_entity = config_entity.subclassed if config_entity and config_entity.__class__ in [ConfigEntity, Scenario] else config_entity
        self.configuration = configuration_or_container
        self.no_ensure = no_ensure
        if self.config_entity and not self.no_ensure:
            self.ensure_dynamic_models()

    @classmethod
    def from_dynamic_model_class(cls, dynamic_model_class):
        """
            If a dynamic model class already exists, use this to recreate the DynamicModelClassCreator class that created it
            :param dynamic_model_class: A dynamic_model_class that was created by this class
        :return:
        """
        raise NotImplementedError("You must override this method")

    @classmethod
    def resolve_configuration(cls, configuration_or_container):
        """
            If the instance that is passed in does not match the configuration that produces the dynamic class,
            map it here. For instance FeatureClassCreator converts a db_entity to db_entity.feature_class_configuration
        """
        return configuration_or_container

    def dynamic_model_configurations(self):
        raise NotImplementedError("Subclass must implement")

    def dynamic_model_configuration(self, key):
        raise NotImplementedError("Subclass must implement")

    def key_to_dynamic_model_class_lookup(self, configurations_or_containers=None):
        """
            Returns all configuration keys mapped to a dynamic subclass or None if no
            class is configured yet for the configuration
        :param config_entity: Used to scope the Feature classes. If no then abstract classes are returned
        :param configurations_or_containers: Optional specific set of configurations. These are the same type
        passed to the second argument of the constructor
        will be used. You must specify this before the db_entities have been created on the config_entity, for the case
        where the config_entity is null.
        :return: A dict keyed by db_entity key and valued by a dynamic model subclass or None
        """

        configurations = configurations_or_containers or self.dynamic_model_configurations()
        if not self.config_entity:
            return self.__class__.key_to_abstract_model_class_lookup(configurations)

        # Get the config_entity from the first self.db_entity_configuration with a feature_class_configuration
        # Get the corresponding db_entities from the config_entity
        existing_configurations = map(
            lambda configuration: self.dynamic_model_configuration(configuration.key),
            map(lambda configuration: self.__class__.resolve_configuration(configuration), configurations))

        return map_to_dict(lambda existing_configuration:
                                [existing_configuration.key,
                                 self.__class__(self.config_entity, existing_configuration, self.no_ensure).dynamic_model_class()],
                           existing_configurations)

    @classmethod
    def key_to_abstract_model_class_lookup(cls, configuration_or_containers):
        """
            Like self.db_entity_key_to_feature_class_lookup, but used when no ConfigEntity is in scope.
            This returns the abstract version of the Feature subclasses by self.db_entity_key
        :param configuration_or_containers:
        :return:
        """
        return map_to_dict(lambda configuration: [configuration.key,
                                                  resolve_module_attr(configuration.abstract_class_name)],
                           map(lambda configuration: cls.resolve_configuration(configuration), configuration_or_containers))

    def ensure_dynamic_models(self):
        """
            For a given run of the application, make sure that all the dynamic model classes of the config_entity have been created.
            We only want to create preconfigured model classes once per application run, and once they are created below we shouldn't have to check
            to see if they exist.
        """
        raise NotImplementedError("Define in subclass")
        return self.config_entity._dynamic_models_created

    @property
    def dynamic_model_class_is_ready(self):
        """
            Indicates if there is enough configuration information to create the dynamic subclass. Defaults to True
        """
        # This is a bit of a hack, but it's assumed the feature_class_configuration is ready when it has
        # an abstract_class, since this is the way that imported feature classes work.
        return self.configuration and\
               self.configuration.abstract_class_name and\
               (self.configuration.class_attrs and len(self.configuration.class_attrs) > 0)

    def dynamic_model_class(self):
        raise NotImplementedError("Subclass must implement this method")

    def generate_configuration(self, fields=[]):
        raise NotImplementedError("Subclass must implement this method")

    def clone_feature_class_configuration_for_config_entity(self, feature_class_configuration):
        raise NotImplementedError("Subclass must implement this method")

    def create_related_fields(self):
        """
            Create ForeignKey and ManyFields for each self.configuration.related_fields
        :return:
        """
        return map_dict_to_dict(
            lambda field_name, related_field_configuration: self.create_related_field(
                field_name,
                related_field_configuration),
            self.configuration.related_fields or {})

    def related_descriptors(self):
        """
            Returns the existing related field descriptors that were created by create_related_fields and assigned
            to the dynamic feature class
        :return: A dict keyed by field name, valued by the ManyToMany field or equivalent
        """
        dynamic_model_class = self.dynamic_model_class()
        return map_dict_to_dict(
            lambda field_name, related_field_configuration: [field_name, getattr(dynamic_model_class, field_name)],
            self.configuration.related_fields or {})

    def create_related_field(self, field_name, related_field_configuration):
        """
            Creates a ForeignKey or ManyToMany field based on related_field_configuration
        :param field_name:
        :param related_field_configuration: A dict containing related_key or related_class_name
            related_key: the instance of the sibling key of the config_entity whose dynamic_model_class is the relation type.
                For DbEntity/Features this would be the db_entity_key and the dynamic_model_class would be its FeatureClass
                For AnalysisModule this would be the analysis module key and its dynamic class
            related_class_name: rather than related_key, any model class, such as BuiltForm, to relate to.
            single: if True this is a ForeignKey (toOne) relationship. Otherwise a ManyToMany is created
        :return: A two-item tuple. First item is the field name and the second is the field.
        """

        config_entity = ConfigEntity._subclassed_by_id(self.configuration.scope)

        # TODO temp coverage of a key name name change
        related_field_configuration['related_key'] = related_field_configuration.get('related_key', related_field_configuration.get('related_db_entity_key'))

        if related_field_configuration.get('related_key', False):
            # field name matches name of peer self.db_entity_key--get it's feature class name
            related_db_entity = get_single_value_or_none(config_entity.computed_db_entities(key=related_field_configuration['related_key']))
            # Always call with no_ensure=True since the config_entity is the same. Otherwise we'd get infinite recursion
            related_class_name_or_model = self.__class__(self.config_entity, related_db_entity, no_ensure=True).dynamic_model_class()
        elif related_field_configuration.get('related_class_name', None):
            # A model class such as BuiltForm
            related_class_name_or_model = resolve_module_attr(related_field_configuration['related_class_name'])
        else:
            raise Exception("No related_key or related_class_name found on feature_class_configuration for self.configuration.key %s" % self.configuration.key)

        logger.info('Creating %r related field for %s using %s', related_field_configuration.get('single', None) and 'single' or 'm2m',
                    field_name, related_field_configuration)
        if related_field_configuration.get('single', None):
            return [field_name,
                    models.ForeignKey(related_class_name_or_model, null=True)]
        else:
            return [field_name,
                    models.ManyToManyField(related_class_name_or_model,
                                           # Pass a custom, readable table name for the through class for ManyToMany relations
                                           db_table='"{schema}"."{table}_{field_name}"'.format(
                                               schema=config_entity.schema(),
                                               table=self.configuration.key,
                                               field_name=field_name))]
