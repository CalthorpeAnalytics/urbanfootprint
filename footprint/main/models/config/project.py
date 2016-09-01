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

from django.contrib.gis.geos import Polygon, MultiPolygon
from django.db import models
from django.conf import settings

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.config.region import Region
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.utils.utils import get_property_path

__author__ = 'calthorpe_analytics'


class Project(ConfigEntity):
    """
        A Project references a single Region and serves as the parent configuration for one or more Scenarios
    """
    objects = GeoInheritanceManager()

    base_year = models.IntegerField(default=2005)

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.srid = settings.DEFAULT_SRID

    def recalculate_bounds(self):

        primary_geography_feature_classes = [self.db_entity_feature_class(db_entity.key)
                                     for db_entity in self.owned_db_entities() if
                                     get_property_path(db_entity, 'feature_class_configuration.primary_geography')]

        use_for_bounds_feature_classes = [self.db_entity_feature_class(db_entity.key)
                                     for db_entity in self.owned_db_entities() if
                                     get_property_path(db_entity, 'feature_class_configuration.use_for_bounds')]

        authority_feature_classes = use_for_bounds_feature_classes if len(use_for_bounds_feature_classes) > 0 \
            else primary_geography_feature_classes

        extents = []
        for authority_feature_class in authority_feature_classes:
            all_features = authority_feature_class.objects.all()
            if len(all_features) > 0:
                bounds = all_features.extent_polygon()
                extents.append(bounds)
                self.bounds = MultiPolygon(extents)
                # Disable publishers for this simple update
                self._no_post_save_publishing = True
                self.save()
                self._no_post_save_publishing = False
            else:
                pass

    def region(self):
        return self.parent_config_entity

    def save(self, force_insert=False, force_update=False, using=None):
        super(Project, self).save(force_insert, force_update, using)

    @classmethod
    def parent_classes(cls):
        """
            Projects may only have a Region for a parent
        :param cls:
        :return:
        """
        return [Region]

    class Meta(object):
        app_label = 'main'
        permissions = (
            ('view_project', 'View Project'),
            # this would permit the merging of region scoped db_entities from on region to another
            ('merge_project', 'Merge Project'),
        )
