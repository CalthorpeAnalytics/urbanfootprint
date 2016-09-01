
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
import sys

import re
from django.conf import settings
from django.contrib.gis.db import models
from django.db import connection
from inflection import titleize
from picklefield import PickledObjectField

from footprint.main.lib.functions import map_dict, accumulate, map_to_dict, merge, unique, remove_keys, one_or_none
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.categories import Categories
from footprint.main.mixins.cloneable import Cloneable
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.name import Name
from footprint.main.mixins.permissions import Permissions
from footprint.main.mixins.shared_key import SharedKey
from footprint.main.mixins.tags import Tags
from footprint.main.mixins.timestamps import Timestamps
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.models.feature.feature_field_mixin import FeatureFieldMixin
from footprint.main.models.geospatial.behavior import Behavior, BehaviorKey
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey
from footprint.main.models.geospatial.intersection import Intersection
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.model_utils import model_dict
from footprint.main.utils.utils import resolve_module_attr
from footprint.uf_tools import dictfetchall

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

class DbEntity(SharedKey, Name, Categories, Tags, Timestamps, Deletable, Cloneable, Permissions, FeatureFieldMixin):

    """
        Represents a database-derived entity, such as a table, view, or query result. Entities may have tags to help entity_configs that may be interested in them. The relationships between db_entities and entity_configs are registered by the DbEntityInterest class, which also defines the type of interest. Some db_entities are "owned" by one entity_config, while others might simply have an "observe" or "edit" or "dependency" relationship. These roles will be figured out later. The key indicates a specific function of the db_entity, such as "base" to indicate a table used for base data. Tags are broader descriptors, such as "university", used for categorization or queries. DbEntities use the SharedKey mixin to permit multiple DbEntities in the same context (e.g. those of a particular ConfigEntity interest) to share a key. This permits the user to assign multiple tables of the same key (e.g. 'base') to a ConfigEntity instance.
        TODO Tags are moving the FeatureFunction. They are depricated here
    """
    class Meta(object):
        abstract = False
        app_label = 'main'
        # Custom permissions in addition to the default add, change, delete
        permissions = (
            ('view_dbentity', 'View DbEntity'),
            # Permission to approve or reject feature updates to the DbEntity
            ('approve_dbentity', 'Approve DbEntity'),
        )

    objects = GeoInheritanceManager()

    # The optional schema and table or view name from which to base the layer. This will result in a query that selects all
    # rows from the table, and the table will be used to configure TileStache or Geoserver.
    # These might also identify the query as operating on the specified table and thus be useful for organization
    schema = models.CharField(max_length=100, null=True)
    table = models.CharField(max_length=100, null=True)
    srid = models.CharField(max_length=100, null=True)

    # Used for Results and similar that create a view of another DbEntity's data.
    # Holds the key that points to dynamic class info for this DbEntity. This key is normally None or the key of another
    # DbEntity, the latter if this DbEntity was cloned from another
    source_db_entity_key = models.CharField(max_length=50, null=True)

    # The user who created the db_entity
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='db_entity_creator')
    # The user who last updated the db_entity
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='db_entity_updater')

    # Describes how to configure the features of the table
    # This is currently a dict but will be come a first-class FeatureClassConfiguration
    feature_class_configuration = PickledObjectField(null=True)
    @property
    def feature_class_configuration_as_dict(self):
        return self.feature_class_configuration.__dict__
    @feature_class_configuration_as_dict.setter
    def feature_class_configuration_as_dict(self, value):
        self.feature_class_configuration = FeatureClassConfiguration(**value) if isinstance(value, dict) else value

    # Tracks post save publishing process for new DbEntities
    # This would be better handled with statuses, but tracking percent is the only
    # way to reliably track completion in the current multi-process post-save graph
    # The range of values are 0 to 100
    setup_percent_complete = models.IntegerField(default=100)

    @property
    def template_feature(self):
        """
            Creates an example instance of the DbEntity's Feature subclass so that the API can inspect the
            properties of the feature. We give this id 0 so that the API has something to load lazily.
            We don't want the API to have to nest the instance in the DbEntity
        :return:
        """
        return self.feature_class(id=0)


    def feature_attribute(self, attribute):
        """
            Creates an example instance of the DbEntity's Feature subclass so that the API can inspect the
            properties of the feature. We give this id 0 so that the API has something to load lazily.
            We don't want the API to have to nest the instance in the DbEntity
        :return:
        """
        return self.feature_class(id=0, attribute=attribute)

    # Set true for DbEntity's that don't reference features, namely background imagery
    no_feature_class_configuration = models.BooleanField(default=False)
    # Remote data, such as background layers, use a url instead of schema and table or as an import source
    url = models.CharField(max_length=1000, null=True)
    # An array of host url prefixes for url based db_entities
    hosts = PickledObjectField(null=True)
    # Indicates whether or not the behavior of the feature_behavior instance cannot be changed
    behavior_locked = models.BooleanField(default=False)

    # If feature_behavior is passed to the constructor, we stash the value temporarily
    # until after save. Then we use it to persist the feature_behavior with our DbEntity
    _feature_behavior = None
    # If categories is passed to the constructor, we stash the value temporarily
    # until after save. Then we use it to add the categories ot our DbEntity
    # This nonsense will go away when we stop using classes for fixtures
    __categories = None
    @property
    def _categories(self):
        return self.__categories

    @_categories.setter
    def _categories(self, value):
        self.__categories = value

    __tags = None
    @property
    def _tags(self):
        return self.__tags

    @_tags.setter
    def _tags(self, value):
        self.__tags = value

    # This is used by the API, specifically needed on the front end to get the new Layer of a new DbEntity
    @property
    def layer(self):
        from footprint.main.models.presentation.layer.layer import Layer
        try:
            return one_or_none(self.db_entity_interest_owner.presentationmedium_set.all().select_subclasses(Layer))
        except Exception, e:
            logger.warn(e.message)

    def save(self, force_insert=False, force_update=False, using=None):
        # Take care of the attached feature_behavior.
        # This will only be done in the resource save case, since other
        # saving uses update_of_create, which eliminates the possibility of an attached feature_behavior
        feature_behavior = self._feature_behavior
        categories = self._categories
        tags = self._tags
        super(DbEntity, self).save(force_insert, force_update, using)
        if feature_behavior and not self.featurebehavior_set.count() == 1:
            feature_behavior.db_entity = self
            feature_behavior.save()
        if categories:
            self.add_categories(*categories)
        if tags:
            self.clear_tags()
            self.add_tags(*tags)
        if not self.dbentityinterest_set.count() and self._config_entity:
            # If the DbEntityInterest doesn't exist yet, created.
            # Otherwise there is nothing to do, since no attribute ever changes
            from footprint.main.models.config.db_entity_interest import DbEntityInterest
            from footprint.main.models.config.interest import Interest
            db_entity_interest = DbEntityInterest(db_entity=self, config_entity=self._config_entity, interest=Interest.objects.get(key=Keys.INTEREST_OWNER))
            db_entity_interest.save()
            self._config_entity = None

    @property
    def feature_behavior(self):
        if self._feature_behavior:
            return self._feature_behavior
        if not self.id:
            return None
        feature_behaviors = self.featurebehavior_set.all()
        if len(feature_behaviors) > 1:
            raise Exception("Expected exactly one FeatureBehavior for DbEntity %s, but found %s" % (self, len(feature_behaviors)))
        return feature_behaviors[0] if len(feature_behaviors) == 1 else None

    @feature_behavior.setter
    def feature_behavior(self, value):
        self._feature_behavior = value

    def has_behavior(self, behavior):
        """
            Returns True if feature_behavior.behavior is or has a parent matching the given behavior
            :param behavior: Behavior instance to match on
        """
        if not self.feature_behavior:
            logger.warn("Corrupt DbEntity %s. Has no feature_behavior" % self.full_name)
            return False
        return self.feature_behavior and self.feature_behavior.behavior.has_behavior(behavior)

    def has_behavior_key(self, behavior_key):
        """
            Returns True if feature_behavior.behavior is or has a parent matching the Behavior matching behavior_key
            :param behavior_key: key of Behavior instance to match on
        """
        if not self.feature_behavior:
            logger.warn("Corrupt DbEntity %s. Has no feature_behavior" % self.full_name)
            return False
        return self.feature_behavior.behavior.has_behavior(Behavior.objects.get(key=behavior_key))


    @property
    def subclassed_feature_behavior(self):
        """
            Caches the subclass instance for speed
        """
        if not self.feature_behavior:
            return None
        id = self.feature_behavior.id
        if not DbEntity._subclassed_feature_behavior:
            from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
            DbEntity._subclassed_feature_behavior[id] = FeatureBehavior.objects.get_subclass(id=id)
        return DbEntity._subclassed_feature_behavior[id]
    _subclassed_feature_behavior = {}

    # The object that describes the functionality of the feature data, that being what it is used for.
    # FeatureBehavior is an association of the DbEntity and a Behavior.
    # For now the relationship between FeatureBehavior and Behavior is OneToOne, defined on the FeatureBehavior side
    # For the clone case pass a zeroed out version of the intersection
    def update_or_create_feature_behavior(self, configured_feature_behavior, cloned_intersection=None):
        """
            Used when creating or updating the db_entity for a ConfigEntity.
            This will update or create the the Behavior associated with the FeatureBehavior
            and then update or create the FeatureBehavior associating it to the DbEntity
            and Behavior
        """

        try:
            # This is a oneToOne, so will throw if it doesn't exist
            existing_feature_behavior = self.feature_behavior
        except:
            existing_feature_behavior = None

        logger.debug("For DbEntity %s, update_or_create_feature_behavior. Existing feature behavior: %s, feature behavior: %s" % (self.name, existing_feature_behavior, configured_feature_behavior))

        if not configured_feature_behavior:
            if not self.feature_behavior:
                # Set a sensible default
                from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
                configured_feature_behavior = FeatureBehavior(
                    behavior=Behavior.objects.get(key=BehaviorKey.Fab.ricate('reference'))
                )
            else:
                # If we have one but nothing is passed in return the existing one
                return existing_feature_behavior

        # First find the stored Behavior represented by feature_behavior.behavior
        # If given a persisted instance use that, otherwise resolve by key
        try:
            behavior = configured_feature_behavior.behavior if \
                configured_feature_behavior.behavior.id else \
                Behavior.objects.get(key=configured_feature_behavior.behavior.key)
        except Exception, e:
            raise Exception("Could not find Behavior with key %s. Exception message %s" % (configured_feature_behavior.behavior.key, e.message))

        # Check and see if a FeatureBehavior for the DbEntity is defined and doesn't match that defined
        # in the given feature_behavior. If they don't equate we need to delete the existing
        # feature_behavior. Throw an error if that's disallowed by the DbEntity
        if existing_feature_behavior and existing_feature_behavior.behavior != behavior:
            if self.behavior_locked:
                raise Exception("Attempt to change locked behavior on DbEntity %s from Behavior %s to Behavior %s" %
                                (self.full_name, self.feature_behavior.behavior.name, behavior.name))
            existing_feature_behavior.delete()
            existing_feature_behavior = None

        existing_intersection = None
        if existing_feature_behavior:
            # If we still have a valid existing feature_behavior have it conform to anything about the Behavior
            # configuration that might have changed.
            updated_existing_feature_behavior = existing_feature_behavior
            template_feature_behavior = behavior.feature_behavior_from_behavior_template()
            existing_intersection = existing_feature_behavior.intersection_subclassed
            # If cloning set the id to None
            if existing_intersection and not updated_existing_feature_behavior.id:
                existing_intersection.id = None
            logger.debug("Existing Intersection: %s" % model_dict(existing_intersection, include_primary_key=True))
            # TODO this seems problematic. The existing FeatureBehavior's tags should take precedence over the
            # Behavior's unless the former has no tags
            updated_existing_feature_behavior._tags = template_feature_behavior._tags
        else:
            # Get a new instance from the Behavior
            updated_existing_feature_behavior = behavior.feature_behavior_from_behavior_template()
        updated_existing_feature_behavior.set_defaults()

        # Intersection properties are defined on the Behavior and possibly extended or overridden on the FeatureBehavior
        # Every FeatureBehavior has its own Intersection instance so that we can customize the intersection for
        # the DbEntity. We always remove the is_template property that might have come the Behavior's Intersection
        intersection_dict = remove_keys(
            merge(
                model_dict(updated_existing_feature_behavior.intersection_subclassed),
                model_dict(configured_feature_behavior.intersection_subclassed),
            ),
            ['is_template']
        )
        logger.debug("Intersection after merge %s" % intersection_dict)
        # Get or create the intersection instance based on the subclass of the source(s)
        intersection_class = \
            (configured_feature_behavior and configured_feature_behavior.intersection_subclassed and configured_feature_behavior.intersection_subclassed.__class__) or\
            (updated_existing_feature_behavior and updated_existing_feature_behavior.intersection and updated_existing_feature_behavior.intersection_subclassed.__class__)
        intersection = intersection_class()
        # Update to match the settings
        intersection.__dict__.update(
            intersection_dict
        )
        if intersection.__class__ == Intersection:
            raise Exception("Expected subclass: %s %s %s" % (intersection_dict, configured_feature_behavior.intersection_subclassed, updated_existing_feature_behavior.intersection_subclassed))
        # Now that we've updated everything, set the id if we already had an Intersection
        intersection.id = existing_intersection.id if existing_intersection else None
        intersection.save()

        # Merge the tags from existing and configurations
        tags = unique((list(updated_existing_feature_behavior.tags.all()) if updated_existing_feature_behavior.pk else []) + \
                      updated_existing_feature_behavior._tags + \
                      configured_feature_behavior._tags)
        configured_feature_behavior._tags = tags

        # Update or create and set to the attributes of the passed in instance
        updated_existing_feature_behavior = updated_existing_feature_behavior.__class__.objects.update_or_create(
            behavior=updated_existing_feature_behavior.behavior,
            db_entity=self,
            # Merge defaults for the template with passed in values
            # on both the Behavior and FeatureBehavior
            defaults=merge(
                model_dict(updated_existing_feature_behavior, omit_fields=['behavior', 'db_entity', 'intersection']),
                model_dict(configured_feature_behavior, omit_fields=['behavior', 'db_entity', 'intersection']),
                dict(intersection=intersection) if intersection else dict())
        )[0]
        if not updated_existing_feature_behavior.intersection:
            raise Exception("No Intersection for %s" % self)
        from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
        if FeatureBehavior.objects.filter(intersection=updated_existing_feature_behavior.intersection).count() > 1:
            raise Exception("For some reason the intersection %s:%s is shared by the following FeatureBehaviors %s. This should never happen." %(
                updated_existing_feature_behavior.intersection_subclassed.__class__.__name__,
                updated_existing_feature_behavior.intersection.id,
                map(lambda feature_behavior: feature_behavior.db_entity.key, FeatureBehavior.objects.filter(intersection=updated_existing_feature_behavior.intersection))
            ))
        # Handle associations that can't be saved during the main save
        updated_existing_feature_behavior.update_or_create_associations(configured_feature_behavior)
        # Set without saving
        self.feature_behavior = updated_existing_feature_behavior
        return updated_existing_feature_behavior


    @property
    def full_table_name(self):
        """
            Return the schema in table in the syntax usable by Django model classes '"schema"."table"'
        :return:
        """
        return '"{0}"."{1}"'.format(self.schema, self.table)

    @property
    def full_name(self):
        """
            Returns the name of the DbEntity with the titleized schema to distinguish it
        """
        return "{0} for {1}".format(self.name, titleize(self.schema) if self.schema else 'Global Config')

    def resolve_abstract_feature_class(self):
        """
            Extracts the abstract Feature class from the DbEntity configuration
            :return The abstract class or None if not configured
        """
        abstract_class_path = self.feature_class_configuration.abstract_class_name or None
        return resolve_module_attr(abstract_class_path) if abstract_class_path else None

    @property
    def feature_class(self):
        """
            Resolves the concrete feature class by finding the db_entity owner
        :return:
        """
        return FeatureClassCreator(self.db_entity_owner, self).dynamic_model_class()

    @property
    def geometry_type(self):
        """
            Resolves the GeometryTypeKey of the DbEntity based on its FeatureClass table
        :return:
        """
        # Query by ST_GeometryType and take the first result.
        # We currently expect feature tables to have only one type
        return GeometryTypeKey.postgis_to_geometry_type_key(
                self.feature_class.objects.filter().extra(
                    select=dict(geometry_type='ST_GeometryType(wkb_geometry)')
                )[0].geometry_type)

    @property
    def config_entity(self):
        """
            As we progress toward removing DbEntityInterest from the code, we use this property
            to resolve the onw
        :return:
        """
        if not self.id:
            # We can't have a config_entity via the DbEntityInterest until we've saved
            return self._config_entity
        return self.db_entity_owner

    _config_entity = None
    @config_entity.setter
    def config_entity(self, value):
        """
            Stores the config_entity temporarily. We'll use it to update_or_create the DbEntityInterest
            after saving the DbEntity
        :param value:
        :return:
        """
        self._config_entity = value

    @property
    def db_entity_interest_owner(self):
        """
            Returns the DbEntityInterest of the owning ConfigEntity
        :return:
        """
        for db_entity_interest in self.dbentityinterest_set.all():
            config_entity = db_entity_interest.config_entity.subclassed
            if config_entity.owns_db_entity(self):
                return db_entity_interest
        raise Exception("No DbEntityInterest found of the owning ConfigEntity for DbEntity %s" % self.key)

    @property
    def db_entity_owner(self):
        """
            The ConfigEntity that owns the DbEntity, resolved by iterating through
            the DbEntityIntereset set
        :return:
        """
        for db_entity_interest in self.dbentityinterest_set.all():
            config_entity = db_entity_interest.config_entity.subclassed
            if config_entity.owns_db_entity(self):
                return config_entity
        raise Exception("Can't find owner of DbEntity %s with schema %s among %s" % (
            self,
            self.schema,
            map(lambda db_entity_interest: db_entity_interest.config_entity, self.dbentityinterest_set.all())))

    # TODO replace format with SC token format
    # Pickle the Django QuerySet configuration. The manager used is always the manager of the ad hoc class that represents
    # the DbEntity via its table argument. There might be a way to have a manager not associated with a table, but that isn't
    # yet supported. configuration is an array of queryset items to chain together to form the queryset
    # [
    #   (values, ['name', 'year']),
    #   (annotate, dict(average_rating=dict(Avg='book__rating'))),
    #   (filter, dict(name__like='Bob%')).
    #   (order_by, ['name', 'year'])
    # ]
    # means:
    #  ad_hoc_class.objects.values('name').annotate(average_rating=Avg('book__rating')).order_by('name','year')
    # Every tuple has a command and args. The former represents a function such as values, annotate aggregate, order_by
    # The latter are either a column/alias path, array of such, or a dictionary for kwargs
    # Every kwarg key at the second level is column/alias path and the value is a primitive or dict
    # These innermost dicts represent functions where the key is the function name and the value is a primitive or
    # column/alias path
    # The values snd annotate clause above causes a group_by, which should actually be specified by the same format in group_by
    # so that it can be overridden by alternative an group_by or values
    query = PickledObjectField(null=True)


    @property
    def is_clone(self):
        return self.source_db_entity_key and self.source_db_entity_key != self.key


    # The same format, but only one dict is expected instead of an array
    # If the group_by dict is present, it will be preprended to the query dicts to form the QuerySet definition
    group_by = PickledObjectField(null=True)

    def run_query(self, config_entity, **kwargs):
        """
            Prepends the given or default group_by (if any) and/or optional values to the query, runs the query, and returns results
            TODO Since ordering of query parts makes a big difference, we might have to let kwargs specify positions in the query
        :param kwargs['group_by']: use this group_by or the else self.group_by or else no group_by
        :param kwargs['values']: use this values to force the query to only return certain fields,
        and to return dicts instead of instances. Only pass values if not already defined in the query or group_by field
        :return:
        """

        full_query = self._add_to_query(**kwargs) if len(kwargs.keys()) > 0 else None
        return self.parse_query(config_entity, full_query)

    def _add_to_query(self, **kwargs):
        return kwargs.get('values', []) + kwargs.get('group_by', self.group_by or []) + self.query

    # TODO this is all used only for results and will be replaced by the Sproutcore style stuff in query_parsing
    def parse_query(self, config_entity, query=None):
        """
            Parses the stored QuerySet components of the DbEntity to create an actual QuerySet
            :param query: pass in a query instead of using self.query. Used by run_grouped_query to add the group_by
        :return:
        """
        query = query or self.query
        if not query:
            logger.error("Trying to run query for db_entity %s, which has no query defined or passed in" % self.full_name)
            return {}

        # Use the base table of the Feature class for now. We'll need to use the rel table soon.
        manager = config_entity.db_entity_feature_class(self.key, base_feature_class=True).objects
        if isinstance(query, basestring):
            # String query
            # Join the query with the base tables of the feature classes that match the db_entity_keys listed
            # as named wildcards in the query string They are in the form %(db_entity_key)
            db_entity_keys = re.findall(r'%\((.+?)\)', query)
            formatted_query = query % map_to_dict(
                lambda db_entity_key: [db_entity_key,
                                       config_entity.db_entity_feature_class(db_entity_key, base_feature_class=True)._meta.db_table],
                db_entity_keys)
            cursor = connection.cursor()
            cursor.execute(formatted_query)

            result_value = dictfetchall(cursor)
            #always return results as a list so that multiple rows can be returned
            return result_value
        else:
            # Combine the query parts
            return [accumulate(lambda manager, queryset_command: self.parse_and_exec_queryset_command(manager, queryset_command), manager, query)]

    def parse_and_exec_queryset_command(self, manager, queryset_command):
        """
            A queryset command is a two item tuple of a command and args, the command is e.g. values, annotate, or order_by, and
            args are as described in the DbEntity.query docs--a single column/alias path, array of such or kwargs.
        :param queryset_command:
        :return:
        """
        if len(queryset_command) != 2:
            raise Exception("Expected queryset_command to be a two item tuple, but got %s".format(queryset_command))
        command, arguments = queryset_command
        # Fetch the command from the manager by name and call it with the parsed arguments
        return getattr(manager, command)(*self.parse_queryset_command_arguments(arguments))

    def parse_queryset_command_arguments(self, queryset_command_arguments):
        """
            Handles the argument whether a single item, list, or dict, and returns the parsed item(s) in the same
            form. For dicts, keys are passed through and the values are parsed
        :param queryset_command_arguments:
        :return:
        """
        return map(
            lambda argument: self.parse_queryset_inner_argument(argument),
            queryset_command_arguments)

    def parse_queryset_inner_argument(self, argument):
        """
            The inner arguments of the queryset command are either a simple column/alias path or a dict in the
            case of aggregate functions, e.g. dict(Avg='book__rating') to indicate Avg('book__rating')
        :param argument:
        :return:
        """
        if isinstance(argument, dict):
            return map_dict(lambda key, value: self.resolve_models_class(key)(value), argument)[0]
        return argument

    def resolve_models_class(self, class_name):
        """
            Lookups up classes by string name for aggregate classes like Avg
            This could be extended to support other aggregate classes defined elsewhere
        :param class_name: unpackaged class name like 'Avg' stored in the query definition
        :return: The class
        """
        return getattr(sys.modules['django.db.models'], class_name)

    @property
    def has_db_url(self):
        """
            Indicates whether or not the DbEntity url is configured to point to a postgres database
        :return:
        """
        return self.url and self.url.startswith('postgres://')

    @property
    def has_file_url(self):
        """
            Indicates whether or not the DbEntity url is configured to point to a file location
        :return:
        """
        return self.url and self.url.startswith('file://')

    @property
    def has_temp_file_url(self):
        """
            Searches the url for settings.TEMP_DIR to indicate that the source was an uploaded file or similar temporary thing
        """
        return self.has_file_url and self.url.find(settings.TEMP_DIR) != -1

    @property
    def importable(self):
        """
            Indicates if the DbEntity has the right characteristics for importing feature data.
        """
        return self.has_db_url or self.has_file_url or (self.origin_instance and self.origin_instance.importable)

    @property
    def reimportable(self):
        """
            Used to dissallow reimporting from file. Reimport should only happen from an administrative command,
            and we can't reimport uploaded files
        """
        return self.importable and not self.has_temp_file_url

    @property
    def is_valid(self):
        return self.no_feature_class_configuration or (self.feature_class_configuration and self.feature_class_configuration.is_valid)

    _result_map_cache = {}
    @classmethod
    def _cached_result_map(cls, instance):
        """
            A class-scope cache or result_maps for each DbEntity. ResultMaps never change for a DbEntity
            unless the underlying Feature table changes
        :param id:
        :param result_map:
        :return:
        """
        result = cls._result_map_cache.get(instance.id)
        if not result:
            result = instance.create_result_map(instance.feature_class.objects)
            cls._result_map_cache[instance.id] = result
        return result

    @property
    def result_map(self):
        """
            Creates and caches the ResultMap for the Feature class of this DbEntity
        :return:
        """
        return self._cached_result_map(self)

    def __unicode__(self):
        return self.name
