
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
import tempfile

from django.db import connection
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import get_user_model
from footprint.utils.utils import log_exceptions
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest

from footprint.upload_manager.forms import FileForm
from footprint.main.admin.views import admin_required
from footprint.upload_manager.geo import process_file
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.upload_manager.utils import create_task as create_upload_task
from footprint.upload_manager.utils import UploadProgressTaskHandler


TESTING_TOOL_RESULT_LIMIT = 1000


@login_required(login_url='/footprint/login')
@admin_required
def upload_test(request):
    """
    Handle requests for the upload testing tool (/footprint/upload_test).
    This is a simple tool to upload a zipped geospatial file, convert,
    load the data into Postgres and renders a page to verify that we
    properly converted spatial and non-spatial data fields.
    """

    if request.method == 'POST':

        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            for chunk in request.FILES['the_file'].chunks():
                tmpfile.write(chunk)

        # make sure the table_name is lower case so the column_names don't error out when querying
        table_name = process_file(tmpfile.name).lower()
        file_name = request.FILES['the_file']
        return HttpResponseRedirect('/footprint/upload_results?offset=0&table_name={}&file_name={}'.format(table_name, file_name))

    else:
        form = FileForm()

    return render(
        request,
        'upload_manager/simple_file_form.html',
        {
            'form': form,
        }
    )


@csrf_exempt
@log_exceptions
def upload(request):
    """Handle upload POST calls from UF."""

    if request.method != 'POST':
        return HttpResponseNotAllowed('No GET allowed')

    api_key = request.GET.get('api_key')
    username = request.GET.get('username')
    config_entity_id = request.GET.get('config_entity__id')
    file_name = request.GET.get('file_name')
    progress_id = request.GET.get('X-Progress-ID')

    user = get_user_model().objects.get(api_key__key=api_key, username=username)
    config_entity = ConfigEntity.objects.filter(id=config_entity_id).get_subclass()

    upload_task = create_upload_task(
        user,
        file_name,
        config_entity,
        extra_data_dict={'X-Progress-ID': progress_id}
    )

    upload_handler = UploadProgressTaskHandler(max_progress=40, upload_task=upload_task)
    request.upload_handlers.insert(0, upload_handler)

    if request.FILES['files[]'].size > settings.MAX_UPLOAD_SIZE:
        return HttpResponseBadRequest(
            "The maximum file size for uploads is {} but the file you selected is {}".format(
                filesizeformat(settings.MAX_UPLOAD_SIZE),
                filesizeformat(request.FILES['files[]'].size)
            )
        )

    # send the inital progress of 0%
    upload_task.send_progress()

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        for chunk in request.FILES['files[]'].chunks():
            tmpfile.write(chunk)

    try:
        process_file(tmpfile.name, should_create_db_entity=True, user=user, config_entity=config_entity, upload_task=upload_task)
    except:
        upload_task.send_error()
        raise

    return HttpResponse()


@login_required(login_url='/footprint/login')
@admin_required
def upload_results(request):
    """View the results of the test upload."""

    table_name = request.GET.get('table_name')
    offset = request.GET.get('offset')
    file_name = request.GET.get('file_name')

    # create geojson to render in map
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ST_AsGeoJSON(wkb_geometry) FROM import.{} LIMIT {} OFFSET {}".format(table_name, TESTING_TOOL_RESULT_LIMIT, offset))
        rows = cursor.fetchall()
    finally:
        cursor.close()

    geojson = {"type": "FeatureCollection", "features": []}
    for row in rows:
        loaded_row = json.loads(row[0])
        geojson['features'].append({"type": "Feature", "geometry": loaded_row, "properties": {}})

    # get column_names for table view of input file data
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT column_name FROM information_schema.columns \
                        WHERE table_schema = 'import' \
                        AND table_name = '{}'".format(table_name))
        column_names = cursor.fetchall()
    finally:
        cursor.close()

    column_names_list = []
    for column_name in column_names:
        column_name = column_name[0]
        if column_name == 'wkb_geometry':
            continue
        else:
            column_names_list.append(column_name)

    # get columns to put into table except wkb_geometry
    cursor = connection.cursor()
    try:
        # query to get rows from all columns except the geometry column (since we're showing it on the map)
        cursor.execute("""
        SELECT
            'SELECT ' ||
            array_to_string(
                ARRAY(
                    SELECT 'o' || '.' || c.column_name
                    FROM information_schema.columns
                    AS c WHERE table_name = '{table_name}'
                    AND c.column_name NOT IN ('wkb_geometry')
                ),
                ','
            ) ||
            ' FROM import.{table_name} AS o' AS columns
        """.format(table_name=table_name)
        )

        sqlstmt = cursor.fetchone()
        sqlstmt = sqlstmt[0] + ' LIMIT {} OFFSET {}'.format(TESTING_TOOL_RESULT_LIMIT, offset)
        cursor.execute(sqlstmt)
        columns = cursor.fetchall()
    finally:
        cursor.close()

    return render(
        request,
        'upload_manager/view_upload.html',
        {
            'geojson': json.dumps(geojson),
            'column_names': column_names_list,
            'columns': columns,
            'next_offset': int(offset) + TESTING_TOOL_RESULT_LIMIT,
            'previous_offset': int(offset) - TESTING_TOOL_RESULT_LIMIT,
            'file_name': file_name,
            'table_name': table_name
        }
    )
