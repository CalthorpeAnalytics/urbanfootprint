
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
from time import time

from django.core.files.uploadhandler import FileUploadHandler

from footprint.upload_manager.models import UploadTask


logger = logging.getLogger(__name__)


def create_task(user, file_name, config_entity=None, extra_data_dict=None):
    """
    Creates an UploadTask for the user and file. Optionally accepts a config_entity,
    and extra_data_dict, which represents a dictionary to be stored in the extra field.
    """

    upload_task = UploadTask.objects.create(
        type=UploadTask.UPLOAD_DATAFILE,
        user=user,
        name=file_name,
        config_entity=config_entity
    )

    if extra_data_dict:
        upload_task = upload_task.load_extra()
        upload_task.extra.update(extra_data_dict)
        upload_task.save()

    return upload_task


class UploadProgressTaskHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, max_progress, upload_task=None):
        self.max_progress = max_progress
        self.upload_task = upload_task
        self.last_progress_sent = 0

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.file_size = content_length

    def receive_data_chunk(self, raw_data, start):
        if self.upload_task:

            self.upload_task.progress += (float(len(raw_data)) / self.file_size) * self.max_progress

            # only log the progress and send progress updates
            # to the browser at most every 2 seconds
            _now = time()
            if _now - self.last_progress_sent > 2:

                # `load_extra()` sets the `extra` field to a dictionary,
                # so call it here before accessing its key value pairs
                self.upload_task.load_extra()

                logger.debug("UploadHandler: Received chunk for file %s. Total progress: %s" %
                             (self.upload_task.extra['X-Progress-ID'], self.upload_task.progress))
                self.upload_task.send_progress()
                self.last_progress_sent = _now

            # Saving restores the `extra` field to JSON - so call `save()`
            # here once we're done accessing key-value pairs from `extra`
            self.upload_task.save()

        else:
            logger.warn("UploadHandler: Received chunk for file, but UploadProgressTaskHandler "
                        "instance does not have an upload_task attribute assigned.")

        return raw_data

    def file_complete(self, file_size):
        if self.upload_task:

            self.upload_task.progress = self.max_progress

            # `load_extra()` sets the `extra` field to a dictionary,
            # so call it here before accessing its key value pairs
            self.upload_task.load_extra()

            logger.debug("UploadHandler: File complete for file %s. Total progress: %s" %
                         (self.upload_task.extra['X-Progress-ID'], self.upload_task.progress))
            self.upload_task.send_progress()

            # Saving restores the `extra` field to JSON - so call `save()`
            # here once we're done accessing key-value pairs from `extra`
            self.upload_task.save()

        else:
            logger.warn("UploadHandler: File complete for file, but UploadProgressTaskHandler "
                        "instance does not have an upload_task attribute assigned.")
