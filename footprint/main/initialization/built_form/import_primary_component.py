
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

from csvImporter.fields import CharField, FloatField, IntegerField
from csvImporter.model import CsvModel

__author__ = 'calthorpe_analytics'

class ImportPrimaryComponent(CsvModel):
# id
    id = IntegerField(prepare=lambda x: x or 0)
    #source,hyperlink,building_type,
    source = CharField(prepare=lambda x: x or '')
    website = CharField(prepare=lambda x: x or '')
    placetype_component = CharField(prepare=lambda x: x or '')
    #building,household_size,
    name = CharField(prepare=lambda x: x or '')
    address = CharField(prepare=lambda x: x or '')

    vacancy_rate = FloatField(prepare=lambda x: x or 0)
    household_size = FloatField(prepare=lambda x: x or 0)

#Pct_SF_Large_Lot,Pct_SF_Small_Lot,Pct_Attached_SF,Pct_MF_2_to_4,Pct_MF_5_Plus,
    percent_detached_single_family = FloatField(prepare=lambda x: x or 0)
    percent_attached_single_family = FloatField(prepare=lambda x: x or 0)
    percent_multifamily_2_to_4 = FloatField(prepare=lambda x: x or 0)
    percent_multifamily_5_plus = FloatField(prepare=lambda x: x or 0)

# Pct_Emp_Office_Svc,Pct_Educ_Svc,Pct_Medical_Svc,Pct_Public_Admin,
    percent_office_services = FloatField(prepare=lambda x: x or 0)
    percent_education_services = FloatField(prepare=lambda x: x or 0)
    percent_medical_services = FloatField(prepare=lambda x: x or 0)
    percent_public_admin = FloatField(prepare=lambda x: x or 0)

#Pct_Retail_Svc,Pct_Restuarant,Pct_Accommodation,Pct_Arts_Entertainment,Pct_Other_Svc,
    percent_retail_services = FloatField(prepare=lambda x: x or 0)
    percent_restaurant = FloatField(prepare=lambda x: x or 0)
    percent_accommodation = FloatField(prepare=lambda x: x or 0)
    percent_arts_entertainment = FloatField(prepare=lambda x: x or 0)
    percent_other_services = FloatField(prepare=lambda x: x or 0)

# Pct_Manufacturing,Pct_Transport_warehouse,Pct_Wholesale,Pct_Construction_Util,Pct_Agriculture,Pct_Extraction,
    percent_manufacturing = FloatField(prepare=lambda x: x or 0)
    percent_transport_warehouse = FloatField(prepare=lambda x: x or 0)
    percent_wholesale = FloatField(prepare=lambda x: x or 0)
    percent_construction_utilities = FloatField(prepare=lambda x: x or 0)

    percent_agriculture = FloatField(prepare=lambda x: x or 0)
    percent_extraction = FloatField(prepare=lambda x: x or 0)

# Pct_ArmedForces,Pct_Military
    percent_military = FloatField(prepare=lambda x: x or 0)
# percent_of_building_type,floors,percent_residential,percent_retail,percent_office,percent_industrial,
    percent_of_placetype_component = FloatField(prepare=lambda x: x or 0)
    lot_size_square_feet = FloatField(prepare=lambda x: x or 0)
    floors = FloatField(prepare=lambda x: x or 0)

#total_far,parking_spaces,parking_structure_square_feet,residential_efficiency,residential_lot_square_feet,square_feet_per_du,
    total_far = FloatField(prepare=lambda x: x or 0)

#residential efficiency
    residential_efficiency = FloatField(prepare=lambda x: x or 0)
    residential_square_feet_per_unit = FloatField(prepare=lambda x: x or 0)

# retail_efficiency,retail_square_feet_per_employee,office_efficiency,office_square_feet_per_employee,
    retail_efficiency = FloatField(prepare=lambda x: x or 0)
    retail_square_feet_per_unit = FloatField(prepare=lambda x: x or 0)
#office efficiency, etc.
    office_efficiency = FloatField(prepare=lambda x: x or 0)
    office_square_feet_per_unit = FloatField(prepare=lambda x: x or 0)

#industrial_efficiency,industrial_square_feet_per_employee,
    industrial_efficiency = FloatField(prepare=lambda x: x or 0)
    industrial_square_feet_per_unit = FloatField(prepare=lambda x: x or 0)

    average_parking_space_square_feet = FloatField(prepare=lambda x: x or 0)
    surface_parking_spaces = FloatField(prepare=lambda x: x or 0)
    above_ground_parking_spaces = FloatField(prepare=lambda x: x or 0)
    below_ground_parking_spaces = FloatField(prepare=lambda x: x or 0)

    building_footprint_square_feet = FloatField(prepare=lambda x: x or 0)
    surface_parking_square_feet = FloatField(prepare=lambda x: x or 0)
    hardscape_other_square_feet = FloatField(prepare=lambda x: x or 0)

    irrigated_softscape_square_feet = FloatField(prepare=lambda x: x or 0)
    nonirrigated_softscape_square_feet = FloatField(prepare=lambda x: x or 0)

    irrigated_percent = FloatField(prepare=lambda x: x or 0)

    id2 = IntegerField(prepare=lambda x: x or 0)

    class Meta:
        delimiter = ","
        has_header = True
