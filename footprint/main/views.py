
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

from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from psycopg2.extensions import AsIs

from footprint.main.models.config.project import Project
from footprint.main.models.config.scenario import Scenario
from footprint.main.sql.config_entity_data import CONFIG_ENTITY_SUBCLASS_DATA_SQL

API_BASE_URL = '/footprint/api/'


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    column_names = [col[0] for col in desc]

    return [
        dict(zip(column_names, row))
        for row in cursor.fetchall()
    ]


def get_project_data(request):

    return get_config_entity_subclass_data(request, Project)


def get_scenario_data(request):

    return get_config_entity_subclass_data(request, Scenario)


def get_config_entity_subclass_data(request, subclass):
    subclass_name = subclass.__name__.lower()

    subclass_specifc_data = {
        'project': {
            'parent_subclass_api_version': 'v1',
            'parent_subclass': 'region',
            'year_column_name': AsIs('base_year'),
            'permission_lookup_table': 'project'
        },
        'scenario': {
            'parent_subclass_api_version': 'v2',
            'parent_subclass': 'project',
            'year_column_name': AsIs('year'),
            'permission_lookup_table': 'basescenario'
        }
    }

    username = request.GET.get('username')
    api_key = request.GET.get('api_key')

    if 'parent_config_entity__id__in' in request.GET:
        filtering_clause = 'parent_config_entity_id = any(array[{0}])'.format(request.GET['parent_config_entity__id__in'])

    elif 'id__in' in request.GET:
        filtering_clause = 'id = any(array[{0}])'.format(request.GET['id__in'])

    elif 'id' in request.GET:
        filtering_clause = 'id = {0}'.format(request.GET['id'])

    else:
        return HttpResponseBadRequest('Query filtering was not in ["parent_config_entity__id__in", "id__in", or "id"]')

    try:
        user = get_user_model().objects.get(username=username, api_key__key=api_key)
    except get_user_model().DoesNotExist:
        return HttpResponse(status=401)

    params = {
        'user_id': user.id,
        'config_entity_subclass': AsIs(subclass_name),
        'config_entity_subclass_str': subclass_name,
        'filtering_clause': AsIs(filtering_clause),
        'api_base_url': API_BASE_URL,
        'v1_api_base_url': API_BASE_URL + 'v1/',
        'v2_api_base_url': API_BASE_URL + 'v2/'
    }

    params.update(subclass_specifc_data[subclass_name])

    cursor = connection.cursor()

    data = {
        'meta': {
            'limit': 1000,
            'next': None,
            'offset': 0,
            'previous': None
        },
        'objects': []
    }

    try:
        cursor.execute(CONFIG_ENTITY_SUBCLASS_DATA_SQL, params)
        db_results = dictfetchall(cursor)
    finally:
        cursor.close()

    for row in db_results:
        data['meta']['total_count'] = len(db_results)

        id = row['id']
        subclass_obj = subclass.objects.get(id=id)
        row['client'] = subclass_obj.client
        row['schema'] = subclass_obj.schema()

        results_data = row.pop('results')
        layers_data = row.pop('layers')

        row['presentations'] = {
            'layers': layers_data,
            'results': results_data
        }

        bounds_geojson = row.pop('bounds')
        row['bounds'] = json.loads(bounds_geojson)

        year_value = row.pop('subclass_year')
        row[str(subclass_specifc_data[subclass_name]['year_column_name'])] = year_value

        data['objects'].append(row)

    return HttpResponse(json.dumps(data), mimetype='application/json')
