
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

from footprint.client.configuration.fixture import LandUseSymbologyFixture

__author__ = 'calthorpe_analytics'


class SacogLandUseSymbology(LandUseSymbologyFixture):
    """
    a resource for translating SACOG's land uses into UF Built Forms
    """

    def land_use_color_lookup(self):
        return {
            "Very High Density Attached Residential": '#993300',
            "Medium-High Density Attached Residential": '#F27900',
            "Medium Density Attached Residential": '#FF9900',
            "High Density Attached Residential": '#CC6600',
            "Urban Attached Residential": '#7A2900',


            "Very Low Density Detached Residential": "#FFFFCC",
            "Low Density Detached Residential": "#FFFF00",
            "Medium Density Detached Residential": '#FABF8F',
            "Medium-High Density Detached Residential": '#FFCC66',

            "LARGE LOT NOT FARM HOME": "#FFFFCC",
            "Rural Residential": "#FFFFCC",
            "Farm Home": "#99FF99",

            "Mobile Home Park": "#FF6600",

            "Moderate-Intensity Office": '#FF99CC',
            "High-Intensity Office": '#FF66CC',
            "CBD Office": '#FF3399',

            "Light Industrial-Office": '#CC99FF',

            "Medical Facility": '#404040',

            "Agriculture": "#948A54",
            "Agricultural Employment": "#948A54",

            "Residential/Retail Mixed Use Low": '#66CCFF',
            "Residential/Retail Mixed Use High": '#3399FF',
            "High-Rise Mixed Use": "#66FFFF",
            "Mid-Rise Mixed Use": "#00FFFF",
            "Urban Mid-Rise Residential": "#009999",

            "Hotel": '#963634',
            "Regional Retail": "#CC0000",
            "Regional Commercial/Office": '#800000',

            "Heavy Industrial": '#9900CC',
            "Light Industrial": '#9933FF',

            "K-12 School": '#808080',
            "Colleges and Universities": '#595959',
            "UC DAVIS": '#595959',

            "Civic/Institution": '#BFBFBF',
            "Public/Quasi-Public": '#D9D9D9',

            "Community/Neighborhood Retail": '#FB3300',
            "Community/Neighborhood Commercial": '#FF0000',
            "Community/Neighborhood Commercial/Office": '#FF0000',

            "Parking Lot": '#C4BD97',
            "Parking Structure": '#948A54',
            "Parking Structure w/Ground Floor Retail": "#494529",

            "Agricultural Processing/Retail Employment": "#948A54",
            "Park and/or Open Space": '#92D050',
            "Airport": "#262626",

            "Military": "#CCCCFF",

            "Blank Place Type": None,
            "Water": None,
            "Roads": None,
            "Urban Reserve": None,
        }
