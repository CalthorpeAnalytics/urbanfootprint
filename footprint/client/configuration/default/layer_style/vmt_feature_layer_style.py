
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

from footprint.main.models.analysis.vmt_features.vmt_feature import VmtFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute, StyleValueContext, Style


class VmtFeatureLayerStyle(LayerStyle):
    model_class = VmtFeature

    style_attributes = [
        StyleAttribute(
            attribute='vmt_daily_per_hh',
            style_type=StyleTypeKey.QUANTITATIVE,
            style_value_contexts=[
                StyleValueContext(value=0, symbol='=', style=Style(**{
                    'polygon-fill': '#E8E8E8',
                    'line-color': '#909090',
                    'line-width': .3,
                })),
                StyleValueContext(value=0, symbol='>', style=Style(**{
                    'polygon-fill': '#004d1a',
                    'line-color': '#909090',
                    'line-width': .3,
                })),

                StyleValueContext(value=20, symbol='>', style=Style(**{
                    'polygon-fill': '#009933',
                    'line-color': '#909090',
                    'line-width': .3,
                })),
                StyleValueContext(value=30, symbol='>', style=Style(**{
                    'polygon-fill': '#00CC33',
                    'line-color': '#909090',
                    'line-width': .3,
                })),
                StyleValueContext(value=40, symbol='>', style=Style(**{
                    'polygon-fill': '#FFFF00',
                    'line-color': '#909090',
                    'line-width': .3,
                })),
                StyleValueContext(value=60, symbol='>', style=Style(**{
                    'polygon-fill': '#FF9900',
                    'line-color': '#909090',
                    'line-width': .3,
                }))                ,
                StyleValueContext(value=80, symbol='>', style=Style(**{
                    'polygon-fill': '#cc1500',
                    'line-color': '#909090',
                    'line-width': .3,
                }))
            ]
        )
    ]
