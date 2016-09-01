
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
import time

from celery import Task
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from inflection import camelize, humanize
from tastypie.models import ApiKey
from django.conf import settings

from footprint.celery import app
from footprint.main.lib.functions import remove_keys, merge
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.utils.utils import resolve_module_attr
from footprint.utils.async_job import start_and_track_task
from footprint.utils.websockets import send_message_to_client

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

def post_save_publishing(signal_path, config_entity, user, **kwargs):
    """
        The initial entry point and recursive entry point for all post save publishing methods
        :signal_path - the full module path of the signal that called this
        :param kwargs:
            signal_proportion_lookup - A dictionary of signal names to the proportion complete of the overall post save.
            The signal matching signal_path will be sought in the dictionary
            config_entity - The scope of whatever being post-saved, whether a config_entity or something within it
            dependent_signal_paths - Full module signal paths called in sequentially by this publisher
            crud_type - CrudKey.CREATE|CLONE|UPDATE|SYNC|DELETE
            instance_class - Optional. Overrides the class of the instance for use in communicating with the client.
            This is used when the client only cares about a base class, such as Feature or to for DbEntityInterest
            to be a DbEntity
            client_instance_path - Optional. Property path to resolve the instance to another instance for the client.
             (this is only used to convert DbEntityInterest to DbEntity)
    """
    api_key = ApiKey.objects.get(user=user).key

    # Gather instance ids, class, and optional instance keys
    bundle = InstanceBundle(**merge(kwargs, dict(user_id=user.id)))

    # Pass the arguments to the task and run via celery. Note that kwargs is being treated
    # as a dict here and passed along
    logger.info("Django post save: %s" % unicode(bundle))

    # Send the start event to the client if we aren't recursing.
    if not kwargs.get('recurse', False):
        event = 'postSavePublisherStarted'
        logger.info("Sending start message %s to user %s with %s" % (event, user.username, unicode(bundle)))

        send_message_to_client(
            user.id,
            dict(
                event=event,
                config_entity_id=config_entity and config_entity.id,
                config_entity_class_name=config_entity and config_entity.__class__.__name__,
                class_name=bundle.class_name_for_client,
                # Always send 0 for initial
                proportion=0,
                ids=bundle.client_instance_ids,
                keys=bundle.keys,
                class_key=bundle.class_key
            )
        )

    # Start Celery
    logger.info("Starting post save publishing with signal path %s" % signal_path)
    job = start_and_track_task(_post_save_publishing,
                               api_key,
                               config_entity,
                               user,
                               **merge(
                                     remove_keys(kwargs, ['instance']),
                                     dict(
                                         # If we are recursing (already in a celery worker, don't start a new celery task
                                         # When we get dependency order figured out, we can do this, but there's probably
                                         # a better way via the Task object or something
                                         current_job=kwargs.get('job', None),
                                         signal_path=signal_path,
                                         crud_type=kwargs.get('crud_type'),
                                         bundle=bundle
                               )))

    return HttpResponse(job.hashid)


def send_fail_message(config_entity, bundle, job, publisher_name, signal_proportion_lookup_name, user):
    job.status = "Failed"
    exc_type, exc_value, exc_traceback = sys.exc_info()
    readable_exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
    job.data = readable_exception
    event = 'postSavePublisherFailed'
    logger.error("Sending Failed message %s for signal %s to user %s with %s readable_exception %s" % \
        (event, signal_proportion_lookup_name, user.username, unicode(bundle), readable_exception))

    send_message_to_client(user.id, dict(
        event=event,
        config_entity_id=config_entity and config_entity.id,
        config_entity_class_name=config_entity and config_entity.__class__.__name__,
        # Send the key since the id of new instances might be meaningless to the client
        # If it hasn't updated the record's id yet
        class_name=bundle.class_name_for_client,
        ids=bundle.client_instance_ids,
        keys=bundle.keys,
        # Used for Features and other things that have a class scope key
        class_key=bundle.class_key,
        publisher_name=publisher_name,
        # The client can display a capitalized version of this to describe the progress
        progress_description=humanize(signal_proportion_lookup_name),
        trace=readable_exception)
    )
    return readable_exception


class PostSaveTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Make sure no transactions are outstanding
        # This shouldn't be needed once Django is upgraded
        job, config_entity, user = args
        bundle = kwargs['bundle']
        # Try to load the instances
        instances = bundle.instances
        logger.error("Handling failure for %s %s instances with error %s and traceback %s",
                     len(instances), 'created' if kwargs.get('created') else 'updated', exc, einfo)

        for instance in instances:
            try:
                logger.error("Handling failure for %s instance %s" % ('created' if kwargs.get('created') else 'updated', instance))
            except:
                logger.error("Handling failure for %s instance with id %s" % ('created' if kwargs.get('created') else 'updated', instance.id))
            # Let the instances delete themselves on a post save creation error
            if kwargs.get('created'):
                instance.handle_post_save_creation_error()

        job.ended_on = timezone.now()
        job.save()

        publishing_info = get_publishing_info(**kwargs)
        # Tell the client about the error
        readable_exception = send_fail_message(
            config_entity,
            bundle,
            job,
            publishing_info['publisher_name'],
            publishing_info['signal_proportion_lookup_name'],
            user)
        raise Exception(''.join(readable_exception))

    def on_success(self, retval, task_id, args, kwargs):
        job, config_entity, user = args
        job.ended_on = timezone.now()
        job.save()


