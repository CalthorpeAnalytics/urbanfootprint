
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

from footprint.main.models.analysis.energy_feature import EnergyFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute, StyleValueContext, Style


class EnergyFeatureLayerStyle(LayerStyle):
    model_class = EnergyFeature

    style_attributes = [
        StyleAttribute(
            attribute='annual_million_btus_per_unit',
            style_type=StyleTypeKey.QUANTITATIVE,
            style_value_contexts=[
                StyleValueContext(value=0, symbol='=', style=Style(
                    polygon_fill='#909090'
                )),
                StyleValueContext(value=0, symbol='>', style=Style(
                    polygon_fill='#97D704'
                )),
                StyleValueContext(value=5, symbol='>', style=Style(
                    polygon_fill='#B2D103'
                )),
                StyleValueContext(value=10, symbol='>', style=Style(
                    polygon_fill='#CBCA03'
                )),
                StyleValueContext(value=15, symbol='>', style=Style(
                    polygon_fill='#C5A703'
                )),
                StyleValueContext(value=20, symbol='>', style=Style(
                    polygon_fill='#BF8603'
                )),
                StyleValueContext(value=30, symbol='>', style=Style(
                    polygon_fill='#B96602'
                )),
                StyleValueContext(value=40, symbol='>', style=Style(
                    polygon_fill='#B34802'
                )),
                StyleValueContext(value=55, symbol='>', style=Style(
                    polygon_fill='#AD2C02'
                )),
                StyleValueContext(value=80, symbol='>', style=Style(
                    polygon_fill='#A71102'
                )),
                StyleValueContext(value=120, symbol='>', style=Style(
                    polygon_fill='#A1020B'
                )),
            ]
        )
    ]
