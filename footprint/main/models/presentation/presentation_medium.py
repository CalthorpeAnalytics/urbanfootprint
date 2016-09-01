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

from django.db import models
from model_utils.managers import InheritanceManager
from picklefield import PickledObjectField
from footprint.main.mixins.deletable import Deletable
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.presentation.medium import Medium
from footprint.main.mixins.name import Name
from footprint.main.utils.model_utils import classproperty
from django.conf import settings

__author__ = 'calthorpe_analytics'

class PresentationMedium(Name, Deletable):
    """
        Links media to a PresentationConfig and also links the medium to a db_entity of the presentation_config via
        StyleConfig instances
    """
    objects = InheritanceManager()

    medium = models.ForeignKey(Medium, null=True)
    # The DbEntityInterest of the PresentationMedium.
    # This scopes the PresentationMedium to a certain DbEntity and ConfigEntity
    # If a PresentationMedium is cloned for customization at a certain ConfigEntity scope,
    # the DbEntityInterest is set to that of the same DbEntity and child ConfigEntity
    # When we remove DbEntityInterest in the future this will become DbEntity, which
    # itself will be unique to a ConfigEntity
    db_entity_interest = models.ForeignKey(DbEntityInterest, null=False)

    # The user who created the db_entity
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='presentation_medium_creator')
    # The user who last updated the db_entity
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='presentation_medium_updater')

    @property
    def db_entity(self):
        return self.db_entity_interest.db_entity

    @db_entity.setter
    def db_entity(self, db_entity):
        """
            Used by the API to set the DbEntity. We use this to create a DbEntityInterest if
            it doesn't exist
        :param db_entity:
        :return:
        """
        self.db_entity_interest = DbEntityInterest.objects.get(
            config_entity=db_entity.config_entity,
            db_entity=db_entity
        )

    @property
    def medium_subclassed(self):
        """
            Subclasses the medium instance to get at the LayerStyle instance, if it exists
        :return:
        """
        return Medium.objects.filter(id=self.medium.id).get_subclass() if self.medium else None

    @medium_subclassed.setter
    def medium_subclassed(self, medium):
        self.medium = medium

    # Used to indicate whether the instance is currently visible in the presentation. This is useful for a layers
    # on a map, charts, etc., when some need to be hidden
    visible = models.BooleanField(default=True)
    visible_attributes = PickledObjectField(null=True)

    @property
    def db_entity_key(self):
        """
            Convenience access. This used to be the only access to the DbEntity, so it is legacy now
        :return:
        """
        return self.db_entity_interest.db_entity.key

    @property
    def key(self):
        """
            Conform to Key interface without a real property. Some day we might have a real key
            property if we want to support multiple instances per DbEntity
        :return:
        """
        return self.db_entity_interest.db_entity.key

    @classproperty
    def key_property(self):
        """
            We use db_entity_key as the instance's unique key within the scope of a ConfigEntity
        :return:
        """
        return 'db_entity_interest.db_entity.key'

    # Optional configuration meant for non-stylistic or medium related value. For instance, a result graph might store
    # it's axis labels and axis increments here
    configuration = PickledObjectField(null=True)

    # Optional. When medium is a Template this combines renders the medium.content as a template with medium_context as
    # its context. The rendered_medium can take any form. It might be a dict keyed by DbEntity column names and valued
    # by CSS, for instance
    rendered_medium = PickledObjectField(null=True)

    @property
    def config_entity(self):
        """
            Shortcut to access the ConfigEntity of the DbEntityInterst conforms to the related_collection_adoption interface
        :return:
        """
        return self.db_entity_interest.config_entity.subclassed

    def __unicode__(self):
        return "db_entity_key:{0}, medium: {1}".format(self.db_entity_key, unicode(self.medium))

    def query(self):
        return self.get_data()

    def get_data(self, **kwargs):
        """
            Return the DbEntity data of the PresentationMedium in cases where DbEntities are modeled by a feature class.
            The feature class of the config_entity, db_entity combination will either return all results or return
            the query defined on the db_entity, if there is one. Optionally provide a group_by clause (see DbEntity for
            syntax)
            :param kwargs['group_by'] overrides or provides the DbEntity query with a group by--aggregating values and determining
            what fields are returned. This will make the return data always a list of dicts.
            :param kwargs['values'] overrides or provides the DbEntity query with
        :return:
        """
        return self.db_entity_interest.db_entity.run_query(self.config_entity.subclassed, **kwargs)

    @property
    def owning_presentation(self):
        raise Exception("Override in subclass")

    # Disable presentation on the instance
    _no_post_save_publishing = False

    class Meta(object):
        app_label = 'main'
        verbose_name_plural = 'presentation_media'
