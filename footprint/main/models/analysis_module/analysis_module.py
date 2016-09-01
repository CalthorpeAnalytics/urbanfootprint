
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
import sys
import traceback
from copy import deepcopy
from string import capitalize

from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models import DateField
from django.utils.timezone import utc
from picklefield import PickledObjectField

from footprint.celery import app
from footprint.main.lib.functions import remove_keys, merge
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.deletable import Deletable
from footprint.main.mixins.name import Name
from footprint.main.mixins.shared_key import SharedKey
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.utils import resolve_module_attr, full_module_path
from footprint.utils.async_job import Job
from footprint.utils.websockets import send_message_to_client

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class AnalysisModule(SharedKey, Name, Deletable):
    """
        No longer abstract. This is a single concrete class.
    """

    objects = GeoInheritanceManager()
    class Meta(object):
        abstract = False
        app_label = 'main'

    started = DateField(null=True)
    completed = DateField(null=True)
    failed = DateField(null=True)

    # The user who created the db_entity
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='analysis_module_creator')
    # The user who last updated the db_entity
    updater = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='analysis_module_updater')

    config_entity = models.ForeignKey(ConfigEntity, null=False)
    analysis_tools = models.ManyToManyField(AnalysisTool)

    # Describes the partner organization(s) involved in development of the module
    partner_description = models.TextField(null=True)

    # Flag used to temporarily disable running the task on post_save when the instance is updated
    _no_post_save_task_run = False
    _no_post_save_task_run_global = False

    # The AnalysisModuleConfiguration.configuration
    configuration = PickledObjectField(null=True, default=lambda: {})

    def __getattr__(self, attr_name):
        """
            Delegate names to the configuration dict
        """
        if attr_name in self.configuration.keys():
            # Configuration value exists
            return self.configuration[attr_name]
        elif attr_name in AnalysisModuleConfiguration.CONFIGURATION_KEYS:
            # Configuration key valid but value is not defined
            return None
        else:
            raise AttributeError(attr_name)

    @property
    def analysis_module_configuration(self):
        """
            Restores the AnalysisModuleConfiguration that created this AnalysisModule
        """
        return AnalysisModuleConfiguration(merge(self.configuration, dict(name=self.name, description=self.description,
                                                                          key=self.key)))

    # The most recent run of the celery task
    celery_task = None

    _started = False
    def init(self):
        for analysis_tool_configuration in self.analysis_module_configuration.analysis_tools:
            analysis_tool_class = resolve_module_attr(analysis_tool_configuration.get('class_name'))
            analysis_tool_class._no_post_save_publishing = True
            analysis_tool, created, updated = analysis_tool_class.objects.update_or_create(
                config_entity=self.config_entity,
                key=analysis_tool_configuration['key'],
                defaults=remove_keys(analysis_tool_configuration, ['key', 'class_name'])
            )
            analysis_tool.initialize(created)
            analysis_tool_class._no_post_save_publishing = False
            if not analysis_tool in self.analysis_tools.all():
                self.analysis_tools.add(analysis_tool)

    def start(self, **kwargs):
        self._started = True
        config_entity = self.config_entity.subclassed
        logger.info('Starting AnalysisModule %s Started for ConfigEntity %s' % (self.name, config_entity.name))
        job = Job.objects.create(
            type=self.key,
            status="New",
            user=self.updater
        )
        job.save()
        self.started = job.created_on
        self.save()
        # Task will use a new version of the instance so set this one to False
        self._started = False

        self.celery_task = analysis_module_task.apply_async(
            args=[job, self.updater, config_entity.id, self.key, kwargs],
            soft_time_limit=3600,
            time_limit=3600,
            countdown=1
        )

        job = Job.objects.get(hashid=job.hashid)
        job.task_id = self.celery_task.id

    def cancel_and_restart(self):
        pass

    def status(self):
        return self.celery_task.status if self.celery_task else None

    def time_since_completion(self):
        return datetime.utcnow() - self.celery_task.completed if self.celery_task else None

