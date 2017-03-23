
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

from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.geospatial.built_form_feature import BuiltFormFeature
from footprint.main.models.geospatial.geometry_type_keys import StyleTypeKey
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.style_attribute import StyleAttribute

__author__ = 'calthorpe_analytics'

class BuiltFormFeatureLayerStyle(LayerStyle):
    model_class = BuiltFormFeature

    style_attributes = [
        StyleAttribute(
            attribute='built_form__id',
            style_type=StyleTypeKey.CATEGORICAL
        )
    ]

class BuiltFormLayerStyle(LayerStyle):
    model_class = BuiltForm

    style_attributes = [
        StyleAttribute(
            attribute='id',
            style_type=StyleTypeKey.CATEGORICAL
        )
    ]
