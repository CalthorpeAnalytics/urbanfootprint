
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
from django.contrib.auth import get_user_model
from django.db import reset_queries
from django.db.models.signals import post_save
from footprint.main.lib.functions import remove_keys, merge
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.analysis_module.analysis_module import AnalysisModule
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.utils.subclasses import receiver_subclasses

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)


def on_config_entity_post_save_analysis_modules(sender, **kwargs):
    """
        Sync a ConfigEntity's ResultPage presentation
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_save_analysis_module. ConfigEntity: %s" % config_entity.name)
    update_or_create_analysis_modules(config_entity, **kwargs)

    reset_queries()


def update_or_create_analysis_modules(config_entity, **kwargs):
    """
        Creates a results library and Result instances upon saving a config_entity if they do not yet exist.
    :param config_entity
    :return:
    """
    from footprint.client.configuration.fixture import AnalysisModuleFixture
    from footprint.client.configuration import resolve_fixture
    analysis_module_fixture = resolve_fixture(
        "analysis_module",
        "analysis_module",
        AnalysisModuleFixture,
        config_entity.schema(),
        config_entity=config_entity)

    for analysis_module_configuration in analysis_module_fixture.default_analysis_module_configurations():
        # Create the table the first time
        analysis_module, created, updated = AnalysisModule.objects.update_or_create(
            config_entity=config_entity,
            key=analysis_module_configuration.key,
            defaults=dict(
                name=analysis_module_configuration.name,
                description=analysis_module_configuration.description,
                partner_description=analysis_module_configuration.partner_description,
                configuration=remove_keys(analysis_module_configuration.configuration, ['key', 'name', 'description']))
        )

        # Update the updater field to the user calling the module, or default to superadmin
        if not analysis_module.updater:
            analysis_module.updater = kwargs.get('user', get_user_model().objects.get(username=UserGroupKey.SUPERADMIN))
        # For the first run make the creator the updater
        if not analysis_module.creator:
            analysis_module.creator = analysis_module.updater
        # update_or_create will kick off the run for updates.
        # don't let it run here
        previous = analysis_module._no_post_save_task_run
        analysis_module._no_post_save_task_run = True
        analysis_module.save()
        analysis_module._no_post_save_task_run = previous
        analysis_module.init()

def on_feature_post_save_analysis_modules(sender, **kwargs):
    """
        Delegate to the DbEntity post save
    """
    logger.info("Handler: on_feature_post_save_tilestache")
    features = kwargs['instance']
    config_entity = features[0].config_entity
    db_entity_interest = config_entity.computed_db_entity_interests(db_entity__key=features[0].db_entity_key)[0]
    # Pretend that we are a DbEntityInterest calling one of its post-save publishing methods
    # features are a parameter used only by this caller
    on_db_entity_post_save_analysis_modules(
        sender,
        instance=db_entity_interest,
        features=features,
        **remove_keys(kwargs, ['instance'])
    )

def on_db_entity_post_save_analysis_modules(sender, **kwargs):
    """
    Respond to whenever a db entity is added or updated
    kwargs:
        instance is the DbEntityInterest
        user_id is the User performing the save
        features are optionally the feature ids if this is called as the result of saving Feature instances
    :return:
    """
    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    if db_entity_interest.db_entity.source_db_entity_key:
        # No analysis dependent on result DbEntities, so just quit
        return
    behavior = db_entity_interest.db_entity.feature_behavior.behavior
    main_config_entity = db_entity_interest.config_entity
    # Todo children() should be all_scenario_descendents or similar to handle region
    config_entities = [main_config_entity] if isinstance(main_config_entity, Scenario) else [main_config_entity]+list(main_config_entity.children())

    for config_entity in config_entities:
        logger.info("Checking which analysis modules should run for config_entity %s, db_entity %s, behavior %s",
                    config_entity.name, db_entity_interest.db_entity.key, behavior)
        analysis_modules = config_entity.analysis_modules
        for analysis_module in analysis_modules:
            for analysis_tool in analysis_module.analysis_tools.all().select_subclasses():
                # If the DbEntity's Behavior matches or has the tool's Behavior as a parent,
                # it means that the DbEntity Feature save should trigger the tool to update
                # We only use this for the Scenario Builder and Agriculture Builder, although
                # other DbEntity Feature updates could trigger analysis tools to run
                # For example, the Scenario Builder has behavior 'scenario_editor_tool', which
                # is a parent behavior of DbEntity 'scenario_end_state's behavior 'scenario_end_state'
                if analysis_tool.behavior and behavior.has_behavior(analysis_tool.behavior):
                    logger.info("Updating AnalysisTool %s for AnalysisModule %s for ConfigEntity %s" % \
                                (analysis_tool.key, analysis_module.key, config_entity.name))

                    # Note that even though an individual tool matched, we call start on the
                    # AnalysisModule, which runs its tools. We don't have any modules with multiple
                    # tools, so this hack works

                    # Update the updater field first
                    analysis_module.updater = get_user_model().objects.get(id=kwargs['user_id'])
                    analysis_module._no_post_save_task_run = True
                    analysis_module.save()
                    analysis_module._no_post_save_task_run = False

                    # Run the module
                    analysis_module.start(
                        ids=map(lambda feature: feature.id, kwargs['features'])
                    )

def on_config_entity_pre_delete_analysis_modules(sender, **kwargs):
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    AnalysisModule.objects.filter(config_entity=config_entity).delete()
    AnalysisTool.objects.filter(config_entity=config_entity).delete()

@receiver_subclasses(post_save, AnalysisModule, "analysis_module_post_save")
def on_analysis_module_post_save(sender, **kwargs):
    analysis_module = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Post Save for AnalysisModule %s for ConfigEntity %s" % \
                (analysis_module.key, analysis_module.config_entity.name))
    if not kwargs.get('created', None):
        # Automatically start the analysis module on update since the client simply updates the
        # analysis module to force it to run.
        # If already started, don't start again. Saves happen during the task run in order
        # to update the analysis_module timestamps
        # The instance flag is used by post_save_config_entity_publishing to turn it off
        if not analysis_module._started and not analysis_module._no_post_save_task_run \
                and not AnalysisModule._no_post_save_task_run_global:
            analysis_module.start()
