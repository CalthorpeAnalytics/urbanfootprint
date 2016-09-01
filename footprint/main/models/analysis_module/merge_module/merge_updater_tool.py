
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

import reversion
from django.contrib.gis.db import models
from django.db import transaction
from django.db.models.signals import post_save

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.utils.subclasses import receiver_subclasses
from footprint.utils.websockets import send_message_to_client

__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)

class MergeUpdaterTool(AnalysisTool):

    db_entity_key = models.CharField(max_length=100, null=True, blank=True)
    target_config_entity = models.ForeignKey('ConfigEntity', null=True, blank=True)

    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
        abstract = False

    def merge_progress(self, proportion, **kwargs):

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


    def update(self, **kwargs):
        logger.info("Executing Merge using {0}".format(self.config_entity))

        self.run_merge_tables(**kwargs)

        logger.info("Done executing Merge")
        logger.info("Executed Merge using {0}".format(self.config_entity))

    def run_merge_tables(self, **kwargs):

        source_config_entity = self.config_entity
        target_config_entity = self.target_config_entity
        print ' source'
        print source_config_entity
        print ' target'
        print target_config_entity

        source_feature_class = source_config_entity.db_entity_feature_class(self.db_entity_key)
        source_db_entity = source_config_entity.db_entity_by_key(self.db_entity_key)
        #resolve the target table by looking at the import table of the source db_entity
        target_db_entity_key = source_db_entity.feature_class_configuration_as_dict.get('import_from_db_entity_key')
        target_feature_class = target_config_entity.db_entity_feature_class(target_db_entity_key)

        #filter the target features by their approval status
        source_features = source_feature_class.objects.filter(approval_status='approved')

        #iterate over the features and merge approved rows into the target table
        for source_feature in source_features:
            with transaction.commit_on_success(), reversion.create_revision():
                target_feature = target_feature_class.objects.get(id=source_feature.id)
                target_feature.__dict__.update(**source_feature.__dict__)
                target_feature.save()
                target_feature.comment = "Merge from ConfigEntity %s" % source_config_entity.key
                # If we have comments defined on the base table
                if hasattr(target_feature, 'comments'):
                    target_feature.comments = target_feature.comment
                reversion.set_user(self.updater)
                reversion.set_comment(target_feature.comment)

                #reset the approval field to null after changes are committed to the target
                source_feature.approval_status = None
                source_feature.save()


# TODO should be handled by based class but isn't
@receiver_subclasses(post_save, MergeUpdaterTool, "on_merge_updater_tool_post_save")
def on_analysis_tool_post_save(sender, **kwargs):
    analysis_tool = kwargs['instance']

    if not analysis_tool._no_post_save_publishing:
        analysis_tool.update()
