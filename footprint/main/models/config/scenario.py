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
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.project import Project

__author__ = 'calthorpe_analytics'


class Scenario(ConfigEntity):
    """
        ProjectScenario is a temporary name while the old Scenario class exists
        Scenarios configure future conditions relatives to the base conditions of their project
    """
    objects = GeoInheritanceManager()

    year = models.IntegerField(null=False, blank=False)

    def set_parent_config_entity(self):
        self.bounds = self.parent_config_entity.bounds

    def save(self, force_insert=False, force_update=False, using=None):
        self.expect_parent_config_entity()
        super(Scenario, self).save(force_insert, force_update, using)

    @property
    def project(self):
        return Project.objects.get(id=self.parent_config_entity.id)

    @classmethod
    def parent_classes(cls):
        """
            Scenarios may only have Projects as a parent
        :param cls:
        :return:
        """
        return [Project]


    class Meta(object):
        permissions = (
            ('view_scenario', 'View Scenario'),
            # Permission to merge data from another Scenario into this one
            ('merge_scenario', 'Merge Scenario'),
        )
        app_label = 'main'

class BaseScenario(Scenario):
    """
        BaseScenarios represent an editing of primary or CanvasFeature data.
    """
    objects = GeoInheritanceManager()
    class Meta(object):
        permissions = (
            ('view_basescenario', 'View Base Scenario'),
            # Permission to merge data from another Scenario into this one
            ('merge_basescenario', 'Merge Base Scenario'),
        )
        app_label = 'main'

class FutureScenario(Scenario):
    """
        FutureScenarios represent and editing of a BuiltFormFeature table
        that is derived from an UrbanFootprint CanvasFeature table
    """
    objects = GeoInheritanceManager()
    class Meta(object):
        permissions = (
            ('view_futurescenario', 'View Future Scenario'),
            # Permission to merge data from another Scenario into this one
            ('merge_futurescenario', 'Merge Future Scenario'),
        )
        app_label = 'main'
