
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

"""
A very minimal import/export utility from files into postgis and out again
"""
import pipes
from pprint import pprint
from django.conf import settings

__author__ = 'calthorpe_analytics'

from itertools import product
from sarge import capture_both, get_both
from footprint.main.utils.uf_toolbox import report_sql_values_as_dict
from footprint.main.utils.utils import database_connection_string_for_ogr, timestamp

import fiona
import logging
import tarfile
import zipfile

logger = logging.getLogger(__name__)


class OGRETL(object):

    DB_CONNECTION = database_connection_string_for_ogr('default')
    EXPORT_COMMAND = '/usr/local/bin/ogr2ogr -append -f {{output_format}} {{geom_type}} {{export_file}} ' \
                     'PG:\"{db_connection}\" {{source}} {{options}}'.format(db_connection=DB_CONNECTION)

    IMPORT_COMMAND = '/usr/local/bin/ogr2ogr -overwrite -skipfailures -progress -f "PostgreSQL"'\
                     'PG:\"{db_connection}\" {{source}} {{options}}'.format(db_connection=DB_CONNECTION)

    FORMATS = {
        "FileGDB": {'ext': "gdb", 'options': ['FGDB_BULK_LOAD']},
        "GeoJSON": {'ext': "json"},
        "CSV": {'ext': "csv"},  # does not export geography
        # "PDF": {'ext': "pdf"},  # does not make sense
        "KML": {'ext': 'kml', 'options': ['NameField={name}']}
    }

    def __init__(self):
        self.import_drivers = {driver: options for driver, options in fiona.supported_drivers.items() if 'r' in options}
        self.export_drivers = {driver: options for driver, options in fiona.supported_drivers.items() if 'w' in options}

    def test(self):
        layers = {'transit_stops': "select * from scag__or_scenarios.major_transit_stops",
                  'land_use_parcels': "select * from scag__or_scenarios.region_existing_land_use_parcels"}

        outputs = [output for output, args in self.FORMATS.items()]
        tests = product(outputs, layers.items())

        for output, layer in tests:
            result = self.export(layer[0] + "_" + output, layer[1], output)

            assert not result.returncode, "ERROR: {layer} > {output}: {err}".format(layer=layer[0], output=output, err=result.stderr.text)
            print "[x] {layer} > {output}".format(layer=layer[0], output=output)

    def export(self, name, statement, output_format, geom="wkb_geometry"):

        if geom:
            geom_type = '-nlt ' + report_sql_values_as_dict(
                "SELECT GeometryType({geom}) from ({query}) b group by GeometryType({geom});".format(
                    geom=geom, query=statement)
            )[0]['geometrytype']
        else:
            geom_type = ''

        output_file = '{dir}/{name}.{ext}'.format(name=name,
                                                  ext=self.FORMATS[output_format]['ext'],
                                                  dir=settings.SENDFILE_ROOT)

        source = "-sql {statement}".format(statement=pipes.quote(statement))
        logger.info("Exporting with sql argument %s" % source)

        options_formatting = dict(name=name)
        formatted_options = [option.format(**options_formatting) for option in self.FORMATS[output_format].get('options', [])]

        ogr_cmd = self.EXPORT_COMMAND.format(
            output_format=output_format,
            geom_type=geom_type,
            source=source,
            export_file=output_file,
            options=" ".join(formatted_options)
        )

        logger.info(ogr_cmd)
        result = capture_both(ogr_cmd)
        assert not result.returncode, "ERROR: {name} > {output}: {err}".format(name=name, output=output_format, err=result.stderr.text)

        return result


    # TODO this is broken :( i mean it never worked  -ekb
    def inspect(self, input_path):

        archive = "tar" if tarfile.is_tarfile(input_path) else "zip" if zipfile.is_zipfile(input_path) else None
        if archive:
            archive_location = "{f}:///{path}".format(f=archive, path=input_path)
            layer_names = fiona.listlayers("", vfs=archive_location)
            layers = [fiona.open(layer_name, vfs=archive_location) for layer_name in layer_names]

        else:
            layer_names = fiona.listlayers(input_path)
            layers = [fiona.open(layer_name, input_path) for layer_name in layer_names]

        return [layer.meta for layer in layers]
