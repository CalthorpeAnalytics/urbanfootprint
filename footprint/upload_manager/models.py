
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

import json
import logging

from django.db import models
from django.conf import settings

from footprint.main.models.config.config_entity import ConfigEntity
from footprint.utils.websockets import send_message_to_client

logger = logging.getLogger(__name__)


class UploadTaskMixin(models.Model):
    """
        Fields common to UploadTask and UploadDatasetTask
    """
    class Meta:
        abstract = True

    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    PARTIAL = 'PARTIAL'
    STATUSES = (
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (PARTIAL, 'Partial'),
    )

    status = models.TextField(default=PENDING, choices=STATUSES)
    created_on = models.DateTimeField(auto_now_add=True)
    ended_on = models.DateTimeField(null=True)
    extra = models.TextField(blank=True)  # JSON
    progress = models.FloatField(default=0)

    def __unicode__(self):
        return u'Upload task %s (%s)' % (self.id, self.status)

    def load_extra(self):
        """
            Converts the extra json string to an object
        :return:
        """
        if not isinstance(self.extra, dict):
            try:
                self.extra = json.loads(self.extra) if self.extra else {}
            except (TypeError, ValueError):
                self.extra = {}
        return self

    def send_progress(self):
        """
        Send progress information to frontend via websockets
        """
        self.load_extra()
        if 'X-Progress-ID' not in self.extra:
            raise Exception('UploadTask must have a X-Progress-ID in'
                            ' order to send messages through websockets')
        if self.progress is None:
            raise Exception('UploadTask cannot send_progress if progress'
                            ' is None')

        kwargs = self.send_progress_kwargs()
        logger.debug("UploadHandler: Sending progress: %s" % kwargs)
        send_message_to_client(self.user.id, kwargs)

    def send_error(self):
        """
        Send error information to frontend via websockets
        """
        kwargs = self.send_error_kwargs()
        logger.error("Error UploadHandler: Sending error to client: %s" % kwargs)
        send_message_to_client(self.user.id, kwargs)


class UploadTask(UploadTaskMixin):
    """
        Manages a zipped uploaded file or an argis file being downloaded.
        In the case of uploaded files there are one or more UploadDatasetTasks created
        to handle the one or more datasets within the zip file.
        For ArcGIS downloads just one UploadDatasetTask is created TODO--not tested
    """

    UPLOAD_DATAFILE = 'UPLOAD_DATAFILE'
    DOWNLOAD_ARCGIS_LAYER = 'DOWNLOAD_ARCGIS_LAYER'
    TYPES = (
        (UPLOAD_DATAFILE, 'Upload a datafile'),
        (DOWNLOAD_ARCGIS_LAYER, 'Download an ArcGis Layer'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='upload_tasks')

    # The target config entity for this job. Recorded at upload time,
    # and then referenced when the export is complete.
    config_entity = models.ForeignKey(ConfigEntity, null=True)

    # Designates whether this is an file upload of arcgis download
    type = models.CharField(max_length=32, choices=TYPES)

    # The name of the file being uploaded. Sent back to the client for monitoring progressclient for monitoring progress
    name = models.CharField(max_length=200)

    # The id of the DbEntity that is created after the upload completes.
    # This might or might not be useful to store
    db_entity_id = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        """
            Override to serialize self.extra before saving
        :param args:
        :param kwargs:
        :return:
        """
        if self.extra is not None and not isinstance(self.extra, basestring):
            self.extra = json.dumps(self.extra)

        return super(UploadTask, self).save(*args, **kwargs)

    def send_progress_kwargs(self):
        """
            Progress arguments to send to the client for this datasource
        :return:
        """
        return dict(
            event="uploadTaskDatasourceProgressUpdated",
            id=self.id,
            file_name=self.name,
            progress=self.progress,
            config_entity_id=self.config_entity.id if self.config_entity else None)

    def send_error_kwargs(self):
        """
            Error arguments when we have a datasource and something goes wrong
        :return:
        """
        return dict(
            event="uploadTaskDatasourceError",
            id=self.id,
            file_name=self.name,
            progress=self.progress,
            config_entity_id=self.config_entity.id if self.config_entity else None)


class UploadDatasetTask(UploadTaskMixin):
    """
        Represents an individual dataset within the uploaded file
    """

    # The main UploadTask representing the file.
    upload_task = models.ForeignKey(UploadTask)

    # The dataset's id
    dataset_id = models.IntegerField()

    # The path of the zip file the sql of this dataset
    file_path = models.TextField(blank=True, null=True)

    # The filename of the dataset within the uploaded zip file
    filename = models.CharField(max_length=200)

    # The dataset metadata, as a JSON string
    # Access/modify this field through `metadata` property below
    _metadata = models.TextField(db_column="metadata", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.extra is not None and not isinstance(self.extra, basestring):
            self.extra = json.dumps(self.extra)

        return super(UploadDatasetTask, self).save(*args, **kwargs)

    @property
    def user(self):
        return self.upload_task.user

    @property
    def metadata(self):
        return json.loads(self._metadata)

    @metadata.setter
    def metadata(self, value):
        self._metadata = json.dumps(value)

    def send_progress_kwargs(self):
        """
            Combines the upload_task send_progress_kwargs with our, giving our matching fields priority
        :return:
        """

        # Convert upload_task extra from json back to object
        self.upload_task.load_extra()

        return dict(
            event="uploadTaskDatasetProgressUpdated",
            id=self.id,
            # The client views the upload_task as a file source object
            datasource_id=self.upload_task.id,
            dataset_id=self.dataset_id,
            # The name of the dataset file that was within the zip file
            file_name=self.filename,
            # Our progress is potentially different than upload_task
            progress=self.progress,
        )

    def send_error_kwargs(self):
        """
            The kwargs when we have a Dataset and something errors
        :return:
        """
        return dict(
            event="uploadTaskDatasetError",
            id=self.id,
            # The client views the upload_task as a file source object
            datasource_id=self.upload_task.id,
            dataset_id=self.dataset_id,
            # The name of the dataset file that was within the zip file
            file_name=self.filename,
        )
