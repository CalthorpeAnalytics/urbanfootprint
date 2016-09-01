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

from footprint.main.managers.config.db_entity_interest_manager import DbEntityInterestManager
from footprint.main.mixins.deletable import Deletable
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.config.interest import Interest
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator


__author__ = 'calthorpe_analytics'

class DbEntityInterest(Deletable):
    """
        TODO remove and use implicit through class
    """
    objects = DbEntityInterestManager()

    # A class name is used to avoid circular dependency
    config_entity = models.ForeignKey('ConfigEntity', null=False)
    db_entity = models.ForeignKey(DbEntity, null=False)
    # TODO not used for anything
    interest = models.ForeignKey(Interest, null=False)
    _no_post_save_publishing = False


    def config_entity_is_db_entity_owner(self):
        """
            Returns true if the config_entity of this db_entity_interest owns the db_entity
        :return:
        """
        return self.config_entity.owns_db_entity(self.db_entity)

    def __unicode__(self):
        return "ConfigEntity:{0}, DbEntity:{1}, Interest:{2}".format(self.config_entity, self.db_entity, self.interest)

    class Meta(object):
        app_label = 'main'
