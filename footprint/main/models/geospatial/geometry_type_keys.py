
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

from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'


class GeometryTypeKey(Keys):
    """
        A Key class to key Geometry Type instances
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            # No prefix since these are so fundamental and are used to create table names,
            # so we don't want them any longer than needed to clearly describe the db_entity
            return ''
    # Preconfigured keys to define the type of Geometry types ie Polygon, Point, etc

    POLYGON = 'polygon'
    LINESTRING = 'linestring'
    POINT = 'point'

    @classmethod
    def postgis_to_geometry_type_key(cls, postgis_value):
        """
            Converts a postgis geometry type to a key of this class
        :param postgis_value:
        :return:
        """
        # TODO complete this list
        return dict(
            ST_Point=cls.POINT,
            ST_LineString=cls.LINESTRING,
            ST_MultiLineString=cls.LINESTRING,
            ST_Polygon=cls.POLYGON,
            ST_MultiPolygon=cls.POLYGON
       )[postgis_value]


class StyleTypeKey(Keys):
    """
        A Key class to key Geometry Type instances
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            # No prefix since these are so fundamental and are used to create table names,
            # so we don't want them any longer than needed to clearly describe the db_entity
            return ''
    # Preconfigured keys to define the type of Geometry types ie Polygon, Point, etc

    SINGLE = 'single'
    CATEGORICAL = 'categorical'
    QUANTITATIVE = 'quantitative'
