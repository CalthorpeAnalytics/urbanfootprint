
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

from footprint.main.models.keys.category_key import CategoryKey

__author__ = 'calthorpe_analytics'

class DbEntityCategoryKey(CategoryKey):
    # Keys
    # This key is used for all category values representing Db Entity classificiations
    KEY_CLASSIFICATION = 'DbEntityClassification'
    # Values
    BASEMAPS = 'basemaps'
    REFERENCE = 'reference'
    EDITABLE_LAYER = 'editable_layers'
    CADASTRAL_BOUNDARIES = 'cadastral/boundaries'
    DEMOGRAPHICS = 'demographics'
    ENVIRONMENTAL = 'environmental'
    LAND_USE_ZONING = 'land use/zoning'
    TRANSPORTATION = 'transportation'
    FUTURE_SCENARIO = 'future scenario layers'
    ANALYSIS_RESULTS = 'analysis results'
