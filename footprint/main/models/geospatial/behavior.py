
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
from django.db import models
from inflection import titleize

from footprint.main.lib.functions import merge, remove_keys, any_true, flat_map, accumulate
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.key import Key
from footprint.main.mixins.name import Name
from footprint.main.mixins.tags import Tags
from footprint.main.models.geospatial.intersection import Intersection, GeographicIntersection
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.model_utils import model_dict
from footprint.main.models.tag import Tag

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class BehaviorKey(Keys):
    """
        A Key class to key Behavior instances
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'behavior'

class Behavior(Name, Key, Tags, Deletable):
    """
        The behavior attribute to a DbEntity via FeatureBehavior. Behaviors describe what functions
        Feature tables perform in the system. The instances form a non-cyclical graph where each instance
        has one or more parents. Behaviors inherit Tags and add their own. They also inherit the FeatureBehavior
        template which is a template FeatureBehavior instance for use as the connector between a DbEntity
        and a Behavior. The template has default values and attributes. It is cloned to create the one
        used to associate the DbEntity to the Behavior. The cloned one can then be given values to create a
        configuration particular to that DbEntity.
    """

    def __init__(self, *args, **kwargs):
        super(Behavior, self).__init__(*args, **remove_keys(kwargs, ['parents', 'tags', 'template_feature_behavior']))
        # Put toManys in the holding tank until save time
        self._parents = kwargs.get('parents', [])
        self._tags = kwargs.get('tags', [])
        # This is saved in the other direction
        self._template_feature_behavior = kwargs.get('template_feature_behavior', None)
        self._intersection = kwargs.get('intersection', None)

    abstract = models.BooleanField(default=False)

    @property
    def unprefixed_key(self):
        return BehaviorKey.Fab.remove(self.key)

    _parents = None
    _tags = None
    _template_feature_behavior = None
    _intersection = None

    def update_or_create_associations(self, behavior):
        # Update/Create template_feature_behavior and set it
        # This is done after the update because the template references back to the Behavior
        self.template_feature_behavior = self.update_or_create_template_feature_behavior(behavior._template_feature_behavior)
        self.name = titleize(BehaviorKey.Fab.remove(self.key))
        self.save()

        # Handle the manys that were embedded in the instance constructor
        # _parents are always configured without the BehaviorKey prefix
        if behavior._parents:
            self.parents.clear()
            self.parents.add(*Behavior.objects.filter(key__in=map(lambda parent: BehaviorKey.Fab.ricate(parent), behavior._parents)))
        if behavior._tags:
            self.tags.clear()
            self.tags.add(*map(lambda tag: Tag.objects.update_or_create(tag=tag.tag)[0], behavior._tags))

        # Add the a default tag that matches the key of the Behavior
        tag_key = BehaviorKey.Fab.remove(self.key)
        if not self.tags.filter(tag=tag_key):
            self.tags.add(Tag.objects.update_or_create(tag=tag_key)[0])

        # Inherit the intersection from the first parent if we don't have one
        # Default to a polygon to polygon GeographicIntersection
        intersection = behavior._intersection or\
                       (self.parents.all()[0].intersection_subclassed if\
                            self.parents.count() == 1 else\
                            GeographicIntersection.polygon_to_polygon)
        if not intersection:
            raise Exception("All behaviors must have a default intersection")
        # Use all attributes to find/create the Intersection instance, including nulls
        # Behaviors can't have specific Intersection properties, as FeatureBehaviors can, so it's safe to
        # share Intersection instances among them. The Intersection of a Behavior is really just the template
        # for that of a FeatureBehavior
        self.intersection = intersection.__class__.objects.get_or_create(**model_dict(intersection))[0]
        self.save()

    # The type of intersection that the the feature associated geography tables use to intersect primary features
    # This is left null for primary features
    intersection = models.ForeignKey(Intersection, null=True)

    @property
    def intersection_subclassed(self):
        """
            Return the subclassed version of the Intersection. If not yet persisted the intersection instance
            will be a subclass or null
        :return:
        """
        return Intersection.objects.get_subclass(id=self.intersection.id) if\
            (self.intersection and self.intersection.id) else\
            self.intersection

    # An instance has zero or more parents. symmetrical says don't add the child to the parents' parents
    parents = models.ManyToManyField('self', symmetrical=False)
    # The FeatureBehavior that is the template for associating the DbEntity to the Behavior. The template instance
    # is cloned and then filled out according to the DbEntity's Feature characteristics. For instance, certain
    # functions might need to be assigned to specific attributes/columns of the Feature class/table that differ
    # from Feature class/table to Feature class/table
    # Only the bootstrap Behavior 'template_feature_behavior' should have null here
    template_feature_behavior = models.ForeignKey('FeatureBehavior', null=True, related_name='owning_behavior')
    # Indicates if the DbEntity features are readonly, at least in the context of this behavior
    readonly = models.BooleanField(default=False)

    @property
    def subclassed_template_feature_behavior(self):
        """
            Since it's possible to have a subclassed FeatureBehavior as the template instance,
            this makes sure we get the subclass version and not the base version. It also caches
            the lookup for efficiency
        """
        id = self.template_feature_behavior.id
        if not id in Behavior._subclassed_template_feature_behavior:
            from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
            Behavior._subclassed_template_feature_behavior[id] = FeatureBehavior.objects.get_subclass(id=id)
        return Behavior._subclassed_template_feature_behavior[id]
    # Caches the TemplateFeatureBehavior subclassed instance version to avoid slowness
    _subclassed_template_feature_behavior = {}

    def update_or_create_template_feature_behavior(self, template_feature_behavior):
        """
            Saves an unsaved template FeatureBehavior, marking it as a template
        """

        if template_feature_behavior and template_feature_behavior.id:
            return template_feature_behavior
        from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
        from footprint.main.models.geospatial.db_entity import DbEntity
        return (template_feature_behavior.__class__ if template_feature_behavior else FeatureBehavior).objects.update_or_create(
            behavior=self,
            db_entity=DbEntity.objects.get(key='template_feature_behavior'),  # Special DbEntity
            is_template=True,
            defaults=model_dict(template_feature_behavior) if template_feature_behavior else {}
        )[0]

    def feature_behavior_from_behavior_template(self):
        """
            The method to create a FeatureBehavior from the template_feature_behavior.
            This might be a subclass instance of FeatureBehavior and/or preconfigured values
            Override FeatureBehavior.set_defaults to set preconfigured values

        """
        template_feature_behavior = self.subclassed_template_feature_behavior
        # Clone it, making a new intersection instance by removing the id
        # If the FeatureBehavior has no Intersection get it from the Behavior
        # Some behaviors, like background_imagery and result also have no Intersection
        intersection = template_feature_behavior.intersection_subclassed or self.intersection_subclassed
        if not intersection:
            raise Exception("No intersection for the template FeatureBehavior resolved")
        intersection.id = 0
        logger.debug("Intersection from template is %s of subclass %s" % (model_dict(intersection, include_primary_key=True) if intersection else 'None', intersection.__class__ if intersection else 'None'))
        feature_behavior = template_feature_behavior.__class__(
            **merge(model_dict(template_feature_behavior),
                    dict(behavior=self, is_template=False, intersection=intersection))
        )
        # Set any defaults defined by the base or subclass
        feature_behavior.set_defaults()
        return feature_behavior

    @property
    def computed_tags(self):
        return self._computed_tags()

    def _computed_tags(self, seen=[]):
        """
            Tags are used for categorizing, especially visually tags + the tags of the parents (recursive).
            tags always at least contain the Behavior's key as a Tag,
            so the user doesn't have to explicitly list tags that match the key.
            It might be that we never need tags that don't match a key
        """

        # Combine querysets using the | operator
        return accumulate(
            lambda previous, next: previous | next,
            self.tags.all().distinct(),
            map(lambda parent: parent._computed_tags(seen+list(self.parents.all())), filter(lambda parent: parent not in seen, self.parents.all().distinct()))).distinct()

    def computed_behaviors(self, level=0):
        """
            Returns the Behavior and all of its ancestors
        """
        return [self] + flat_map(lambda parent: parent.computed_behaviors(), self.parents.all())

    def dump_behaviors(self, level=0, seen=[]):
        """
            Pretty print the behavior and its ancestors using indentation
        """
        return '\n'.join(['%s>%s' % ('--'*level, self.unprefixed_key)] + map(
            lambda parent: parent.dump_behaviors(level+1, seen+[self]),
            filter(lambda behavior: behavior not in seen, self.parents.all())))

    def has_behavior(self, behavior, seen=[]):
        return self==behavior or any_true(lambda parent_behavior: parent_behavior.has_behavior(behavior, seen+[self]),
                                          filter(lambda behavior: behavior not in seen, self.parents.all()))

    def __unicode__(self):
        return '{0} (Parents: {1})'.format(self.key, ', '.join(map(lambda parent: parent.key, self.parents.all() if self.pk else self._parents)))

    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

def update_or_create_behavior(behavior):
    """
        Update or create a behavior based on the given behavior
    """

    updated_behavior = Behavior.objects.update_or_create(
        key=behavior.key,
        defaults=model_dict(behavior, omit_fields=['key', 'template_feature_behavior'])
    )[0]
    updated_behavior.update_or_create_associations(behavior)
    return behavior
