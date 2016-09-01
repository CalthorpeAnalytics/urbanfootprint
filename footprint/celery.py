
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
__author__ = 'calthorpe_analytics'

import os

from celery import Celery

app = Celery('footprint',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['footprint.main.publishing.publishing',
                     'footprint.main.publishing.data_export_publishing',
                     'footprint.main.publishing.data_import_publishing',
                     'footprint.main.models.analysis_module',
                     'footprint.tasks'])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
