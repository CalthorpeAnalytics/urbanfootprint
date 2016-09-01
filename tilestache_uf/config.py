import json
from tilestache_uf.srs_keys import SRSKeys

__author__ = 'calthorpe_analytics'
from tilestache_uf.settings import METATILE
import logging
logger = logging.getLogger(__name__)


class Configs:
    VECTOR_LAYER = {
        'metatile': METATILE,
        'provider': {
            'name': 'vector',
            'driver': 'postgis',
            'clipped': False,
            'parameters':
                dict(
                    query=None,
                    column="wkb_geometry",
                    user_id_lookup=None
                ),
        },
        'projected': True,
        'write cache': False,
        'allowed origin': "*",
        'id_property': None
    }

    RASTER_LAYER = {
        "metatile": METATILE,
        'provider': {
            'name': 'mapnik',
            'mapfile': None
        },
        'png options': {
            'palette256': False,
        }
    }

    MML_TEMPLATE = {
        "Layer": [
            {
                "Datasource": {
                    "extent": "",
                    "geometry_field": "wkb_geometry",
                    "srid": 4326,
                    "type": "postgis",
                },

                "png options": {"palette256": False},

                #TODO: look up geometry type from the geometry_columns table
                "geometry": "polygon",
                "srs": SRSKeys.SRS_4326,
                },
            ],
        "interactivity": True,
        "maxzoom": 18,
        "minzoom": 7,
        "format": "png",
        "srs": SRSKeys.SRS_GOOGLE,
    }


def build_vector_layer_config(parameters, provider_id_property=None, client_id_property='id'):
    """
    Creates a configuration dictionary for a vector layer, filling in the details of the template dict above for the
    layer. Supports the custom TileStache hack by ABL to add user_id querying.

    :param parameters:
    :param provider_id_property:
    :param client_id_property:
    :return:
    """

    config_dict = Configs.VECTOR_LAYER.copy()

    config_dict['provider']['parameters'] = parameters
    if provider_id_property:
        config_dict['provider']['id_property'] = client_id_property
        config_dict['provider']['properties'] = {provider_id_property: client_id_property}
    #config_dict['id_property'] = client_id_property

    return config_dict


def build_raster_layer_config(mapfile):
    """
    Creates a configuration dictionary for a raster layer
    :param parameters:
    :return:
    """
    config_dict = Configs.RASTER_LAYER.copy()
    config_dict['provider']['mapfile'] = mapfile
    return config_dict


def build_mml_json(db, query, geom_table, layer_id, name, cls, style):
    mml = Configs.MML_TEMPLATE.copy()
    layer = mml['Layer'][0]
    ds = layer['Datasource']
    ds['dbname'] = db['NAME']
    ds['host'] = db['HOST']
    ds['password'] = db['PASSWORD']
    ds['port'] = db['PORT']
    ds['table'] = '(%s) as foo' % query
    ds['geometry_table'] = geom_table
    ds['user'] = db['USER']
    layer['id'] = layer_id
    layer['name'] = name
    layer['class'] = cls
    layer["srs"] = SRSKeys.SRS_4326,
    mml['Stylesheet'] = [style]
    mml['srs'] = SRSKeys.SRS_GOOGLE

    return json.dumps(mml)