@app.task
def analysis_module_task(job, user, config_entity_id, key, kwargs):

    config_entity = ConfigEntity.objects.get(id=config_entity_id).subclassed
    analysis_module = AnalysisModule.objects.get(config_entity=config_entity, key=key)
    # Set again for new instance
    analysis_module._started = True

    try:
        # TODO progress calls should be moved to each module so the status bar increments on the client
        # logger.info('AnalysisModule %s Started for ConfigEntity %s with kwarg keys' % (analysis_module.name, config_entity.name, ', '.join(kwargs or dict().keys())))
        send_message_to_client(user.id, dict(
            event='postSavePublisherStarted'.format(capitalize(key)),
            job_id=str(job.hashid),
            config_entity_id=config_entity.id,
            ids=[analysis_module.id],
            class_name='AnalysisModule',
            key=analysis_module.key))

        # Call each tool's update method
        for analysis_tool in analysis_module.analysis_tools.all().select_subclasses():
            updated_kwargs = deepcopy(kwargs)
            updated_kwargs.update(dict(analysis_module=analysis_module, user=user, job=job, key=key))
            analysis_tool.update(**updated_kwargs)

        # Call the post save publisher
        from footprint.main.publishing.config_entity_publishing import post_save_config_entity_analysis_module
        post_save_config_entity_analysis_module.send(sender=config_entity.__class__, config_entity=config_entity, analysis_module=analysis_module)

        logger.info('AnalysisModule %s Completed for ConfigEntity %s' % (analysis_module.name, config_entity.name))
        logger.info('Sending message to client postSavePublisherCompleted to user %s for module %s and config entity %s' % \
                     (user.username, analysis_module.name, config_entity.name))
        send_message_to_client(user.id,
                               dict(event='postSavePublisherCompleted',
                                    job_id=str(job.hashid),
                                    config_entity_id=config_entity.id,
                                    ids=[analysis_module.id],
                                    class_name='AnalysisModule',
                                    key=analysis_module.key)
        )
        analysis_module.completed = datetime.utcnow().replace(tzinfo=utc)
        analysis_module.save()
        analysis_module._started = False

    except Exception, e:
        try:
            analysis_module.failed = datetime.utcnow().replace(tzinfo=utc)
            analysis_module.save()
        finally:
            analysis_module._started = False

        exc_type, exc_value, exc_traceback = sys.exc_info()
        readable_exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error(readable_exception)
        send_message_to_client(user.id,
                               dict(event='postSavePublisherFailed',
                                    job_id=str(job.hashid),
                                    config_entity_id=config_entity.id,
                                    ids=[analysis_module.id],
                                    class_name='AnalysisModule',
                                    key=analysis_module.key
                               )
        )
        raise Exception(readable_exception)
    finally:
        job.ended_on = datetime.utcnow().replace(tzinfo=utc)
        job.save()


class AnalysisModuleKey(Keys):
    class Fab(Keys.Fab):
        @classmethod

        def prefix(cls):
            return None

    # Predefined keys for convenience
    SCENARIO_BUILDER = Fab.ricate('core')
    ENVIRONMENTAL_CONSTRAINT = Fab.ricate('environmental_constraint')
    ENVIRONMENTAL_CONSTRAINT_INITIALIZER = Fab.ricate('environmental_constraint_initializer')
    FISCAL = Fab.ricate('fiscal')
    VMT = Fab.ricate('vmt')
    ENERGY = Fab.ricate('energy')
    WATER = Fab.ricate('water')

    PUBLIC_HEALTH = Fab.ricate('public_health')

    AGRICULTURE = Fab.ricate('agriculture')
    AGRICULTURE_ANALYSIS = Fab.ricate('agriculture_analysis')
    MERGE_MODULE = Fab.ricate('merge_module')


class AnalysisModuleConfiguration(object):
    """
        A flexible configuration class for AnalysisModule dynamic subclasses.
        This is roughly parallel to a DbEntity. DbEntity has feature_class_configuration to configure the dynamic class
        and this has configuration.
    """
    def __init__(self, configuration):

        self.abstract_class_name = full_module_path(configuration['abstract_class']) if \
                                configuration.get('abstract_class') else \
                                configuration.get('abstract_class_name', full_module_path(AnalysisModule))
        self.configuration = remove_keys(configuration, ['key', 'name', 'description'])
        self.name = configuration.get('name')
        self.description = configuration.get('description')
        self.partner_description = configuration.get('partner_description')
        self.key = configuration.get('key')
        self.analysis_tools = configuration.get('analysis_tools', [])
        super(AnalysisModuleConfiguration, self).__init__()


    # Describes how to configure the features of the table
    configuration = PickledObjectField(null=True, default=lambda: {})

    # These are the keys allowed in the configuration. They can be changed at any time
    CONFIGURATION_KEYS = [
        'key',
        'name',
        'description',
        'initializer_task_name',
        'task_name',
        'analysis_tools'
        # Class-level attributes.
        'class_attrs',
        # Indicates that the AnalysisModuleConfiguration was generated and not for a pre-configured AnalysisModule
        'generated'
    ]

    def __getattr__(self, attr_name):
        """
            Delegate names to the configuration dict
        """
        if attr_name in self.configuration.keys():
            # Configuration value exists
            return self.configuration[attr_name]
        elif attr_name in self.CONFIGURATION_KEYS:
            # Configuration key valid but value is not defined
            return None
        else:
            raise AttributeError(attr_name)

    class Meta(object):
        abstract = False
        app_label = 'main'

    @classmethod
    def analysis_module_configuration(cls, config_entity, **kwargs):
        if not config_entity:
            return cls.abstract_analysis_module_configuration(**kwargs)

        configuration = merge(
            remove_keys(kwargs, ['class_scope']),
            dict(generated=False))

        return AnalysisModuleConfiguration(configuration)

    @classmethod
    def abstract_analysis_module_configuration(cls, **kwargs):
        """
            Abstract version of the configuration for use when no ConfigEntity is specified
        """

        configuration = merge(
            remove_keys(kwargs, ['class_scope']),
            dict(
                class_attrs={'key': kwargs['key']},
                generated=False))

        return AnalysisModuleConfiguration(configuration)
