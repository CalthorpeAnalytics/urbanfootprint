
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
from __builtin__ import staticmethod

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.db.models import GeometryField
from django.db.models import ForeignKey, DateTimeField, TextField
from django.db.models.fields import Field, IntegerField
from tastypie.fields import ToManyField, OneToOneField
from tastypie.utils.timezone import now

from footprint.main.lib.functions import map_to_dict, merge, unique, flat_map, filter_dict, my_deep_copy, first, any_true, remove_keys
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.dynamic_model_class_creator import DynamicModelClassCreator
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.geospatial.feature_version import feature_revision_manager
from footprint.main.utils.dynamic_subclassing import get_dynamic_model_class_name, dynamic_model_class, \
    resolve_dynamic_model_class
from footprint.main.utils.inline_inspectdb import InlineInspectDb
from footprint.main.utils.model_utils import limited_api_fields
from footprint.main.utils.query_parsing import related_field_paths_to_fields
from footprint.main.utils.utils import resolve_module_attr, split_filter
from footprint.utils.utils import timestamp, get_property_path

logger = logging.getLogger(__name__)

class FeatureClassCreator(DynamicModelClassCreator):

    # A special key for the FeatureClassConfiguration when it exists independent of a DbEntity,
    # which is only true for uploaded feature tables that haven't been processed yet
    DETACHED_FROM_DB_ENTITY = 'detached_from_db_entity'

    db_entity = None

    def __init__(self, config_entity=None, db_entity_or_feature_class_configuration=None, no_ensure=False):
        """
            Creates a FeatureClassCreator for the given ConfigEntity, and optionally specific to a DbEntity of the ConfigEntity.
            The DbEntity must have a feature_class_configuration in order to create a Feature class
        """
        if isinstance(db_entity_or_feature_class_configuration, FeatureClassConfiguration):
            # Some base class methods pass in the configuration to the constructor--resolve the DbEntity
            # If this configuration is detached there is no db_entity
            if db_entity_or_feature_class_configuration.key != self.DETACHED_FROM_DB_ENTITY:
                self.db_entity = config_entity.computed_db_entities(key=db_entity_or_feature_class_configuration.key)[0]
        else:
            self.db_entity = db_entity_or_feature_class_configuration
        super(FeatureClassCreator, self).__init__(
            config_entity,
            self.resolve_configuration(self.db_entity) if self.db_entity else db_entity_or_feature_class_configuration,
            no_ensure)

    @classmethod
    def from_dynamic_model_class(cls, dynamic_model_class):
        """
            Gets the FeatureClassCreator based on the config_entity and db_entity, or
            from the config_entity and configuration if no db_entity exists
        :return:
        """
        return FeatureClassCreator(
            dynamic_model_class.config_entity,
            dynamic_model_class.db_entity if \
                dynamic_model_class.configuration.key != cls.DETACHED_FROM_DB_ENTITY else \
                dynamic_model_class.configuration)

    @classmethod
    def resolve_configuration(cls, db_entity):
        return db_entity.feature_class_configuration

    def db_entity_to_feature_class_lookup(self):
        """
            Returns the db_entity to feature_classes of the config_entity.computed_db_entities()
        :return:
        """
        return map_to_dict(lambda db_entity: [db_entity, FeatureClassCreator(self.config_entity, db_entity).dynamic_model_class()],
                           filter(lambda db_entity: db_entity.feature_class_configuration, self.config_entity.computed_db_entities()))

    def dynamic_model_configurations(self):
        """
            Returns all of the DbEntities of the config_entity that have a feature_class_configuration and are not provisional
        """
        db_entities = self.config_entity.computed_db_entities(
            no_feature_class_configuration=False, feature_class_configuration__isnull=False
        )
        valid_db_entities, invalid_db_entities = split_filter(
            lambda db_entity: not db_entity.feature_class_configuration or db_entity.is_valid, db_entities
        )
        return valid_db_entities

    def dynamic_model_configuration(self, key):
        """
            Find the DbEntity matching the key. Then get its FeatureClassConfiguration version
        """
        try:
            return filter(
                lambda feature_class_configuration: feature_class_configuration.key == key,
                self.dynamic_model_configurations())[0]
        except:
            logging.exception("No FeatureClassConfiguration exists with key %s", key)
            raise

    def ensure_dynamic_models(self):
        """
            For a given run of the application, make sure that all the dynamic model classes of the config_entity have been created.
            We only want to create model classes once per application run, and once they are created below we shouldn't have to check
            to see if they exist. If need models are created by layer import, etc, that process is responsible for creating the classes,
            and then they will be created here on the subsequent application runs
        """
        if self.no_ensure:
            logger.warn('Skipping ensure_dynamic_models for %s. no_ensure = %s, created = %s',
                        self, self.no_ensure, self.config_entity._dynamic_model_class_created)
            return False

        # Creates the dynamic feature classes
        filtered_db_entities = filter(
            lambda db_entity: not db_entity.no_feature_class_configuration and db_entity.feature_class_configuration,
            self.config_entity.computed_db_entities())
        logger.debug("For ConfigEntity %s will ensure the following DbEntities: %s" %
                     (self.config_entity.key, ', '.join(map(lambda db_entity: db_entity.key, filtered_db_entities))))
        for db_entity in filtered_db_entities:
            FeatureClassCreator(self.config_entity, db_entity, no_ensure=True).dynamic_model_class()

        # Creates the dynamic geography classes
        self.dynamic_geography_classes

        # Prevent a rerun by setting this flag to True now that we're done
        self.config_entity._dynamic_model_class_created = True

    @property
    def resolved_geography_scope(self):
        """
            The config_entity id ancestor whose geography table is used by this ConfigEntity depends on its class.
            This is always self.config_entity except for Scenario, which always uses the Project scope,
            since scenarios never define a primary geography
        """
        config_entity = self.config_entity.subclassed
        primary_geography_scope = self._resolve_geography_scope(config_entity)
        if not primary_geography_scope:
                raise Exception("No Primary Geography found at any scope for FeatureClassConfiguration with ConfigEntity %s" % self.config_entity.name)
        return primary_geography_scope

    def _resolve_geography_scope(self, config_entity):
        primary_geographies = [config_entity.db_entity_feature_class(db_entity.key)
                                 for db_entity in config_entity.owned_db_entities() if
                                 get_property_path(db_entity, 'feature_class_configuration.primary_geography')]
        if len(primary_geographies) > 0:
            # Primary geography at this scope
            return config_entity
        else:
            # Try again with the parent ConfigEntity
            if not config_entity.parent_config_entity:
                return None
            return self._resolve_geography_scope(config_entity.parent_config_entity_subclassed)


    def dynamic_geography_class_name(self, geography_scope_id=None):
        """
            Returns the Geography class for the given config_entity scope, or by default the scope
            of this feature_class_configuration, which is that of its config_entity
        :param geography_scope_id: Optional config_entity scope id for which to fetch the Geography class
        :return:
        """
        return get_dynamic_model_class_name(resolve_module_attr('footprint.main.models.geographies.geography.Geography'),
                                            geography_scope_id or self.geography_scope.id)

    def dynamic_geography_class(self, geography_scope=None):
        """
            Return the geography class based on the db_entity or config_entity
            :param geography_scope. Optional geography_scope override. By default
            self.geogrpahy_scope is used
        """
        scope = geography_scope or self.geography_scope

        return dynamic_model_class(
            resolve_module_attr('footprint.main.models.geographies.geography.Geography'),
            scope.schema(),
            'geography',
            self.dynamic_geography_class_name(geography_scope.id if geography_scope else None),
            scope=scope
        )

    def geographies_field(self, geography_scope):
        """
            Returns the ManyToMany field of the Feature class that relates it to the
            given geogrpahy scope, which is the ConfigEntity equal to or greater than self.config_entity
        :param geogrpahy_scope: Optional. Defaults to the config_entity's geography scope
        :return:
        """
        # The field is always named 'geographies_[scope_id]'
        return getattr(self.dynamic_model_class(), 'geographies_%s' % geography_scope.id).field

    @property
    def primary_geography_feature_class(self):
        """
            Finds the DbEntity which is the primary_geography and creates its feature_class
        :return:
        """
        db_entity = first(
            lambda db_entity: db_entity.feature_class_configuration.primary_geography,
            self.dynamic_model_configurations())
        if not db_entity:
            raise Exception("No primary geography feature class found for ConfigEntity %s" % self.config_entity)
        return self.__class__(self.config_entity, db_entity).dynamic_model_class()

    @property
    def geography_scope(self):
        return ConfigEntity._subclassed_by_id(self.configuration.geography_scope \
                                                                 if self.configuration and self.configuration.key else \
                                                                 self.config_entity.id)

    def common_geography_scope(self, related_feature_class):
        """
            Find the geography_scope that self.configuration shares with the related_feature_class.
            For instance, if this is a Project scope and the related_feature_class is a Scenario scope,
            the common scope is the Project, assuming the Scenario belongs to the project. For
            two Scenarios of the same Project the common scope is the Project
        :return:
        """
        related_feature_class_creator = self.__class__.from_dynamic_model_class(related_feature_class)
        common_ancestor = self.geography_scope.resolve_common_ancestor(related_feature_class_creator.geography_scope)
        if not common_ancestor:
            raise Exception("No common ancestor between %s and %s. This should not be possible" % (self.config_entity.name, related_feature_class.config_entity.name))
        # Now that we have a common ancestor, we need to go up the ancestor tree until we find a ConfigEntity that
        # has a primary geography. For instance, two Project DbEntities or a Project and Scenario DbEntity both
        # have the Project as the common ancestor, but it might be that only the Region has a primary_geography
        while not self.__class__(common_ancestor,  no_ensure=True).config_entity_has_primary_geography:
            if not common_ancestor.parent_config_entity:
                raise Exception("Reached GlobalConfig without finding a ConfigEntity with a primary geography.")
            common_ancestor = common_ancestor.parent_config_entity

        return common_ancestor

    def common_geography_class(self, related_feature_class):
        """
            Find the common Geography of this feature class and a related feature_class
        :param related_feature_class:
        :return:
        """

        common_geography_scope = self.common_geography_scope(related_feature_class)
        return self.dynamic_geography_class(common_geography_scope)

    @property
    def dynamic_geography_classes(self):
        """
            Returns the dynamic Geography class for this Feature class and all the ConfigEntities above it that
            define a Geography class
        :return:
        """
        if not self.config_entity.parent_config_entity:
            return []
        parent_config_entity = self.config_entity.parent_config_entity_subclassed
        geography_classes = [self.dynamic_geography_class()]
        if not isinstance(parent_config_entity, GlobalConfig):
            geography_classes.extend(self.__class__(config_entity=parent_config_entity).dynamic_geography_classes)

        return geography_classes


    def has_dynamic_model_class(self):
        """
            Returns true if the instance has an abstract_class configured
        """
        feature_class_configuration = self.configuration
        if not feature_class_configuration:
            return None
        return feature_class_configuration.abstract_class_name

    def geography_scopes(self, with_existing_tables_only=True):
        """
            Returns all of the geography scopes for this config_entity, beginning with itself and ascending
            up until but not including the GlobalConfig
        :param with_existing_tables_only: Default True. Only return geography scopes that have a representative
        geography table, meaning that a DbEntity exists at that scope that is the primary_geography. This
        is useful to prevent trying to join to geography tables at scopes where they don't exist.
        :return:
        """
        return unique(filter(
            lambda config_entity: not with_existing_tables_only or\
                                  self.__class__(config_entity,  no_ensure=True).config_entity_has_primary_geography,
            self.geography_scope.ascendants()[:-1]
        ))

    def dynamic_model_class(self, base_only=False, schema=None, table=None):
        """
            Gets or creates a DbEntity Feature subclass based on the given configuration.
            There are two classes get or created. The base models the imported table.
            The child subclasses the base and adds relations. This way the imported table is not manipulated.
            The child class is returned unless base_only=True is specified
        :params base_only: Default False, indicates that only the base feature class is desired, not the subclass
            that contains the relationships
        :return: The dynamic subclass of the subclass given in feature_class_configuration or None
        """
        if not self.configuration:
            # Return none if no self.configuration exists
            return None

        if not self.configuration.class_attrs or len(self.configuration.class_attrs) == 0:
            raise Exception("Class attributes missing from configuration for db_entity %s" %
                            self.db_entity.full_name if self.db_entity else self.configuration.key)

        if self.configuration.feature_class_owner:
            # If a different DbEntity owners owns the feature_class (e.g. for Result DbEntities), delegate
            self.__class__(
                self.config_entity,
                self.config_entity.computed_db_entities().get(key=self.configuration.feature_class_owner),
                # Same config_entity, ensuring would cause infinite recursion
                no_ensure=True
            ).dynamic_model_class(base_only)

        # Create the base class to represent the "raw" table
        try:
            abstract_feature_class = resolve_module_attr(self.configuration.abstract_class_name)
        except Exception, e:
            if not self.configuration:
                logging.exception("Corrupt DbEntity %s. No feature_class_configuration defined")
            if not self.configuration.abstract_class_name:
                logging.exception("Corrupt DbEntity %s. No feature_class_configuration.abstract_class_name defined")
            raise

        # Produce a list of fields that are defined in the configuration and do not match those
        # in the abstract Feature class
        existing_field_names = map(lambda field: field.name,
                                   filter(lambda field: isinstance(field, Field), abstract_feature_class._meta.fields))
        fields = filter(lambda field: isinstance(field, Field) and field.name not in existing_field_names+['id'], self.configuration.fields or [])

        # The id distinguishes the class. Use a random id if there is no db_entity
        id = self.db_entity.id if self.db_entity else timestamp()
        # Use the DbEntity table name if the former exists, otherwise just wake it with the configuration key
        schema = schema or (self.db_entity.schema if self.db_entity else self.configuration.key)
        table = table or (self.db_entity.table if self.db_entity else self.configuration.key)

        # Create the base Feature subclass. This points at the Feature table and is named based on the
        # Abstract Feature subclass or simply the Feature class along with the id of the ConfigEntity and DbEntity,
        # or a Timestamp for new Feature tables that don't yet have a DbEntity
        base_feature_class = dynamic_model_class(
            abstract_feature_class,
            schema,
            table,
            class_name="{0}{1}".format(abstract_feature_class.__name__, id),
            fields=map_to_dict(lambda field: [field.name, field], fields),
            # (no extra fields defined here in the parent)
            class_attrs=merge(self.configuration.class_attrs or {}, dict(configuration=self.configuration)),
            related_class_lookup=self.configuration.related_class_lookup or {}
        )

        # Make sure the base class fields are saved in the version.
        # Register the base class so we can exclude geometries.
        # This only needs to happen the first time a feature class is ever generated
        # I don't think it needs registration otherwise
        if not feature_revision_manager.is_registered(base_feature_class):
            feature_revision_manager.register(base_feature_class,
                           # Don't store the Geography, it never changes and is huge
                           # Our custom adapter will just grab it from the actual instance when deserializing
                           exclude=['geography', 'wkb_geometry']) # Never save geometries
        if base_only:
            # If the child class isn't needed, return the base
            return base_feature_class

        # Create the child class that subclasses the base and has the related fields
        # By convention the child class name simply adds 'rel' to that of the base class name
        class_name = "{0}{1}Rel".format(abstract_feature_class.__name__, id)
        existing_relation_class = resolve_dynamic_model_class(base_feature_class, class_name=class_name)
        if existing_relation_class:
            if not feature_revision_manager.is_registered(existing_relation_class):
                logger.warn('Registering existing rel class %s', existing_relation_class)
                parent_field_names = existing_relation_class.objects.parent_field_names(with_id_fields=False)
                feature_revision_manager.register(existing_relation_class,
                                                  follow=parent_field_names,
                                                  exclude=['geographies']) # Never save geometries
            return existing_relation_class

        # Get all Geography scopes for which to create a _geographies_[scope_id] association, up to but excluding the
        # GlobalConfig,
        ###NW - Changed with_existing_tables_only to true to filter out client Region which has no geography and no tables
        config_entity_geography_scopes = self.geography_scopes(with_existing_tables_only=True)

        logger.info('Creating feature class %s for table %s.%s', class_name, schema, '{0}rel'.format(table))

        relation_feature_class = dynamic_model_class(
            base_feature_class,
            schema,
            '{0}rel'.format(table),
            class_name=class_name,
            fields=merge(
                # Create all related fields. These are ForeignKey fields for single values and ManyToMany for many values
                self.create_related_fields(),
                # Create the ManyToMany geographies associations for each geography scope that associates the feature to
                # the primary geographies that it intersects. Even if this feature contains primary geographies,
                # there remains a many property in case there are multiple primary geography feature tables
                # The association is named geographies_[config_entity_scope_id]
                map_to_dict(
                    lambda geography_scope: ['geographies_%s' % geography_scope.id,
                                             models.ManyToManyField(
                                                self.dynamic_geography_class_name(geography_scope.id),
                                                db_table='"{schema}"."{table}_geography_{scope_id}"'.format(
                                                schema=schema,
                                                table=table,
                                                scope_id=geography_scope.id))],
                    config_entity_geography_scopes
                ),
                dict(
                     # The user who last updated the db_entity
                     updater=models.ForeignKey(User, null=True),
                     updated=DateTimeField(auto_now=True, null=False, default=now),
                     comment=TextField(null=True),
                     approval_status=TextField(null=True)
                ),
            ),
            class_attrs=merge(self.configuration.class_attrs or {}, dict(configuration=self.configuration)),
            related_class_lookup=self.configuration.related_class_lookup or {}
        )
        # an instance is saved
        parent_field_names = relation_feature_class.objects.parent_field_names(with_id_fields=False)
        if feature_revision_manager.is_registered(relation_feature_class):
            logger.warn("Trying to re-register relation_feature_class %s. This should not happen" % relation_feature_class)
        else:
            exclude = []
            for m2m, _ in relation_feature_class._meta.get_m2m_with_model():
                if m2m.name.startswith('geographies'):
                    exclude.append(m2m.name)

            feature_revision_manager.register(relation_feature_class,
                                              follow=parent_field_names,
                                              exclude=exclude)
        return relation_feature_class

    def dynamic_join_model_class(self, join_models, related_field_names):
        """
            Creates an unmanaged subclass of the feature class with extra fields to represent the
            the fields of the join_models. This also adds fields for any fields specified in the
            related_model_lookup. This is not for join models but ForeignKeys such as BuiltForm
            These latter fields must be specified explicitly because the main model and join models
            can't populate their foreign keys from the query because the query has to be
            a ValuesQuerySet in order to do the join. So we create id versions of the fields here
            (e.g. built_form_id) which the query can fill and then use that to manually
            set the foreign key reference in the Tastypie resource.
            :param join_models: Other feature models whose attributes should be added to the subclass
            :param related_field_names: List of field names of foreign key id fields (AutoFields)

        """
        main_model_class = self.dynamic_model_class()
        manager = main_model_class.objects
        # Exclude the following field types. Since the base Feature defines an id we'll still get that, which we want
        exclude_field_types = (ForeignKey, ToManyField, OneToOneField, GeometryField)
        all_field_paths_to_fields = merge(
            # Create fields to represented foreign key id fields
            # Our query fetches these ids since it can't fetch related objects (since its a values() query)
            map_to_dict(
                lambda field_name: [field_name.replace('__', '_x_'),
                                    IntegerField(field_name.replace('__', '_x_'), null=True)],
                related_field_names
            ),
            # The join fields for each joined related model
            *map(
                lambda related_model: related_field_paths_to_fields(
                    manager,
                    related_model,
                    exclude_field_types=exclude_field_types,
                    fields=limited_api_fields(related_model),
                    separator='_x_'),
                join_models)
        )

        abstract_feature_class = resolve_module_attr(self.configuration.abstract_class_name)
        # Make sure the class name is unique to the related models and the given ConfigEntity
        related_models_unique_id = '_'.join(sorted(map(lambda related_model: related_model.__name__, join_models), ))
        dynamic_model_clazz = dynamic_model_class(
            main_model_class,
            self.db_entity.schema,
            self.db_entity.table,
            class_name="{0}{1}{2}{3}Join".format(
                abstract_feature_class.__name__,
                self.db_entity.id,
                self.config_entity.id,
                related_models_unique_id),
            fields=all_field_paths_to_fields,
            class_attrs=self.configuration.class_attrs or {},
            related_class_lookup=self.configuration.related_class_lookup or {},
            is_managed=False,
            cacheable=False)
        logger.info("Created dynamic join model class %s" % dynamic_model_clazz)
        logger.debug("Created with model fields %s" % map(lambda field: field.name, dynamic_model_clazz._meta.fields))
        logger.debug("Created with related and join fields %s" % all_field_paths_to_fields)
        return dynamic_model_clazz

    @staticmethod
    def remove_auto(field):
        modified_field = my_deep_copy(field)
        modified_field.auto_created = False
        modified_field.primary_key = False
        return modified_field

    def feature_class_configuration_from_introspection(self):
        """
            Creates a dynamic Feature class configuration by introspecting the db_entity's Feature table.
        :return: The Feature class configuration
        """
        fields = InlineInspectDb.get_fields(self.db_entity.full_table_name)
        return self.generate_configuration(fields.values())

    def feature_class_configuration_from_metadata(self, metadata):
        """
            Creates a dynamic Feature class configuration from the given python metadata
            No DbEntity needs to be specified at self.db_entity for this case, since
            we often are generating a FeatureClassConfiguration from the metadata before
            andy DbEntity exists in order to show the user what they have uploaded.
            metadata is in the following form, for example:
            [ {u'auto_populate': True,
               u'default': u'SEQUENCE',
               u'editable': True,
               u'name': u'ogc_fid',
               u'nullable': False,
               u'type': u'integer',
               u'visible': True},

              {u'default': None,
               u'editable': True,
               u'geometry_type': u'MULTIPOLYGON',
               u'name': u'wkb_geometry',
               u'nullable': True,
               u'type': u'geometry',
               u'visible': True},

               {u'default': None,
               u'editable': True,
               u'name': u'name',
               u'nullable': True,
               u'type': u'string',
               u'visible': True}

               ... ]
        :return: The Feature class configuration
        """
        fields = map(
            lambda meta: self.resolve_field(meta),
            metadata
        )
        return self.generate_configuration(fields)

    @staticmethod
    def resolve_field(meta):
        type = meta['type']
        rest = merge(filter_dict(
            # Don't allow default='SEQUENCE'
            lambda key, value: not (key=='default' and value=='SEQUENCE'),
            # Ignore these keys
            remove_keys(meta, ['type', 'auto_populate', 'visible', 'geometry_type', 'nullable'])
        ), dict(null=True))
        if type=='string':
            return models.CharField(**rest)
        elif type=='integer':
            return models.IntegerField(**rest)
        elif type=='float':
            return models.FloatField(**rest)
        elif type=='biginteger':
            return models.BigIntegerField(**rest)
        elif type=='geometry':
            return models.GeometryField(geography=False, **rest)
        elif type=='date':
            return models.DateField(**rest)
        elif type=='datetime':
            return models.DateTimeField(**rest)

    def feature_class_configuration_from_geojson_introspection(self, data):
        """
            Creates a dynamic Feature class configuration by introspecting the db_entity's Feature table.
        :return: The Feature class configuration
        """
        properties = unique(flat_map(lambda feature: feature.properties.keys(), data.features))
        fields = map(lambda property: models.CharField(property), properties)
        return self.generate_configuration(fields)


    @property
    def config_entity_has_primary_geography(self):
        """
            Returns True if a primary geography exists at this ConfigEntity scope (not necessarily the geography_scope),
            meaning that at least one of its DbEntities is configured as a primary_geography. It checks this
            by verifying that the geography table of the dynamic Geography class for this config_entity exists
        """
        return any_true(
            lambda db_entity: db_entity.feature_class_configuration and \
                              db_entity.feature_class_configuration.primary_geography,
            self.config_entity.owned_db_entities())



    def generate_configuration(self, fields=[]):
        """
            Creates a feature_class_configuration for db_entities not pre-configured, in other words, those that
            were uploaded.
        """

        # Use the pk for the source_id_column
        primary_key_fields = filter(lambda field: field.primary_key, fields)
        # Use the existing primary key or default to the default Django one
        # The former case applies to imported tables that have primary keys, the latter to tables that are
        # created by Django
        source_id_column = primary_key_fields[0].name if primary_key_fields else 'id'

        return self.complete_or_create_feature_class_configuration(
            FeatureClassConfiguration(
                fields=fields,
                source_id_column=source_id_column,
                # Generated tells us that the feature_class_configuration wasn't pre-configured in code
                generated=True
            )
        )

    def complete_or_create_feature_class_configuration(self, feature_class_configuration, **overrides):
        """
            Clones the given feature_class_configuration to make it specific to the ConfigEntity
            If the feature_class_configuration is null a simple one is created
            :param feature_class_configuration: Used for the basis of cloning from another DbEntity, or
            as the preconfigured instance that was defined in an initializer, such as default_project.py
            :param overrides: Override anything in the feature_class_configuration. This is used for cloning
            when we need to specify generated=YES, source_from_origin_layer_selection=True, etc
        """
        if self.db_entity and self.db_entity.no_feature_class_configuration:
            # If nothing is passed it means that the DbEntity doesn't represent a feature table, e.g. background imagery
            return None

        key = self.db_entity.key if self.db_entity else self.DETACHED_FROM_DB_ENTITY

        return FeatureClassConfiguration(**merge(
            dict(
                # Indicates that the configuration was generated by introspecting a table, rather than by deliberate configuration
                generated=False,
                # Indicates that the features should be created from an origin LayerSelection features.
                source_from_origin_layer_selection=False,
                # The origin Layer id
                origin_layer_id=None,
                # The user of the origin layer
                origin_user=None,
                # The default data_importer for features
                # The default imports based on the url of the db_entity--usually a special database url
                data_importer=None,
            ),
            # Override the above with any configured attributes
            merge(feature_class_configuration.__dict__, overrides) if feature_class_configuration else {},
            # Override or define ConfigEntity specific attributes
            dict(
                key=key,
                # The scope is the id of the config_entity
                scope=self.config_entity and self.config_entity.id,
                # The config_entity id scopes the geography table, except for scenarios which
                # always use their Project config_entity id as the scope
                geography_scope=self.config_entity.id,
                schema=self.config_entity.schema(),
                class_attrs=merge(
                    feature_class_configuration.class_attrs if feature_class_configuration else {},
                    {'config_entity__id': self.config_entity.id, 'override_db': self.config_entity.db, 'db_entity_key': key}),
            ) if self.config_entity else dict(
                # Abstract case
                key=key,
                class_attrs=merge(
                    feature_class_configuration.class_attrs if feature_class_configuration else {},
                    {'db_entity_key': key})
            )
        ))


    def update_db_entity(self, feature_class_configuration):
        # Update our DbEntity so we have the configuration available for future operations
        # Note that we always want to generate the feature_class_configuration here if its generated in case
        # the table schema is updated and we need to modify the configuration
        self.db_entity.feature_class_configuration.__dict__.update(feature_class_configuration.__dict__)
        # Disable signals and update the DbEntity
        self.db_entity._no_post_post_save = True
        self.db_entity.save()
        self.db_entity._no_post_post_save = False
        # Update our reference
        self.configuration = self.db_entity.feature_class_configuration
