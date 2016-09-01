import re
import json
import logging
import traceback

from django.db import connection
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError

from tilestache_uf.models import Layer

log = logging.getLogger(__name__)


def vectors(request, layer_key):

    try:
        layer = Layer.objects.get(key=layer_key)
        layer_value = layer.value
    except Layer.DoesNotExist:
        log.error("The selected lay key {layer_key} does not exist", layer_key=layer_key)
        return HttpResponseNotFound("The selected lay key {} does not exist".format(layer_key), status=404)

    if 'provider' in layer_value and 'parameters' in layer_value['provider']:
        layer_params = layer_value['provider']['parameters']
    else:
        log.error("The layer value is malformed: {layer_value}", layer_value=layer_value)
        return HttpResponseServerError("The layer value is malformed", status=500)

    user_id = request.GET.get('user_id')
    selection_id = request.GET.get('selection_id')

    query_params = {}

    if selection_id:
        # See here for comments about support for filtering layer selections
        # by selection_id and for backwards compatability by user_id:
        # https://github.com/UrbanFootprint/TileStache/pull/5
        query_params['selection_id'] = selection_id

    elif 'user_id_lookup' in layer_params and user_id:
        query_params['selection_id'] = layer_params['user_id_lookup'][str(user_id)]

    else:
        log.error("Invalid get params: {params}. One of `user_id` or `selection_id` is required.", params=request.GET)
        return HttpResponseNotFound("Invalid get params: {}. One of `user_id` or `selection_id` is required.".format(request.GET), status=404)

    cursor = connection.cursor()

    query = layer_params['query'].replace('{user_id}', '%(selection_id)s')
    geom_col_name_match = re.search('SELECT (?P<geom_col_name>"[^"]+"."[^"]+"."wkb_geometry"),', query)

    if geom_col_name_match:
        geom_col_name = geom_col_name_match.group('geom_col_name')
        query = re.sub(geom_col_name, 'ST_AsGeoJSON({})'.format(geom_col_name), query)
    else:
        log.error("Unable to extract the geometry column name from query: {query}", query=query)
        # if we can't manipulate the query to cast the geometry column to GeoJSON,
        # there's nothing meaningful we can return to leaflet
        return HttpResponseServerError("Unable to extract the geometry column name from query: {}".format(query), status=500)

    try:
        cursor.execute(query, query_params)
        rows = cursor.fetchall()
    except Exception as e:
        log.error("Encountered error fetching from the database: {traceback}", traceback=traceback.format_exc())
        return HttpResponseServerError("Encountered error fetching from the database: {}".format(e), status=500)
    finally:
        cursor.close()

    return_data = {
        "type": "FeatureCollection",
        "features": []
    }

    for geojson, _id in rows:
        return_data["features"].append({
            "geometry": json.loads(geojson),
            "type": "Feature",
            "properties": {
                "id": _id
            },
            "id": _id
        })

    return HttpResponse(json.dumps(return_data), mimetype='application/json')
