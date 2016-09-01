
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

from __future__ import absolute_import

import time

from fabric.decorators import task

__author__ = 'calthorpe_analytics'

import os
from django.conf import settings
from footprint.utils.async_job import Job
from django.utils import timezone
from footprint.celery import app
from boto import ec2

@app.task
def cleanup_export_job(*args, **kwargs):
    jobs_to_clean = Job.objects.filter(type="_export_layer", status="Complete")
    for job in jobs_to_clean:
        if timezone.now() - job.ended_on > settings.DOWNLOAD_FILE_EXPIRY:
            filepath = settings.SENDFILE_ROOT + job.data
            os.remove(filepath)
            job.delete()
        else:
            continue
