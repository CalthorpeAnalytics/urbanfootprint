
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
import shlex
import shutil
import sys
import traceback

import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.utils import timezone
from sendfile import sendfile
from tastypie.models import ApiKey

from footprint.celery import app
from footprint.main.models import LayerSelection, Result
from footprint.main.models.keys.keys import Keys
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.utils.ogr import OGRETL
from footprint.main.utils.utils import timestamp, database_connection_string_for_ogr
from footprint.main.utils.zip_geodatabase import zip_file_gdb
from footprint.utils.async_job import Job
from footprint.utils.async_job import start_and_track_task
from footprint.utils.utils import full_module_path
from footprint.utils.websockets import send_message_to_client

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = {
    "geojson": '''"GeoJSON"''',
    "gdb": '''"FileGDB"''',
    "shapefile": '''"ESRI Shapefile"'''
}

def export_layer(request, layer_id, api_key):
    job = start_and_track_task(_export_layer, api_key, layer_id)
    return HttpResponse(job.hashid)

def class_name_for_client(clazz):
    """
        Returns just the final segment of the class name--module segments are omitted
    """
    return full_module_path(clazz).split('.')[-1]


def export_result_table(request, result_id, api_key):
    result = Result.objects.get(id=result_id)
    result_table_name = str(Result.objects.get(id=result_id).db_entity_interest.db_entity.full_table_name)
    result_query = 'select * from {0}'.format(result_table_name)
    logger.debug("Exporting results for db entity key: %s" % (result.db_entity_key))
    logger.debug("Exporting results using query: %s" % (result_query))
    job = start_and_track_task(_export_query_results, api_key, class_name_for_client(Result), result.id, result.db_entity_key, result_query)
    return HttpResponse(job.hashid)


def export_query_results(request, layer_selection_unique_id, api_key):
    layer_selection = LayerSelection.from_unique_id(layer_selection_unique_id)
    query = layer_selection.query_sql
    logger.debug("Exporting query results for layer_selection: %s, query: %s" % (layer_selection.unique_id, query))
    job = start_and_track_task(_export_query_results, api_key, class_name_for_client(LayerSelection), layer_selection.unique_id, layer_selection.layer.db_entity_key, query)
    return HttpResponse(job.hashid)

def export_query_summary(request, layer_selection_unique_id, api_key):
    layer_selection = LayerSelection.from_unique_id(layer_selection_unique_id)
    query = layer_selection.summary_query_sql
    logger.debug("Exporting summary query results for layer_selection: %s, summary query: %s" % (layer_selection.unique_id, query))
    job = start_and_track_task(_export_query_results, api_key, class_name_for_client(LayerSelection), layer_selection.unique_id, '%s_Summary' % layer_selection.layer.db_entity_key, query)
    return HttpResponse(job.hashid)


@app.task
def _export_layer(job, layer_id):

    try:
        layer = Layer.objects.get(id=layer_id)
        job.status = "Exporting"
        job.save()

        db_entity = layer.db_entity_interest.db_entity
        geometry_type = layer.medium_subclassed.geometry_type
        export_file, filename = export_db_entity_to_file(db_entity, geometry_type)

        job.status = "Zipping"
        job.save()

        zip_file_gdb(export_file)
        shutil.rmtree(export_file)

        job.data = '/' + filename + ".zip"
        job.save()

        send_message_to_client(job.user.id, dict(event='layerExportCompleted',
                                                 layer_id=layer_id,
                                                 job_id=str(job.hashid)))

        job.status = 'Complete'

    except Exception, e:
        job.status = "Failed"

        exc_type, exc_value, exc_traceback = sys.exc_info()
        readable_exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
        job.data = readable_exception
        job.save()

        send_message_to_client(job.user.id, dict(event=job.type + " failed", trace=readable_exception))

    job.ended_on = timezone.now()
    job.save()

def get_export_result(request, api_key, hash_id):
    job = Job.objects.get(hashid=hash_id)
    try:
        user_id = ApiKey.objects.get(key=api_key).user_id
        assert user_id == job.user.id
    except:
        return HttpResponseForbidden("This user did not request that file!")

    if job.status != "Complete":
        return HttpResponseNotFound("Export is not complete")
    filepath = settings.SENDFILE_ROOT + job.data
    return sendfile(request, filepath, attachment=True)


def export_db_entity_to_file(db_entity, geometry_type, export_file=None, export_format="gdb", fields=None):

    if fields:
        field_string = ''
        for field in fields:
            field_string += field + ', '
        field_string = field_string[:-2]
    else:
        field_string = " * "

    table = "{schema}.{table}".format(**db_entity.__dict__)

    select_statement = "select * from (select {fields} from {table}) as {feature_class};".format(
        fields=field_string, table=table, feature_class=db_entity.key)
    filename = construct_export_filename(db_entity, export_format)

    if not export_file:
        export_file = "{SENDFILE_ROOT}/{filename}".format(
            SENDFILE_ROOT=settings.SENDFILE_ROOT,
            filename=filename)

    print "attempting to create" + export_file

    export_command = generate_ogr_command(export_format, geometry_type, select_statement, export_file)
    export_command_args = shlex.split(export_command)
    print export_command, export_command_args
    # shlex ("simple lexical analysis") splits the command string into its arguments before it runs in subprocess
    ogr_result = os.system(export_command) #, shell=True)
    # print result
    if ogr_result:
        raise Exception(ogr_result)
    logger.info("file ready for download")

    return export_file, filename


def generate_ogr_command(export_format, geometry_type, select_statement, export_file):
    logger.info("Exporting Layer of Type: {0}".format(geometry_type.upper()))
    ogr_command = "/usr/local/bin/ogr2ogr -append -f {ogr_format} -sql \'{select_statement}\' -nlt {geometry_type} {export_file} "\
        "PG:\"{db_connection}\" {options}".format(
        ogr_format=SUPPORTED_FORMATS[export_format],
        srs=Keys.SRS_4326,
        select_statement=select_statement,
        export_file=export_file,
        db_connection=database_connection_string_for_ogr('default'),
        options="FGDB_BULK_LOAD" if export_format == 'gdb' else '',
        geometry_type=geometry_type.upper()
        )

    logger.info("Data Export: " + ogr_command)

    return ogr_command


def construct_export_filename(entity, extension):
    export_file_name = "{db_entity}_{timestamp}.{extension}".format(
        db_entity=entity.name.replace(" ", "_"),
        timestamp=timestamp(),
        extension=extension)

    return export_file_name

@app.task
def _export_query_results(job, class_name, unique_id, filename, query, event='queryResultExportCompleted'):

    try:
        job.status = "Exporting"
        job.save()

        # add timestamp to filename to prevent conflicts
        filename = filename + "_" + timestamp()
        result = OGRETL().export(filename, query, 'CSV', geom=None)

        job.data = '/' + filename + ".csv"
        job.save()

        send_message_to_client(job.user.id, dict(event=event,
                                                 class_name=class_name,
                                                 unique_id=unique_id,
                                                 job_id=str(job.hashid)))

        job.status = 'Complete'

    except Exception, e:
        logger.error(e)
        job.status = "Failed"

        exc_type, exc_value, exc_traceback = sys.exc_info()
        readable_exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
        job.data = readable_exception
        job.save()

        send_message_to_client(job.user.id, dict(event=job.type + " failed", trace=readable_exception))

    job.ended_on = timezone.now()
    job.save()
