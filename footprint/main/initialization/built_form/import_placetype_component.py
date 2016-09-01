
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

__author__ = 'calthorpe_analytics'

from csvImporter.fields import CharField, FloatField, IntegerField
from csvImporter.model import CsvModel

__author__ = 'calthorpe_analytics'

class ImportPlacetypeComponent(CsvModel):
#    BTID,Building_Type,
# Urban Mixed Use,Urban Residential,Urban Commercial,City Mixed Use,City Residential,City Commercial,
# Town Mixed Use,Town Residential,Town Commercial,Village Mixed Use,Village Residential,Village Commercial,
# Neighborhood Residential,Neighborhood Low,Office Focus,Mixed Office and R&D,Office/Industrial,Industrial Focus,
# Low-Density Employment Park,High Intensity Activity Center,Mid Intensity Activity Center,
# Low Intensity Retail-Centered N'Hood,Retail: Strip Mall/ Big Box,Industrial/Office/Res Mixed High,
# Industrial/Office/Res Mixed Low,Suburban Multifamily,Suburban Mixed Residential,Residential Subdivision,
# Large Lot Residential Area,Rural Residential,Rural Ranchettes,Rural Employment,Campus/ University,
# Institutional,Parks & Open Space,BuildingType Name,Gross_Net_Flag
    category = CharField(prepare=lambda x: x or '')
    btid = IntegerField(prepare=lambda x: x or 0)
    color = CharField(prepare=lambda x: x or '')
    name = CharField(prepare=lambda x: x or '')
    urban_mixed_use = FloatField(prepare=lambda x: x or 0)
    urban_residential = FloatField(prepare=lambda x: x or 0)
    urban_commercial = FloatField(prepare=lambda x: x or 0)
    city_mixed_use = FloatField(prepare=lambda x: x or 0)
    city_residential = FloatField(prepare=lambda x: x or 0)
    city_commercial = FloatField(prepare=lambda x: x or 0)
    town_mixed_use = FloatField(prepare=lambda x: x or 0)
    town_residential = FloatField(prepare=lambda x: x or 0)
    town_commercial = FloatField(prepare=lambda x: x or 0)
    village_mixed_use = FloatField(prepare=lambda x: x or 0)
    village_residential = FloatField(prepare=lambda x: x or 0)
    village_commercial = FloatField(prepare=lambda x: x or 0)
    neighborhood_residential = FloatField(prepare=lambda x: x or 0)
    neighborhood_low = FloatField(prepare=lambda x: x or 0)
    office_focus = FloatField(prepare=lambda x: x or 0)
    mixed_office_and_r_and_d = FloatField(prepare=lambda x: x or 0)
    office_industrial = FloatField(prepare=lambda x: x or 0)
    industrial_focus = FloatField(prepare=lambda x: x or 0)
    low_density_employment_park = FloatField(prepare=lambda x: x or 0)
    high_intensity_activity_center = FloatField(prepare=lambda x: x or 0)
    mid_intensity_activity_center = FloatField(prepare=lambda x: x or 0)
    low_intensity_retail_centered_neighborhood = FloatField(prepare=lambda x: x or 0)
    retail_strip_mall_big_box = FloatField(prepare=lambda x: x or 0)
    industrial_office_residential_mixed_high = FloatField(prepare=lambda x: x or 0)
    industrial_office_residential_mixed_low = FloatField(prepare=lambda x: x or 0)
    suburban_multifamily = FloatField(prepare=lambda x: x or 0)
    suburban_mixed_residential = FloatField(prepare=lambda x: x or 0)
    residential_subdivision = FloatField(prepare=lambda x: x or 0)
    large_lot_residential = FloatField(prepare=lambda x: x or 0)
    rural_residential = FloatField(prepare=lambda x: x or 0)
    rural_ranchettes = FloatField(prepare=lambda x: x or 0)
    rural_employment = FloatField(prepare=lambda x: x or 0)
    campus_or_university = FloatField(prepare=lambda x: x or 0)
    institutional = FloatField(prepare=lambda x: x or 0)
    parks_and_open_space = FloatField(prepare=lambda x: x or 0)

    class Meta:
        delimiter = ","
        has_header = True
