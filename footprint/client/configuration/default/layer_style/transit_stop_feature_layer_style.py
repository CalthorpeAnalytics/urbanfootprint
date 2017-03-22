
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from footprint.main.models.base.transit_stop_feature import TransitStopFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute, StyleValueContext, Style


class TransitStopFeatureLayerStyle(LayerStyle):
    model_class = TransitStopFeature

    _style_attributes = [
        StyleAttribute(
            attribute='route_type',
            style_type=StyleTypeKey.CATEGORICAL,
            style_value_contexts=[
                StyleValueContext(value=0, symbol='=', style=Style(
                    polygon_fill='#FFFF00'
                )),
                StyleValueContext(value=1, symbol='=', style=Style(
                    polygon_fill='#47D147'
                )),
                StyleValueContext(value=2, symbol='=', style=Style(
                    polygon_fill='#7575A3'
                )),
                StyleValueContext(value=3, symbol='=', style=Style(
                    polygon_fill='#CC0099'
                ))
            ]
        )
    ]
