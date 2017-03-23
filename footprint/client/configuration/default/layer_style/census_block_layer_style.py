
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

from footprint.main.models.base.census_block import CensusBlock
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute, StyleValueContext, Style

__author__ = 'calthorpe_analytics'

class CensusBlockLayerStyle(LayerStyle):
    model_class = CensusBlock

    style_attributes = [
        StyleAttribute(
            attribute='wkb_geometry',
            style_type=StyleTypeKey.SINGLE,
            style_value_contexts=[
                StyleValueContext(value=None, symbol=None, style=Style(
                    line_color='#CCFFFF',
                    line_width=3
                ))
            ]
        )
    ]
