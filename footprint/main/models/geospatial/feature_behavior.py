
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
from django.db.models import ManyToManyField

from footprint.main.lib.functions import remove_keys
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.tags import Tags
from footprint.main.models.geospatial.attribute_group import AttributeGroup
from footprint.main.models.geospatial.attribute_group_configuration import AttributeGroupConfiguration
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.geospatial.intersection import Intersection
from footprint.main.models.tag import Tag


__author__ = 'calthorpe_analytics'

class FeatureBehavior(Tags):
    """
        Associated to a single DbEntity OneToOne and associates to a Behavior.
        Behavior defines the function of the DbEntity's features

        FeatureBehavior also has configuration properties that are populated from
        a the behavior.template_feature_behavior and then customized for the DbEntity

        self.db_entity can be used to access the DbEntity
    """

    # FeatureBehavior is a wrapper to Behavior that allows a DbEntity to associate
    # indirectly to a Behavior. The behavior defines a template which is used to create
    # an instance of the FeatureBehavior for use by the DbEntity
    # For behavior.teamplate_feature_behavior instances, the behavior is the owning behavior
    behavior = models.ForeignKey(Behavior, null=False)

    # The AttributeGroups associated with this FeatureBehavior
    # AttributeGroups associate the Behavior to specific attributes of the Feature class
    # For instance, a Behavior concerning demographics might expose an AttributeGroup interface
    # that expects an employment, dwelling_unit, and population attribute. The FeatureBehavior
    attribute_groups = ManyToManyField(AttributeGroup, through=AttributeGroupConfiguration)

    # The DbEntity of the FeatureBehavior. Only null temporarily when being hydrate by Tastypie during a DbEntity save
    db_entity = models.ForeignKey(DbEntity, null=True)

    # Set true for instances that are used as a template by Behavior (see Behavior.template_feature_behavior)
    is_template = models.BooleanField(default=False)
    # Indicates if the features are editable. Normally leave this alone
    # and let that of the Behavior take care of it
    readonly = models.BooleanField(default=False)

    # Adds intersection information specific to the DbEntity. The intersection type is normally specified
    # in the Behavior.intersection dict. So whatever is set here is merged with the dict of the Behavior
    intersection = models.OneToOneField(Intersection, null=True, related_name='feature_behavior')

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

    @intersection_subclassed.setter
    def intersection_subclassed(self, value):
        """
            The API needs to set the intersection via this property
        :param value:
        :return:
        """
        self.intersection = value

    _tags = None
    _attribute_group_configurations = None
    def __init__(self, *args, **kwargs):
        super(FeatureBehavior, self).__init__(*args, **remove_keys(kwargs, ['tags', 'attribute_group_configurations']))
        self._tags = self._tags or []
        self._tags.extend(kwargs.get('tags', []))
        self._attribute_group_configurations = kwargs.get('attribute_group_configurations') or self._attribute_group_configurations or []

    @property
    def computed_readonly(self):
        return self.readonly or self.behavior.readonly

    def set_defaults(self):
        """
            Sets defaults for FeatureBehavior instances created from a Behavior template or when updating
            after a configuration change.
            Override when subclassing FeatureBehavior to set default values
        """

        # Use the Behavior's Intersection template if the FeatureBehavior doesn't have its own
        # We create our own instance from it upon save
        self.intersection = self.intersection_subclassed or self.behavior.intersection_subclassed
        self.readonly = self.readonly or self.behavior.readonly

    def update_or_create_associations(self, feature_behavior):
        if feature_behavior._tags:
            self.tags.clear()
            self.tags.add(*map(
                lambda tag: Tag.objects.update_or_create(tag=tag.tag)[0],
                feature_behavior._tags))
        if feature_behavior._attribute_group_configurations:
            self.attributegroupconfiguration_set.all().delete()
            for attribute_group_configuration in feature_behavior._attribute_group_configurations:
                attribute_group_configuration, created, updated = AttributeGroupConfiguration.objects.update_or_create(
                    attribute_group=attribute_group_configuration.attribute_group,
                    feature_behavior=self,
                    defaults=dict(
                        attribute_mapping=attribute_group_configuration.attribute_mapping,
                        group_permission_configuration=attribute_group_configuration.group_permission_configuration
                    )
                )
                attribute_group_configuration.sync_permissions()


    _no_post_save_publishing = False
    objects = GeoInheritanceManager()
    class Meta(object):
        abstract = False
        app_label = 'main'
