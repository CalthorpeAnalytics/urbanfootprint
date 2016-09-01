
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
from django.conf import settings
from django.middleware import transaction
import re
from tastypie.models import ApiKey

__author__ = 'calthorpe_analytics'

from django.db import models
import uuid
logger = logging.getLogger(__name__)

class Job(models.Model):
    hashid = models.CharField(max_length=36, unique=True)
    task_id = models.CharField(max_length=36)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='jobs')
    type = models.CharField(max_length=32)
    status = models.TextField(blank=True)  # JSON
    created_on = models.DateTimeField(auto_now_add=True)
    ended_on = models.DateTimeField(null=True)
    data = models.TextField(null=True)

    def __unicode__(self):
        return u'Job %s' % self.hashid

    def save(self, *args, **kwargs):
        if not self.hashid:
            self.hashid = uuid.uuid4()
        super(Job, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_on']
        app_label = 'main'

def start_and_track_task(celery_task, api_key, *args, **kwargs):

    user_id = ApiKey.objects.get(key=api_key).user_id

    job = Job.objects.create(
        type=re.split(r'\.', celery_task.name)[-1],
        status="New",
        user=get_user_model().objects.get(id=user_id)
    )
    job.save()
    try:
        # Make sure no transactions are outstanding
        # This shouldn't be needed once Django is upgraded
        transaction.commit()
    except Exception, e:
        pass

    logger.info("Starting celery task %s with args: %s kwargs %s", celery_task, args, kwargs)
    current_task = celery_task.apply_async(
        args=list((job,) + args),
        kwargs=kwargs,
        soft_time_limit=3600,
        time_limit=3600,
        countdown=1
    )

    job = Job.objects.get(hashid=job.hashid)
    job.task_id = current_task.id
    job.save()

    return job