def get_publishing_info(**kwargs):
    signal_path = kwargs['signal_path']
    signal_proportion_lookup_name = signal_path.split('.')[-1]
    publisher_name = unicode(
        camelize(
            signal_proportion_lookup_name,
            False
        )
    )
    # Lookup the dependent signal paths of the signal. We'll use these to recurse
    dependent_signal_paths = kwargs['dependent_signal_paths'](signal_path)
    proportion = kwargs.get('signal_proportion_lookup', {}).get(signal_proportion_lookup_name, 0)
    return dict(
        publisher_name=publisher_name,
        signal_path=signal_path,
        signal_proportion_lookup_name=signal_proportion_lookup_name,
        proportion=proportion,
        dependent_signal_paths=dependent_signal_paths)


@app.task(base=PostSaveTask)
def _post_save_publishing(job, config_entity, user, **kwargs):
    """
        Runs all configured publishers via the Django signals they depend upon.
        This is done in Celery in order to support long running tasks launched from a client.
        Peer tasks are run in parallel. Dependent tasks are called after the tasks they depend on complete

    :param hash_id: Job hash id
    :param config_entity:
    :param user: The current user or None if no user is in scope
    :return:
    """

    if not settings.FOOTPRINT_INIT:
        # There is a poorly-understood issue related to uploading .gdb
        # files with mutliple layers (possibly caused by some race
        # condition) that, without sleeping here, causes the celery
        # task to run without an `instance` (the object that triggered
        # post save processing). Testing had shown 10 seconds to be the
        # shortest amount of time to wait here that permits the post-save
        # processing to complete successfully.
        time.sleep(10)

    bundle = kwargs['bundle']
    # Make sure all the Feature subclasses that the celery worker might need are created
    if config_entity:
        config_entity._feature_classes_created = False
        FeatureClassCreator(config_entity)

    # Get the publisher_name, proportion, and signal_path
    publishing_info = get_publishing_info(**kwargs)

    try:
        # Make sure no transactions are outstanding
        # This shoudln't be needed once Django is upgraded
        transaction.commit()
    except Exception, e:
        pass

    # Updated the kwargs to include the resolved instance. This will be sent when we recurse on post_save_publishing
    # Also use first=False to indicate recursion so we don't resend the start signal to the client
    updated_kwargs = merge(
        remove_keys(kwargs, ['signal_path', 'current_job', 'bundle']),
        dict(instance=bundle.instances, user_id=bundle.user_id, recurse=True, current_job=job))
    logger.warn("kwargs %s" % updated_kwargs)

    logger.info("Running handlers for signal {signal_path} for {bundle}".format(
        config_entity=config_entity,
        username=user.username,
        signal_path=publishing_info['signal_path'],
        bundle=unicode(bundle)))

    # Send the signal. The listening publishers will run in sequence
    # We always send the signal in the context of the underlying config_entity class if one exists
    resolve_module_attr(publishing_info['signal_path']).send(
        sender=config_entity.__class__ if config_entity else bundle.clazz, **updated_kwargs
    )
    try:
        # Make sure no transactions are outstanding
        # This shouldn't be needed once Django is upgraded
        transaction.commit()
    except Exception, e:
        pass

    event = 'postSavePublisherProportionCompleted'
    logger.info("Sending message %s for signal complete %s to user %s with %s, and proportion %s" %
                 (event, publishing_info['signal_proportion_lookup_name'], user.username, unicode(bundle), publishing_info['proportion']))

    if kwargs.get('update_setup_percent_complete'):
        for instance in bundle.client_instances:
            # This creates an update statement to increment to the setup_percent_complete field
            # by the given proportion
            logger.info("Instance percent before %s" % instance.setup_percent_complete)
            instance.setup_percent_complete = F('setup_percent_complete') + 100*publishing_info['proportion']
            instance.save()
            logger.info("Instance percent after %s" % instance.setup_percent_complete)

    send_message_to_client(user.id, dict(
        event=event,
        job_id=str(job.hashid),
        config_entity_id=config_entity and config_entity.id,
        config_entity_class_name=config_entity and config_entity.__class__.__name__,
        # Send the key since the id of new instances might be meaningless to the client
        # If it hasn't updated the record's id yet
        publisher_name=publishing_info['publisher_name'],
        class_name=bundle.class_name_for_client,
        ids=bundle.client_instance_ids,
        keys=bundle.keys,
        # Used for Features and other things that have a class scope key
        class_key=bundle.class_key,
        # Send the proportion of work that completing this signal signifies--0 to 1
        proportion=publishing_info['proportion'],
        # The client can display a this to describe the progress
        progress_description=humanize(publishing_info['signal_path']),
    ))

    # Find all dependent signals of this one and run each in parallel
    for dependent_signal_path in publishing_info['dependent_signal_paths']:
        # Recurse
        post_save_publishing(
            dependent_signal_path,
            config_entity,
            user,
            **updated_kwargs
        )
    job.status = 'Complete'
