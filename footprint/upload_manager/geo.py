
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

import os
import re
import logging
import tempfile
import subprocess
from time import time
from zipfile import ZipFile

import ogr
import osr
import requests
from memoize import memoize

from django.db import connection
from django.conf import settings

from footprint.upload_manager.db import get_db_entity_params, create_db_entity, load_to_database


logger = logging.getLogger(__name__)


OGR_DRIVER_MAP = {
    '.gdb': 'FileGDB',
    '.shp': 'ESRI Shapefile'
}
GEOMETRY_COLUMN_NAME = 'wkb_geometry'
CACHE_TIMEOUT = 60 * 60 * 24 * 7  # one week


class UnknownEsriSRIDException(Exception):
    def __init__(self, geo_fpath):
        Exception.__init__(self, "Unable to determine SRID from esri filepath {}".format(geo_fpath))


class NoProjectionDataAvailable(Exception):
    def __init__(self, geo_fpath):
        Exception.__init__(self, "Unable to extract projection string from filepath {}".format(geo_fpath))


def process_file(zip_filepath, *args, **kwargs):
    """
    The main entry point into the processing of an uploaded zip file. The filepath
    param represents an absolute filepath to zipped gdb or shape file dataset residing
    on disk. This method will either load the data into a table in the import schema so
    that it may load data for the testing tool, or it will create a DbEntity and trigger
    the related post-save processing, which completes a series of tasks necessary for
    an uploaded geospatial dataset to become a UF layer.
    """

    logger.debug("Processing %s with kwargs: %s", zip_filepath, kwargs)

    # whether we should create a DbEntity (default is to just load data into db)
    should_create_db_entity = kwargs.get('should_create_db_entity')

    # Whether we should filter the layer name for a multi-layer upload.
    # For uploads from a gdb fileset from the arc tool, the filename is
    # actually the name of the layer the user selected for upload, and
    # therfore doesn't have a file extension like .shp or .zip.
    upload_task = kwargs.get('upload_task')
    if upload_task:
        upload_task_fname = upload_task.name
        if upload_task_fname.endswith('.zip') or upload_task_fname.endswith('.shp'):
            layer_name = None
        else:
            layer_name = upload_task_fname
    else:
        layer_name = None

    geo_fpath = get_geospatial_filepath(zip_filepath)
    layer_names = get_layer_names(geo_fpath, layer_name)

    for layer_name in layer_names:

        if should_create_db_entity:
            db_entity_key, db_entity_name = get_db_entity_params(layer_name)
            table_name = db_entity_key

        else:
            # otherwise get the filename without extention appended with
            # a timestamp to avoid collision with any other tables, e.g.:
            # /path/to/uploaded_dataset.zip --> uploaded_dataset_1457393348
            table_name = "{}_{}".format(layer_name.lower(), int(time()))

        # run ogr2ogr and generate a .sql script to load the transformed data
        pg_dump_fpath = convert_to_pgdump(geo_fpath, layer_name, table_name)

        if should_create_db_entity:
            layer_count = len(layer_names)
            create_db_entity(pg_dump_fpath, db_entity_key, db_entity_name, table_name, layer_count, *args, **kwargs)

        # if not creating a DbEntity and associated layers, etc., just load
        # the data for use with the testing tool
        else:
            load_to_database(pg_dump_fpath, table_name)

    # The return value is only used by the UI testing tool.
    # If the dataset contains multiple layers, we'll just
    # return the table name for the last layer.
    return table_name


