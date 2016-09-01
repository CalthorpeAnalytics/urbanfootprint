import shlex
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location
from ModestMaps.OpenStreetMap import Provider

from django.conf import settings
import logging
import shutil
from sarge import capture_both

from footprint.main.utils.utils import create_static_content_subdir
from tilestache_uf.models import Config

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


def generate_coordinates(ul, lr, zooms, padding):
    """ Generate a stream of coordinates for seeding.

        Flood-fill coordinates based on two corners, a list of zooms and padding.
    """
    offset = 0
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)

                yield coord
                offset += 1


def invalidate_feature_cache(layer_key, features):
    """
    invaldiates the cached tiles that contain the features
    @:param features: array of feature objects
    :return:
    """


    logger.info("Invalidating features: {0}".format(features))
    # get bbox of features
    dj_config = Config.objects.get()
    config = dj_config.tilestache_config_object

    logger.info("Config Cache: {0}".format(config.cache))

    from TileStache.Caches import S3, Test
    if isinstance(config.cache, Test):
        return
    osm = Provider()

    try:
        ts_layer = config.layers[layer_key]
    except IndexError:
        logger.exception('Cannot invalidate %r', layer_key)
        return

    cleared = 0
    keys = []
    for f in features:

        lon1, lat1, lon2, lat2 = f.wkb_geometry.extent

        south, west = min(lat1, lat2), min(lon1, lon2)
        north, east = max(lat1, lat2), max(lon1, lon2)
        northwest = Location(north, west)
        southeast = Location(south, east)

        ul = osm.locationCoordinate(northwest)
        lr = osm.locationCoordinate(southeast)

        for coord in generate_coordinates(ul, lr, range(4, 19), padding=0):
            if isinstance(config.cache, S3.Cache):
                keys.append(S3.tile_key(ts_layer, coord, 'png', config.cache.path))
            else:
                logger.info("ts_layer: {0}, coord: {1}".format(ts_layer, coord))
                config.cache.remove(ts_layer, coord, 'png')
            cleared += 1

    if keys:
        config.cache.bucket.delete_keys(keys)

    logger.info("cleared {0} TILES".format(cleared))


def carto_css(mml, name):
    """
    Takes MML string input and writes it to a Mapnik XML file.
    :param mml: an mml string, containing the proper CartoCSS styling and connection attributes required by the
    CartoCSS conversion program
    :param name: the unique name of the layer (standard method is to name it with its database schema and table name)
    :return mapfile: a cascadenik-ready document.
    """
    from sarge import shell_format, run, Capture
    create_static_content_subdir('cartocss')
    mml_file = "{0}/cartocss/{1}.mml".format(settings.MEDIA_ROOT, name)
    xml_file = mml_file.replace(".mml", ".xml")
    f = open(mml_file, 'w+')
    f.write(mml)
    f.close()

    if not settings.FOOTPRINT_INIT:

        carto_css_command = shell_format("{0}/carto {1}".format(settings.BIN_DIR, mml_file))
        logger.debug("Running carto: %s" % carto_css_command)
        carto_css_content = None

        try:
            carto_result = capture_both(carto_css_command)
            assert not any(carto_result.returncodes)
            carto_css_content = carto_result.stdout.text
            logger.debug("Carto xml content: %s" % carto_css_command)
            f = open(xml_file, 'w')
            f.write(carto_css_content)
            f.close()

        except AssertionError, e:
            logger.error("Failed to generate cartocss for {mml}. Exception: {message}. {carto_output}".format(
                mml=mml_file, message=carto_result.stderr.text, carto_output=carto_css_content))
            raise e

    return xml_file


def invalidate_cache(layer_key, config_key='default'):
    """
    Invalidates the entire cache for the layer
    :return:
    """
    from TileStache.Caches import S3, Disk, Test
    logger.debug("starting invalidation")
    dj_config = Config.objects.filter(name=config_key)
    if not dj_config.exists():
        return
    dj_config = dj_config[0]
    config = dj_config.tilestache_config_object

    if isinstance(config.cache, S3.Cache):
        prefix_key = '{path}{key}'.format(bucket=dj_config.cache['bucket'], path=dj_config.cache['path'], key=layer_key)
        logger.info('clearing S3 cache for {key}'.format(key=prefix_key))
        keys = [k for k in config.cache.bucket.list(prefix=prefix_key)]

        if len(keys):
            result = config.cache.bucket.delete_keys(keys)
            assert not result.errors, [e for e in result.errors]
            logger.info("Cleared S3 cache: {0} ({1} tiles)".format(prefix_key, len(result.deleted)))
            # time.sleep(5)

    elif isinstance(config.cache, Disk):
        layer_cache = shlex.os.path.join(config.cache.cachepath, layer_key)
        shutil.rmtree(layer_cache, ignore_errors=True)

    elif isinstance(config.cache, Test):
        return

    else:
        raise Exception("Cache is not recognized!")
