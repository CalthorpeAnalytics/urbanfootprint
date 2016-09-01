
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

from mock import patch

from django.test import TestCase

from footprint.upload_manager.geo import is_valid_srid, get_projection_string_from_output, get_db_entity_params, \
                                         get_srid_via_osr, get_srid_from_esri_prj


PROJCS_OGRINFO_OUTPUT = """
    INFO: Open of `USGS_BATHYMETRY.gdb'
          using driver `FileGDB' successful.

    Layer name: USGS_BATHYMETRY_CONTOURS_50FT
    Geometry: Multi Line String
    Feature Count: 1316
    Extent: (6300537.172183, 1583793.355584) - (6638069.926930, 1830244.032038)
    Layer SRS WKT:
    PROJCS["NAD_1983_StatePlane_California_V_FIPS_0405_Feet",
        GEOGCS["GCS_North_American_1983",
            DATUM["North_American_Datum_1983",
                SPHEROID["GRS_1980",6378137,298.257222101]],
            PRIMEM["Greenwich",0],
            UNIT["Degree",0.017453292519943295]],
        PROJECTION["Lambert_Conformal_Conic_2SP"],
        PARAMETER["False_Easting",6561666.666666666],
        PARAMETER["False_Northing",1640416.666666667],
        PARAMETER["Central_Meridian",-118],
        PARAMETER["Standard_Parallel_1",34.03333333333333],
        PARAMETER["Standard_Parallel_2",35.46666666666667],
        PARAMETER["Latitude_Of_Origin",33.5],
        UNIT["Foot_US",0.30480060960121924],
        AUTHORITY["EPSG","102645"]]
    FID Column = OBJECTID
    Geometry Column = Shape
    ID: Real (0.0)
    CONTOUR: Real (0.0)
    Shape_Length: Real (0.0)
"""

PROJCS_PROJECTION_STRING = """\
PROJCS["NAD_1983_StatePlane_California_V_FIPS_0405_Feet",GEOGCS["GCS_North_American_1983",\
DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],\
PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic_2SP"],\
PARAMETER["False_Easting",6561666.666666666],PARAMETER["False_Northing",1640416.666666667],\
PARAMETER["Central_Meridian",-118],PARAMETER["Standard_Parallel_1",34.03333333333333],\
PARAMETER["Standard_Parallel_2",35.46666666666667],PARAMETER["Latitude_Of_Origin",33.5],\
UNIT["Foot_US",0.30480060960121924],AUTHORITY["EPSG","102645"]]\
"""

GEOGCS_PROJECTION_STRING = """\
GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],\
PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]\
"""

GEOGCS_PROJECTION_STRING_EXPANDED = """
   GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]
"""


class MockedRequest(object):
    """A class to mock the class returned by `requests.get()`"""

    def __init__(self, return_payload):
        self.return_payload = return_payload
        self.status_code = 200

    def json(self):
        return self.return_payload


class UploadManagementTestCase(TestCase):
    def test_is_valid_srid(self):
        """Test that we can lookup SRIDs in Postgis's spatial_ref_sys table."""

        self.assertEqual(is_valid_srid(4362), True)
        self.assertEqual(is_valid_srid(102645), False)

    def test_get_db_entity_params(self):
        """Test that we can extract proper DbEntity key and name values from the geospatial layer name."""

        layer_name = 'USGS_BATHYMETRY_CONTOURS_50FT'
        expected_params = ('usgs_bathymetry_contours_50_ft', 'Usgs Bathymetry Contours 50 Ft')
        self.assertEqual(get_db_entity_params(layer_name), expected_params)

    def test_get_projection_string_from_output(self):
        """
        Test that we can extract the projection-related data from
        the output of ogrinfo.
        """

        output = PROJCS_OGRINFO_OUTPUT
        projection_string = get_projection_string_from_output(output)
        expected_output = PROJCS_PROJECTION_STRING
        self.assertEqual(projection_string, expected_output)

    def test_preserve_internal_whitespace(self):
        """
        Test that we extract compact projection data but preserve
        any whitespace characters inside the projection data content.
        """

        expanded = GEOGCS_PROJECTION_STRING_EXPANDED
        compact = get_projection_string_from_output(expanded)
        self.assertEqual(compact, GEOGCS_PROJECTION_STRING)

    def test_get_gcs_srid_via_osr(self):
        srid = get_srid_via_osr(GEOGCS_PROJECTION_STRING)
        self.assertEqual(srid, 4326)

    def test_get_srid_with_bad_auth_code(self):
        """
        Test that a bad projection string returns the wrong SRID until we
        modify it to return the expected SRID.
        """

        with patch('footprint.upload_manager.geo.requests.get') as patched_get:

            patched_get.side_effect = [
                MockedRequest({
                    u'html_showResults': True,
                    u'codes': [
                        {
                            u'url': u'http://prj2epsg.org/epsg/102645.json',
                            u'code': u'102645',
                            u'name': u'NAD_1983_StatePlane_California_V_FIPS_0405_Feet'
                        }
                    ],
                    u'exact': True
                }),
                MockedRequest({
                    u'html_showResults': True,
                    u'codes': [
                        {
                            u'url': u'http://prj2epsg.org/epsg/2229.json',
                            u'code': u'2229',
                            u'name': u'NAD_1983_StatePlane_California_V_FIPS_0405_Feet'
                        }
                    ],
                    u'exact': True
                })
            ]

            expected_srid = 2229
            srid = get_srid_from_esri_prj(PROJCS_PROJECTION_STRING)
            self.assertEqual(srid, expected_srid)
