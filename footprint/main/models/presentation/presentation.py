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

import logging

from django.db import models
from model_utils.managers import InheritanceManager
from picklefield import PickledObjectField
from footprint.main.lib.functions import flat_map, map_property
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.name import Name
from footprint.main.mixins.related_collection_adoption import RelatedCollectionAdoption
from footprint.main.mixins.scoped_key import ScopedKey
from footprint.main.models.config.config_entity import ConfigEntity
logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class Presentation(Name, ScopedKey, Deletable, RelatedCollectionAdoption):
    """
        Creates a presentation, such as a map, result page, or report specifc to a ConfigEntity.
        The presentation is concerned with the visualization of the properties of the ConfigEntity.
        Presentations are defined at all ConfigEntity scopes. Within a presentation the
        PresentationMedia (i.e. Layers or Results) are inherited from the Presentation of the
        parent ConfigEntity
    """

    # Presentations have sublasses--enable subclass querying
    objects = InheritanceManager()

    # Stores a serialized instance of a Configuration
    configuration = PickledObjectField(null=True)

    config_entity = models.ForeignKey('ConfigEntity', null=False)

    # presentation_media is defined on the subclasses as layers and results to circumvent a django bug

    # This is layers for LayerLibrary and results for ResultLibrary
    presentation_media_alias = None

    @property
    def config_entity_subclassed(self):
        """
            Resolves the config_entity to its subclass version. This garbage should all be done elegantly by Django,
            maybe in the newest version. Otherwise refactor to generalize
        :return:
        """
        return ConfigEntity._subclassed(self.config_entity)

    def donor(self):
        """
            Used by the RelatedCollectionAdoption mixin to identify the donor for our adopting.
            Since presentations adopt presentation_media, we need to find the corresponding
            Presentation of the parent_config_entity
        :return:
        """
        parent_config_entity = self.config_entity.parent_config_entity
        try:
            return parent_config_entity and parent_config_entity.presentation_set.filter(key=self.key).select_subclasses().get()
        except Exception, e:
            raise e

    def donees(self):
        """
            Used by the RelatedCollectionAdoption mixin. The donees of this Presentation are the corresponding
            Presentation of each child ConfigEntity of this presentation's ConfigEntity
        :return:
        """

        # We use filter here since the presence of a Presentation in the child is optional. We expect 0 or 1 for
        # each child
        return flat_map(
            lambda child_config_entity: child_config_entity.presentation_set.filter(key=self.key).select_subclasses(),
            self.config_entity.children())

    @property
    def presentation_media(self):
        """
            Delegates to layers or results
        :return:
        """
        return getattr(self, self.presentation_media_alias)

    def computed_presentation_media(self, **query_kwargs):
        """
            The presentation_media that belong to this instance and those adopted from
            the parent config_entity's PresentationLibrary. The alias is layers for LayerLibrary
            and results for ResultLibrary
        :return:
        """
        return self._computed(self.presentation_media_alias, **query_kwargs).all().select_subclasses()

    def add_presentation_media(self, *presentation_media):
        """
            Adds one or more PresentationMedia to the instance's collection.
            This adopts the donor's PresentationMedia first and then adds.
            The presentation_media can be subclassed (e.g. Layer or Result) or the base class PresentationMedium instances
        :return: The computed results after adding the given items
        """
        logger.debug("For Presentation %s (%s) with presentation_media '%s' donor %s (%s) presentation_media: %s, adding presentation_media: %s" % (
            self.name,
            self.id,
            ', '.join(map_property(self.computed_presentation_media(), 'db_entity_key')),
            self.donor().name if self.donor() else "No Donor",
            self.donor().id if self.donor() else '',
            ', '.join(map_property(self.donor().computed_presentation_media(), 'db_entity_key')) if self.donor() else '',
            ', '.join(map_property(presentation_media, 'db_entity_key')),
        ))
        self._add(self.presentation_media_alias, *presentation_media)
        logger.debug("Presentation %s (%s) now has its own presentation_media: %s" % (
            self.name,
            self.id,
            ', '.join(map_property(self.presentation_media.all(), 'db_entity_key')),
        ))

    def db_entities(self):
        """
            Returns all DbEntities associated to the presentation via PresentationMedia instance. This will always be
            a subset of the config_entity.computed_db_entities(). Since the PresentationMedia's db_entity_key implies
            the DbEntity that is selected among two or more of the same key, only one DbEntity per key is returned,
            the selected or only one
        :return:
        """
        return self.config_entity.computed_db_entities().filter(key__in=
            map(lambda presentation_media: presentation_media.db_entity_key,
                self.presentationmedium_set.exclude(db_entity_key__isnull=True)))

    def __unicode__(self):
        return "{0}, {1}".format(Name.__unicode__(self), ScopedKey.__unicode__(self))

    class Meta(object):
        app_label = 'main'
