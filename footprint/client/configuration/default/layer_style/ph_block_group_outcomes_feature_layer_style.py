
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

from footprint.main.models.analysis.public_health_features.ph_block_group_outcomes_feature import PhBlockGroupOutcomesFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute, StyleValueContext, Style


class PhBlockGroupOutcomesLayerStyle(LayerStyle):
    model_class = PhBlockGroupOutcomesFeature

    _style_attributes = [
        StyleAttribute(
            attribute='adult_all_walk_minutes',
            style_type=StyleTypeKey.QUANTITATIVE,
            style_value_contexts=[
                StyleValueContext(value=0, symbol='=', style=Style(
                    polygon_fill='#E8E8E8'
                )),
                StyleValueContext(value=0, symbol='>', style=Style(
                    polygon_fill='#C3523C'
                )),
                StyleValueContext(value=2, symbol='>', style=Style(
                    polygon_fill='#B1782D'
                )),
                StyleValueContext(value=4, symbol='>', style=Style(
                    polygon_fill='#9F9F1E'
                )),
                StyleValueContext(value=6, symbol='>', style=Style(
                    polygon_fill='#8DC60F'
                )),
                StyleValueContext(value=8, symbol='>', style=Style(
                    polygon_fill='#7BED00'
                )),
                StyleValueContext(value=15, symbol='>', style=Style(
                    polygon_fill='#5FBC1E'
                )),
                StyleValueContext(value=20, symbol='>', style=Style(
                    polygon_fill='#438C3D'
                )),
                StyleValueContext(value=25, symbol='>', style=Style(
                    polygon_fill='#275C5B'
                )),
                StyleValueContext(value=30, symbol='>', style=Style(
                    polygon_fill='#0B2C7A'
                )),
            ]
        )
    ]
