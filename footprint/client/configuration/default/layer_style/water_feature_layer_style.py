
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

from footprint.main.models.analysis.water_feature import WaterFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleValueContext, StyleAttribute, Style


class WaterFeatureLayerStyle(LayerStyle):
    model_class = WaterFeature

    style_attributes = [
        StyleAttribute(
            attribute='annual_gallons_per_unit',
            style_type=StyleTypeKey.QUANTITATIVE,
            style_value_contexts=[
                StyleValueContext(value=0, symbol='=', style=Style(**{'polygon-fill': '#909090', })),
                StyleValueContext(value=0, symbol='>', style=Style(**{'polygon-fill': '#B3D8FF', })),
                StyleValueContext(value=40, symbol='>', style=Style(**{'polygon-fill': '#9FC6F0', })),
                StyleValueContext(value=60, symbol='>', style=Style(**{'polygon-fill': '#8BB5E1', })),
                StyleValueContext(value=80, symbol='>', style=Style(**{'polygon-fill': '#77A4D2', })),
                StyleValueContext(value=120, symbol='>', style=Style(**{'polygon-fill': '#6392C3', })),
                StyleValueContext(value=160, symbol='>', style=Style(**{'polygon-fill': '#6392C3', })),
                StyleValueContext(value=200, symbol='>', style=Style(**{'polygon-fill': '#5081B5', })),
                StyleValueContext(value=250, symbol='>', style=Style(**{'polygon-fill': '#3C70A6', })),
                StyleValueContext(value=300, symbol='>', style=Style(**{'polygon-fill': '#285E97', })),
                StyleValueContext(value=350, symbol='>', style=Style(**{'polygon-fill': '#144D88', })),
                StyleValueContext(value=400, symbol='>', style=Style(**{'polygon-fill': '#013C7A', })),
            ]
        )
    ]
