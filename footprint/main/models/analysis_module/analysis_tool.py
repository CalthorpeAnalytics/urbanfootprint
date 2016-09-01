
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
import math

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.shared_key import SharedKey
from footprint.main.models.geospatial.behavior import Behavior
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.subclasses import receiver_subclasses
from footprint.utils.websockets import send_message_to_client

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


class AnalysisTool(SharedKey):
    """
        Base class for Analysis Tools. AnalysisModules have many AnalysisTools
    """

    objects = GeoInheritanceManager()
    config_entity = models.ForeignKey('ConfigEntity', null=False)
    # This behavior determines what DbEntities the tool responds to when the former are created or updated
    behavior = models.ForeignKey(Behavior, null=True)
    # The user who last updated the db_entity
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, default=1, related_name='analysis_tool_updater')
    updated = models.DateTimeField(auto_now=True)

    # todo is this where we create options?

    _no_post_save_publishing = False

    # units that are lost to redevelopment by the end state year
    @staticmethod
    def redev_units(field, feature, base_feature):
        units = math.fabs(getattr(feature, field) - getattr(base_feature, field)) \
            if getattr(feature, field) - getattr(base_feature, field) < 0 \
            else 0

        return float(units)

    # new units built by the final scenario year
    @staticmethod
    def new_units(field, feature, base_feature):
        units = getattr(feature, field) - getattr(base_feature, field) \
                if getattr(feature, field) - getattr(base_feature, field) > 0 \
                else 0
        return float(units)

    RESIDENTIAL_TYPES = ['du_detsf_ll', 'du_detsf_sl', 'du_attsf', 'du_mf']
    COMMERCIAL_TYPES = [
        'retail_services', 'restaurant', 'accommodation', 'other_services', 'office_services', 'education',
        'public_admin', 'medical_services', 'wholesale', 'transport_warehousing', 'construction', 'utilities',
        'manufacturing', 'extraction', 'military', 'agriculture'
    ]

    @property
    def all_types_and_categories(self):
        return self.RESIDENTIAL_TYPES + self.COMMERCIAL_TYPES + ['residential', 'commercial']

    class Meta(object):
        app_label = 'main'
        abstract = False

    def initialize(self, created):
        """
            Optional initializer called after the tool instance is created
        """
        pass

    def update(self, **kwargs):
        """
            Overridden by the subclass to run the tool when a dependency changes
        """
        pass

    @classmethod
    def pre_save(cls, user_id, **kwargs):
        """
            Allows subclasses to perform presave operations during API saves
            of the AnalysisModule
        """
        pass

    @classmethod
    def post_save(cls, user_id, objects, **kwargs):
        """
            Allows subclasses to perform postsave operations during API saves
            of the AnalysisModule
        """
        pass

    @property
    def unique_id(self):
        """
            The client id of this instance, a combination of its id and the ConfigEntity id
        """
        return '%s_%s' % (self.config_entity.id, self.id)

    def report_progress(self, proportion, **kwargs):
        send_message_to_client(kwargs['user'].id, dict(
            event='postSavePublisherProportionCompleted',
            job_id=str(kwargs['job'].hashid),
            config_entity_id=self.config_entity.id,
            ids=[kwargs['analysis_module'].id],
            class_name='AnalysisModule',
            key=kwargs['analysis_module'].key,
            proportion=proportion)
        )
        logger.info("Progress {0}".format(proportion))


@receiver_subclasses(post_save, AnalysisTool, "on_analysis_tool_post_save")
def on_analysis_tool_post_save(sender, **kwargs):
    analysis_tool = kwargs['instance']
    if not analysis_tool._no_post_save_publishing:
        analysis_tool.update()


class AnalysisToolKey(Keys):
    SCENARIO_UPDATER_TOOL = 'scenario_updater_tool'
    ENVIRONMENTAL_CONSTRAINT_UNION_TOOL = 'environmental_constraint_union_tool'
    ENVIRONMENTAL_CONSTRAINT_UPDATER_TOOL = 'environmental_constraint_updater_tool'
    ENERGY_UPDATER_TOOL = 'energy_updater_tool'
    WATER_UPDATER_TOOL = 'water_updater_tool'
    VMT_UPDATER_TOOL = 'vmt_updater_tool'
    FISCAL_UPDATER_TOOL = 'fiscal_updater_tool'
    AGRICULTURE_UPDATER_TOOL = 'agriculture_updater_tool'
    MERGE_UPDATER_TOOL = 'merge_updater_tool'
    PUBLIC_HEALTH_UPDATER_TOOL = 'public_health_updater_tool'
    AGRICULTURE_ANALYSIS_UPDATER_TOOL = 'agriculture_analysis_updater_tool'
