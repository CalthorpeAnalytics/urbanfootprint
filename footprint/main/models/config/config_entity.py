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


from __builtin__ import classmethod
import logging

from django.contrib.auth.models import Group
from django.contrib.gis.db import models
from django.conf import settings
from footprint.main.lib.functions import flat_map, unique, compact
from footprint.main.mixins.analysis_modules import AnalysisModules
from footprint.main.mixins.categories import Categories
from footprint.main.mixins.cloneable import Cloneable
from footprint.main.mixins.config_entity_related_collection_adoption import ConfigEntityRelatedCollectionAdoption
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.db_entities import DbEntities
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.permissions import Permissions
from footprint.main.mixins.related_collection_adoption import RelatedCollectionAdoption
from footprint.main.mixins.scoped_key import ScopedKey
from footprint.main.mixins.built_form_sets import BuiltFormSets
from footprint.main.mixins.geographic_bounds import GeographicBounds
from footprint.main.mixins.name import Name
from footprint.main.mixins.policy_sets import PolicySets
from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)


class ConfigEntity(
        ConfigEntityRelatedCollectionAdoption,
        RelatedCollectionAdoption,
        GeographicBounds,
        PolicySets,
        BuiltFormSets,
        DbEntities,
        AnalysisModules,
        Name,
        ScopedKey,
        Categories,
        Deletable,
        Cloneable,
        Permissions):
    """
        The base abstract class defining and UrbanFootprint object that is configurable
    """

    objects = GeoInheritanceManager()

    # The user who created the config_entity
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='config_entity_creator')
    # The user who last updated the db_entity
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='config_entity_updater')

    media = models.ManyToManyField('Medium', null=True)

    # Use parent_config_entity_subclassed to get the actual subclass, not a generic config_entity instance
    parent_config_entity = models.ForeignKey('ConfigEntity', null=True, related_name='parent_set')

    # Designates the key prefix for database imports
    import_key = models.CharField(max_length=64, null=True)

    behavior = models.ForeignKey('Behavior', null=True)

    # Tracks post save publishing process for client-created ConfigEntities
    # This would be better handled with statuses, but tracking percent is the only
    # way to reliably track completion in the current multi-process post-save graph
    # The range of values are 0 to 100
    # This must be set explicitly to 0 when beginning. We default to 100 to handle
    # preconfigured ConfigEntities
    # This is the same bomb-proofing as DbEntity upload.
    # When we clone a Scenario we don't want to server it to the API unless all steps of the clone succeed.
    setup_percent_complete = models.IntegerField(default=100)

    @property
    def client(self):
        """
            The client is always the highest region key
        :return:
        """
        ancestors = self.ancestors
        if len(ancestors) > 1:
            # If it is a secondary region or lower
            return ancestors[-2].key
        elif len(ancestors) > 0:
            # If it is a highest region
            return self.key
        else:
            # GlobalConfig
            return None

    @property
    def parent_config_entity_subclassed(self):
        return self.parent_config_entity.subclassed if self.parent_config_entity else None

    @property
    def ancestors(self):
        """
            All config_entity ancestors of this config_entity
        :return:
        """
        parent_config_entity = self.parent_config_entity_subclassed
        return ([parent_config_entity] + parent_config_entity.ancestors) if parent_config_entity else []

    def ascendants(self, until_ancestor=None):
        """
            All config_entity ancestors including this one up to and including  until_ancestor or
            else GlobalConfig
        :param until_ancestor: Optional ancestor to stop on. Defaults to the GlobalConfig
        :return:
        """
        parent_config_entity = self.parent_config_entity_subclassed
        return [self] +\
               ((parent_config_entity.ascendants(until_ancestor) if until_ancestor != parent_config_entity else []) \
                    if parent_config_entity \
                    else [])

    def resolve_common_ancestor(self, config_entity, no_reverse_recurse=False):
        """
            Finds the common ancestor of the two config_entities, which might be one of the config_entities
        :param config_entity: Compared with self to find a common ancestor
        :return:
        """
        subclassed = self.subclassed
        if subclassed == config_entity.subclassed:
            return subclassed
        elif not subclassed.parent_config_entity:
            return None
        else:
            # Run with self.parent_config_entity
            result = self.parent_config_entity_subclassed.resolve_common_ancestor(config_entity, True)
            if no_reverse_recurse or result:
                return result
            # If no common ancestor is found reverse actors. This must resolve in a match
            return config_entity.resolve_common_ancestor(self, True)

    # The optional config_entity whence this instance was cloned.
    @property
    def origin_instance_subclassed(self):
        return self.origin_instance.subclassed if self.origin_instance else None

    db = 'default'

    # Temporary state during post_save to disable recursing on post_save publishers
    _no_post_save_publishing = False

    def donor(self):
        """
            Used by the RelatedCollectionAdoption mixin. The parent_config_entity is the donor to this config_entity
        :return:
        """
        return self.parent_config_entity_subclassed

    def donees(self):
        """
            Used by the RelatedCollectionAdoption mixin. The donees of this config_entity are its children
        :return:
        """
        return self.children()

    # The collections listed here (defined in the various mixins) behave similarly. They are many-to-many collections.
    # When computed_COLLECTION_NAME() is called, the returned values are either
    # 1) if this instance has no items in its own collection, the values of the first ancestor via parent which has
    # items set in its collection of the same name
    # 2) if this instance has added items to its collection via add_COLLECTION_NAME(*items), then the parent's
    #  computed_COLLECTION_NAME() items are first inherited to this instance's collection (references, not clones),
    # and then the items given are added. The end result is if no items exist for the instance, computed_COLLECTION_NAME
    # returns the combined values of the ancestors. If items were added for the instance, computed_COLLECTION_NAME()
    # returns the combined values of the ancestors followed by the instances own unique items. Duplicate items,
    # as identified by the items' pk, are ignored by add_COLLECTION_NAME(*items)

    # This pattern of collection inheritance is common enough that the functionality could be added to the Django model
    # framework by extending certain classes, but I haven't invested the time in doing this. The logic resides in
    # ConfigEntitySets for now
    INHERITABLE_COLLECTIONS = ['db_entities', 'built_form_sets', 'policy_sets']
    # Because DbEntityInterest uses a through class (and others might in the future), this dict should be used to
    # resolve the add and remove functions

    def __unicode__(self):
        return '{name} {id} (key:{key}) (class:{clazz})'.format(name=self.name, id=self.id, key=self.key, clazz=self.__class__.__name__)

    class Meta(object):
        abstract = False # False to allow multi-table-inheritance with many-to-many relationship
        app_label = 'main'

    def children(self):
        """
        Executes a query to return all children of this ConfigEntity. It's up to the caller to call the
        InheritanceManager.subclasses to 'cast' to the classes that they expect
        :return:
        """
        return ConfigEntity.objects.filter(parent_config_entity=self, deleted=False)

    def subclassed_children(self):
        return map(lambda child: child.subclassed, self.children())

    def descendants(self):
        """
            Find all descendants of this ConfigEntity
        :return:
        """
        for child in self.subclassed_children():
            yield child
            for subchild in child.descendants():
                yield subchild

    def descendants_by_type(self, subclass):
        """
            Find all descendants of this ConfigEntity that match the given ConfigEntity subclass
            :param subclass: A ConfigEntity subclass
        """
        return flat_map(lambda child: child.descendants_by_type(subclass) if not isinstance(child, subclass) else [child],
                        self.subclassed_children())

    def deleted_children(self):
        return ConfigEntity.objects.filter(parent_config_entity=self, deleted=True)

    def parent_config_entity_saved(self):
        """
        Called whenever the parent_config_entity's attributes are updated
        :return:
        """
        pass

    def config_keys(self):
        return self.parent_config_entity_subclassed.config_keys() + [self.key] if self.parent_config_entity else [self.key]

    def schema(self):
        """
            The database schema name, created by concatenating this instance's key and its parents with underscores,
            where the top-most region is the first key, followed by sub-regions, project, and finally scenario
        :return: underscore concatenated schema name
        """
        return "__".join(self.config_keys()[1:]) if self.parent_config_entity else self.config_keys()[0]

    @property
    def schema_prefix(self):
        """
            Like schema, but GlobalConfig keys have no prefix. This allows global scoped objects, such
            as UserGroups, to simply be named, for example 'super_admin', rather than 'global__super_admin'
        :return:
        """
        return "__".join(self.config_keys()[1:])

    def expect_parent_config_entity(self):
        if not self.parent_config_entity:
            raise Exception("{0} requires a parent_config_entity of types(s)".format(
                self.__class__.__name__,
                ', '.join(self.__class__.parent_classes())))

    def config_entity_ancestor(self, config_entity_class):
        """
            Resolve the ancestor of this ConfigEntity of the given class
        """

        if isinstance(self, config_entity_class):
            return self
        parent_config_entity = self.parent_config_entity_subclassed
        if parent_config_entity:
            return parent_config_entity.config_entity_ancestor(config_entity_class)
        raise Exception("Reached GlobalConfig without finding ancestor of class %s" % config_entity_class)

    def resolve_db(self):
        # This could be used to configure horizontal databases if needed
        return 'default'

    def user_group_name(self, global_group_name):
        """
            All ConfigEntity's define a default User Group name based on their schema.
            The one special case is GlobalConfig, whose ConfigEntity Group is
            UserGroupKey.ADMIN. It returns None here.
            The name returned is '__'.join([self.schema_prefix, global_group_name]) where global_group_name
            is a global group name, such as UserGroupKey.ADMIN. Normally there
            will just be one group per ConfigEntity with full permissions, but you must
            pass the expected global group name to form the name
        :return:
        """
        return '__'.join(compact([self.schema_prefix, global_group_name])) if \
            self.parent_config_entity else None

    def config_entity_group(self, global_group_name):
        """
            Resolves the ConfigEntity Group name based on the Global Group name. The exception
            is for GlobalConfig, which has no ConfigEntity Group since it is the same thing
            as the Global SuperAdmin. So it returns None
        :param global_group_name:
        :return:
        """
        config_entity_group_name = self.user_group_name(global_group_name)
        return Group.objects.get(name=config_entity_group_name) if config_entity_group_name else None

    def config_entity_groups(self):
        """
            Get ConfigEntity-specific groups of the given ConfigEntity.
        :return: Group objects of the ConfigEntity
        """
        from footprint.client.configuration.fixture import ConfigEntityFixture

        # Each ConfigEntity class has its own groups according to the configuration
        # global groups listed in its configuration
        # Iterate through the configured global groups and create ConfigEntity-specific versions
        client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(self)

        # Map the fixture to its ConfigEntity Group
        # GlobalConfig returns nothing here since the SuperAdmin Group is both its Global Group
        # and ConfigEntity Group
        return compact(map(
            lambda global_group_name: self.config_entity_group(global_group_name),
            client_fixture.default_config_entity_groups()
        ))

    def best_matching_config_entity_group_for_group(self, group):
        """
            For ConfigEntities with multiple groups we need the highest ConfigEntity Group to which the
            given group matches or is superior to
        :param user:
        :return:
        """
        the_group_hierarchy = group.group_hierarchy
        if group.group_hierarchy in self.group_hierarchies.all():
            # if there's a direct match return the group
            return group
        else:
            # Go through the groups from most superior based on shortness of ancestry
            # If the group is in the ConfigEntity group's superiors, return the ConfigEntity group
            for group_hierarchy in sorted(
               self.group_hierarchies.all(),
               key=lambda group_hierarchy: len(group_hierarchy.config_entity.ancestors)):
                if the_group_hierarchy.id in map(lambda g: g.id, group_hierarchy.all_superiors()):
                    return group_hierarchy.group
        raise Exception("No match for group %s among %s" % (
            group.name, ', '.join(
                map(lambda group_hierarchy: group_hierarchy.group.name,
                    self.group_hierarchies.all())
                )
            )
        )

    @property
    def full_name(self):
        """
        Concatenates all ancestor names except for that of the GlobalConfig.
        Thus a full name might be region_name subregion_name project_name scenario_name
        """
        return '%s %s of schema %s' % (self.__class__.__name__, self.name, self.schema())

    @classmethod
    def lineage(cls, discovered=[]):
        """
            Returns the hierarchy of parent classes of this class. Duplicates are ignored. Order is from this class up
            until GlobalConfig
        :param cls:
        :return:
        """
        return unique([cls] + flat_map(lambda parent_class: parent_class.lineage(discovered + cls.parent_classes()),
                                       filter(lambda parent_class: parent_class not in discovered,
                                              cls.parent_classes())))

    @property
    def subclassed(self):
        """
            Resolves the config_entity to its subclass version. This garbage should all be done elegantly by Django,
            maybe in the newest version. Otherwise refactor to generalize
        :return:
        """
        return ConfigEntity._subclassed(self)

    _subclassed_lookup = {}

    @classmethod
    def _subclassed(cls, config_entity):
        """
            Cache subclassed config_entities to compensate for Djangos apparent inability to store these on models with
            ConfigEntity ForeignKeys
        :param id:
        :return:
        """
        id = config_entity.id
        return cls._subclassed_by_id(id)

    @classmethod
    def _subclassed_by_id(cls, id):
        subclassed = cls._subclassed_lookup.get(id, None)
        if not subclassed:
            cls._subclassed_lookup[id] = cls.resolve_scenario(
                ConfigEntity.objects.get_subclass(id=id))
        return cls._subclassed_lookup[id]

    _dynamic_model_cached_lookup = {}

    @property
    def _dynamic_model_class_created(self):
        """
            Returns whether or not the config_entity's dynamic models have been created.
            They only have to happen once unless new models are added
        :return:
        """
        return self.__class__._dynamic_model_cached_lookup.get(self.id, False)

    @_dynamic_model_class_created.setter
    def _dynamic_model_class_created(self, value):
        """
            Set whether or not the dynamic model classes for a config_entity have been created
            This is currently just done in FeatureClassCreator, but we might extend it so
            other sources load dynamic models
        :param value:
        :return:
        """
        self.__class__._dynamic_model_cached_lookup[self.id] = value

    @staticmethod
    def resolve_scenario(config_entity):
        for scenario_type in ['basescenario', 'futurescenario']:
            if hasattr(config_entity, scenario_type):
                return getattr(config_entity, scenario_type)
        return config_entity


class ConfigEntityKey(Keys):
    """
        Keyspace for config entities. These keys have no prefix.
    """
    pass