def get_layer_names(geo_fpath, selected_layer_name=None):
    """
    Since layers in the same dataset can use
    different projections, we'll need to create a
    DbEntity for each layer. Use the osr library from
    gdal to loop through layers and grab their names.
    """

    _, geo_ext = os.path.splitext(geo_fpath)
    driver_name = OGR_DRIVER_MAP[geo_ext]

    driver = ogr.GetDriverByName(driver_name)
    dataset = driver.Open(geo_fpath, 0)

    layer_names = []
    for idx in xrange(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(idx)
        layer_name = layer.GetName()

        if selected_layer_name:
            if selected_layer_name == layer_name:
                layer_names.append(layer_name)
                break
        else:
            layer_names.append(layer_name)

    return layer_names


def get_geospatial_filepath(zip_filepath):
    """
    Extract the zip file and return the filepath that we'll need to
    pass into ogr2ogr. For shapefile archives, this will be the file
    with a .shp extension. gdb archives contain multiple file inside
    a directory that ends in .gdb, e.g.: `dataset_name.gdb/file1.gdbtable`.
    ogr2ogr gets passed the <dataset_name>.gdb directory path.
    """

    # create a temp directory to extract inside of
    tmp_dir = tempfile.mkdtemp()

    with ZipFile(zip_filepath) as zipped_file:
        zipped_file.extractall(path=tmp_dir)

    # loop through unzipped files and handle some special cases
    for unzipped_fname in zipped_file.namelist():

        # some archives contain encoded files with names like '__MACOSX'
        if unzipped_fname.startswith('__'):
            continue

        if unzipped_fname.endswith('.shp'):
            fpath = os.path.join(tmp_dir, unzipped_fname)
            return fpath

        elif '.gdb/' in unzipped_fname:
            fpath = os.path.join(tmp_dir, unzipped_fname)
            return fpath.split('.gdb/')[0] + '.gdb'


def convert_to_pgdump(geo_fpath, layer_name, table_name):
    """
    This method makes necessary calls to get the projection data
    string and SRID that corresponds to the layer_name param,
    then executes ogr2ogr in a subprocess to convert the
    geospatial dataset into a pg_dump file.

    """

    projection_data = get_projection_string(geo_fpath, layer_name)

    if not projection_data:
        logger.error("Unable to extract projection data string from filepath %s", geo_fpath)
        raise NoProjectionDataAvailable(geo_fpath)

    # get the SRID needed for postgis from the projection data string
    srid = get_srid_from_esri_prj(projection_data)

    if not srid:
        # we can't do anything meaningful with the layer if we don't know the srid
        # TODO: create a data model to represent SRID-lookup and projection-extraction
        # misses so we have persistent examples to make improvements from
        logger.error("Unable to determine SRID from filepath %s", geo_fpath)
        raise UnknownEsriSRIDException(geo_fpath)

    # the resoluting sql script that will load the data
    directory = os.path.dirname(os.path.realpath(geo_fpath))
    sql_fpath = os.path.join(directory, "{}.sql".format(layer_name.replace(' ', '_')))

    # construct the ogr2ogr command list
    cmd = [
        "ogr2ogr",
        "--config", "PG_USE_COPY", "YES",  # use copy instead of insert for performance
        "-f", "PGDump", sql_fpath, geo_fpath,
        "-lco", "SCHEMA={}".format(settings.IMPORT_SCHEMA),
        "-nln", table_name,
        "-lco", "GEOMETRY_NAME={}".format(GEOMETRY_COLUMN_NAME),
        "-lco", "DROP_TABLE=IF_EXISTS",
        "-lco", "CREATE_SCHEMA=OFF",
        "-nlt", "GEOMETRY",
        "-lco", "SRID={}".format(srid),
        "-lco", "COLUMN_TYPES=wkb_geometry=geometry",
        "-lco", "PRECISION=NO",
        layer_name
    ]

    logger.debug("Performing the following ogr2ogr command: %s", ' '.join(cmd))

    # run ogr2ogr in a subprocess and return the filepath to the generated sql file
    subprocess.check_call(cmd)

    return sql_fpath


def get_projection_string(geo_fpath, layer_name):
    """
    Run ogrinfo on the layer and get the projection-related
    data string from the ouptut.
    """

    cmd = ["ogrinfo", "-so", geo_fpath, layer_name]

    output = subprocess.check_output(cmd)

    return get_projection_string_from_output(output)


def get_projection_string_from_output(output):
    """
    See the docstring for the method get_srid_from_esri_prj below
    (or the unit tests in footprint/upload_manager/tests.py) for
    an example format of the projection data string ogrinfo
    emits this string with other output unrelated to the layer
    projection, we so parse the entire string to extract only
    the PROJCS[...] or GEOGCS[...] section and remove whitespaces.
    """

    start_idx = output.find('PROJCS')
    if start_idx == -1:
        start_idx = output.find('GEOGCS')
        if start_idx == -1:
            return

    stack = []
    stack_modified = False
    for i, char in enumerate(output[start_idx:]):
        if char == '[':
            stack.append(char)
            stack_modified = True
        elif char == ']':
            stack.pop()
        if stack_modified and not stack:
            end_idx = start_idx + i
            projection = output[start_idx:end_idx+1]
            projection = re.sub(r'^\s*', '', projection, flags=re.MULTILINE)  # strip leading whitespaces from each line
            projection = re.sub(r'\s*$', '', projection, flags=re.MULTILINE)  # and trailing whitespaces
            projection = re.sub(r'\n', '', projection)  # and then finally newline characters

            return projection


def get_srid_from_esri_prj(projection_data):
    """
    `projection_data` is the form of, e.g.:

    PROJCS[
        "NAD_1983_StatePlane_California_V_FIPS_0405_Feet",
        GEOGCS[
            "GCS_North_American_1983",
            DATUM[
                "D_North_American_1983",
                SPHEROID[
                    "GRS_1980",
                    6378137.0,
                    298.257222101
                ]
            ],
            PRIMEM[
                "Greenwich",
                0.0
            ],
            UNIT[
                "Degree",
                0.0174532925199433
            ]
        ],
        ...
        UNIT[
            "Foot_US",
            0.3048006096012192
        ]
    ]

    from which we need to extract a SRID before inserting into PostGIS. We can do this using
    the osr library from gdal or through an API endpoint at prj2epsg.org. The order of attempts
    goes like: osr, osr with modified projection string, prj2epsg.org API, and finally
    prj2epsg.org API with modified projection string. The modified string represents
    the projection string with instances of AUTHORITY[...] tags removed, as testing has shown
    those to have resulted in false positives.
    """

    # TODO: investigate string parsing/matching on postgis's spatial_ref_sys table (srtext column)

    # first try with osr
    srid = get_srid_via_osr(projection_data)

    if is_valid_srid(srid):
        return srid

    # now try with osr with 'AUTHORITY[...]' tags removed
    modified_projection_data = remove_bad_auth_code(projection_data)
    srid = get_srid_via_osr(modified_projection_data)

    if is_valid_srid(srid):
        return srid

    # try with the API using the original projection_data
    srid = get_srid_via_api(projection_data)

    if is_valid_srid(srid):
        return srid

    # finally try the API using the modified project_data
    srid = get_srid_via_api(modified_projection_data)

    if is_valid_srid(srid):
        return srid


def get_srid_via_osr(projection_data):
    """Attempt to retrive the SRID using osr's API."""

    srs = osr.SpatialReference()
    srs.ImportFromESRI([projection_data])
    srs.AutoIdentifyEPSG()

    code = srs.GetAuthorityCode(None)
    if code:
        return int(code)


@memoize(timeout=CACHE_TIMEOUT)
def get_srid_via_api(projection_data):
    """
    Make an API call to prj2epsg.org to lookup the SRID.
    An example return data payload looks like:

    {
        "exact":true,
        "html_terms":"PROJCS...",
        "codes":[{
            "name":"NAD_1983_StatePlane_California_V_FIPS_0405_Feet",
            "code":"2229",
            "url":"http://prj2epsg.org/epsg/2229.json"
        }],
        "html_showResults":true
    }

    """

    url = "http://prj2epsg.org/search.json?mode=wkt&terms={}".format(projection_data)
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if 'codes' in data and len(data['codes']) == 1:
            if 'code' in data['codes'][0]:
                return int(data['codes'][0]['code'])


@memoize(timeout=CACHE_TIMEOUT)
def is_valid_srid(srid):
    """
    Returns True if the extracted SRID exists in PostGIS's
    spatial_ref_sys table, otherwise returns False.
    """

    if not srid:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM spatial_ref_sys WHERE srid = %(srid)s", {'srid': srid})
        result = cursor.fetchone()
    finally:
        cursor.close()

    return result[0] > 0


def remove_bad_auth_code(projection_string):
    """
    Remove instances of, e.g., ",AUTHORITY['EPSG','2229']" as they can
    result in false positives of invalid SRIDs -- osr and the prj2epsg
    API seem to check the 'AUTHORITY' tags first and often get
    the right SRID value after bad tags are removed when the tag
    included a bad SRID value.
    """

    return re.sub(r',AUTHORITY\[[^\]]*\]', '', projection_string)
