
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

from django.db import models

from footprint.main.lib.functions import first, map_dict_to_dict
from footprint.main.utils.utils import resolve_module_attr


__author__ = 'calthorpe_analytics'

class DbEntities(models.Model):

    db_entities = models.ManyToManyField('DbEntity', through='DbEntityInterest')
    class Meta:
        abstract = True

    def add_db_entity_interests(self, *db_entity_interests):
        """
            Adds one or more unsaved DbEntityInterests to the instance's collection.
            If the instance has not yet overridden its parents' db_entities by adding at least one DbEntityInterest,
            the parents DbEntityInterests will be adopted and then the db_entities give here will be added
        :return:
        """
        # This check exists to avoid infinite recursion, since db_entities are sometimes added post_config_entity_save handler
        if len(db_entity_interests) > 0:
            # Even though the field name is db_entities, we need to pass the DbEntityInterests
            self._add('db_entities', *db_entity_interests)

    def remove_db_entity_interests(self, *db_entity_interests):
        self._remove('db_entities', *db_entity_interests)

    def feature_class_of_base_class(self, base_feature_class):
        """
            Finds the feature_class of this config_entity that is derived from the given base class
        :param base_feature_class:
        :return:
        """
        db_entities = filter(
            lambda db_entity:
                # Get the configured abstract class
                # The source_db_entity_key is a hack to prevent Result db_entities from being chosen
                issubclass(
                    resolve_module_attr(db_entity.feature_class_configuration.abstract_class_name, object),
                    base_feature_class) and
                not db_entity.source_db_entity_key,
            self.computed_db_entities())
        if len(db_entities) != 1:
            raise Exception(
                "Expected exactly one db_entity matching the base_class {0} but got {1}".format(
                    base_feature_class, db_entities if len(db_entities) > 0 else 'none'))
        return self.db_entity_feature_class(db_entities[0].key)

    def db_entity_feature_class(self, key, abstract_class=False, base_feature_class=False):
        """
            Resolves the Feature class subclass of this config_entity for the given key, or the base class version
            if base_class-True. Note that this is slightly different than asking a DbEntity for its corresponding
            Feature class. A DbEntity will always use its owning ConfigEntity for the config_entity property
            of the Feature class. This method uses self as the ConfigEntity, which is useful when self
            is a lower ConfigEntity in the hierarchy (such as a Scenario) and the Feature class needs
            access to related Feature classes that are also at a low level. This works because a lower ConfigEntity
            has access to DbEntities that the higher one does not, which allows queries between from a higher
            DbEntity to join a lower one.
        :param key: The DbEntity key
        :param abstract_class, Default False, if True returns the abstract base class instead of the subclass
        :param base_feature_class, Default False, if True returns the base class instead of the default rel class
        :return:
        """
        try:
            original_db_entity = self.computed_db_entities().get(key=key)
        except Exception, e:
            raise Exception("The DbEntity key %s could not be found in the computed DbEntities of the ConfigEntity %s, which contains %s" %
                            (key, self.name, ', '.join(map(lambda db_entity: db_entity.key, self.computed_db_entities()))))

        source_db_entity_key = original_db_entity.source_db_entity_key if original_db_entity.source_db_entity_key else key
        db_entity = self.computed_db_entities().get(key=source_db_entity_key)
        # Resolve the source_db_entity_key of the DbEntity or just use key
        from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
        if abstract_class:
            subclass = resolve_module_attr(db_entity.feature_class_configuration.abstract_class_name)
        elif base_feature_class or db_entity.feature_class_configuration.no_table_associations:
            subclass = FeatureClassCreator(self, db_entity).dynamic_model_class(base_only=True)
        else:
            subclass = FeatureClassCreator(self, db_entity).dynamic_model_class()
        if not subclass:
            raise Exception(
                "For config_entity {0} no class associated with db_entity_key {1}{2}. "
                "Register a table in default_db_entities() of the owning config_entity.".
                format(unicode(self), key, ", even after resolving source_db_entity_key to {0}".format(source_db_entity_key)
                if source_db_entity_key != key else ''))
        return subclass

    def clone_db_entities(self):
        """
            If this ConfigEntity has an origin_instance, update or create the former's db_entity by copying the
            latter's, if they are not already present.
        :return:
        """
        if not self.origin_instance:
            raise Exception("Cannot clone a config_entity's db_entities which lacks an origin_instance")
        origin_db_entity_interests = self.origin_instance_subclassed.computed_db_entity_interests

        # Sync the db_entities, instructing the method to clone from the origin
        # TODO figure this out
        #sync_db_entities()

    def has_feature_class(self, db_entity_key):
        try:
            self.db_entity_feature_class(db_entity_key)
            return True
        except Exception:
            return False

    def abstract_class_of_db_entity(self, key):
        """
            Like feature_class_of_db_entity, but returns the base abstract Feature class instead of the subclass
        :param key:
        :return:
        """
        return self.db_entity_feature_class(key, abstract_class=True)


    def db_entity_owner(self, db_entity):
        """
            Returns the ConfigEntity that owns the db_entity, either self or one of its ancestors
        :param db_entity:
        :return:
        """
        return self if self.owns_db_entity(db_entity) else self.parent_config_entity_subclassed.db_entity_owner(
            db_entity)

    def owns_db_entity(self, db_entity):
        return self.schema() == db_entity.schema

    def owned_db_entities(self, **query_kwargs):
        """
            Returns non-adopted DbEntity instances
        """
        return map(
            lambda db_entity_interest: db_entity_interest.db_entity,
            self.owned_db_entity_interests(
                # add a db_entity__ prefix since the kwargs are desiged for a DbEntity, not the DbEntityInterest
                **map_dict_to_dict(lambda key, value: ['db_entity__%s' % key, value], query_kwargs)
            )
        )

    def owned_db_entity_interests(self, **query_kwargs):
        """
            Returns non-adopted DbEntityInterest instances
        """
        return filter(
            lambda db_entity_interest: db_entity_interest.db_entity.schema == self.schema(),
            self.computed_db_entity_interests(**query_kwargs))

    def db_entity_by_key(self, key):
        """
            Gets the DbEntities of the instance with the given key.

        :param key: The key attribute of the DbEntity
        :return:
        """
        return self.computed_db_entities(key=key).get()

    def resolve_db_entity(self, table, schema=None):
        """
            Search for a entity with the given table (and schema).
        :param table: the name of the table
        :param schema: the optional name of the DbEntity's schema.
        :return: a DbEntity instance matching the table and schema belonging to the instance or the first ancestor that has it
        """
        self._get('db_entities', table=table, schema=schema)

    def db_entities_having_behavior(self, behavior, **kwargs):
        """
            Finds all computed DbEntities matching kwargs that have the given Behavior instance
            :param behavior: A Behavior instance
        """
        return filter(lambda db_entity: db_entity.has_behavior(behavior), self.computed_db_entities(**kwargs))

    def db_entities_having_behavior_key(self, behavior_key, **kwargs):
        """
            Finds all computed DbEntities matching kwargs that have the Behavior of the given key
            :param behavior_key: The key of a Behavior instance
        """
        return filter(lambda db_entity: db_entity.is_valid and db_entity.has_behavior_key(behavior_key), self.computed_db_entities(**kwargs).filter(source_db_entity_key__isnull=True))

    @property
    def primary_geography_db_entity(self):
        """
            Looks up the ancestry for the closest primary_geography DbEntity and returns it
        :return:
        """
        primary_geography_db_entity = first(
            lambda db_entity: db_entity.feature_class_configuration and db_entity.feature_class_configuration.primary_geography,
            self.owned_db_entities())
        if primary_geography_db_entity:
            return primary_geography_db_entity
        return self.parent_config_entity_subclassed.primary_geography_db_entity if self.parent_config_entity else None

    @property
    def primary_geography_config_entity(self):
        """
            Looks up the ancestry for the closest primary_geography DbEntity and returns the owning config_entity
        :return:
        """
        primary_geography_db_entity = first(
            lambda db_entity: db_entity.feature_class_configuration and db_entity.feature_class_configuration.primary_geography,
            self.owned_db_entities())
        if primary_geography_db_entity:
            return self
        return self.parent_config_entity_subclassed.primary_geography_config_entity if self.parent_config_entity else None
