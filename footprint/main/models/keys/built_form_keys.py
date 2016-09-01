
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


class BuiltFormKeys(object):
    """
    Keys for used by Built Forms
    """

    BUILDING_USE_RESIDENTIAL = 'Residential'
    BUILDING_USE_OFFICE = 'Office'
    BUILDING_USE_RETAIL = 'Retail'
    BUILDING_USE_INDUSTRIAL = 'Industrial'

    INFRASTRUCTURE_STREET = PLACETYPE_COMPONENT_STREET = 'Street'
    INFRASTRUCTURE_UTILITIES = PLACETYPE_COMPONENT_UTILITY = 'Utility'
    INFRASTRUCTURE_PARK = PLACETYPE_COMPONENT_PARK = 'Park'
    INFRASTRUCTURE_TYPES = [INFRASTRUCTURE_STREET, INFRASTRUCTURE_UTILITIES, INFRASTRUCTURE_PARK]

    BUILDINGTYPE_CIVIC = 'Civic'
    BUILDINGTYPE_RESIDENTIAL = 'Residential'
    BUILDINGTYPE_DETACHED_RESIDENTIAL = 'Detached Residential'
    BUILDINGTYPE_ATTACHED_AND_MULTIFAMILY = 'Attached and Multifamily Residential'
    BUILDINGTYPE_OFFICE_INDUSTRIAL = 'Office/Industrial'
    BUILDINGTYPE_COMMERCIAL_RETAIL = 'Commercial/Retail'
    BUILDINGTYPE_MIXED_USE = 'Mixed Use'
    BUILDINGTYPE_INSTITUTIONAL = 'Institutional'
    BUILDINGTYPE_BLANK = 'Blank'
    BUILDINGTYPE_AGRICULTURAL = 'Agriculture'


    RESIDENTIAL_BUILDINGTYPE_CATEGORIES = [
        BUILDINGTYPE_RESIDENTIAL, BUILDINGTYPE_DETACHED_RESIDENTIAL,
        BUILDINGTYPE_ATTACHED_AND_MULTIFAMILY, BUILDINGTYPE_MIXED_USE
    ]

    EMPLOYMENT_BUILDINGTYPE_CATEGORIES = [
        BUILDINGTYPE_AGRICULTURAL,
        BUILDINGTYPE_OFFICE_INDUSTRIAL, BUILDINGTYPE_COMMERCIAL_RETAIL, BUILDINGTYPE_INSTITUTIONAL,
        BUILDINGTYPE_CIVIC, BUILDINGTYPE_MIXED_USE
    ]

    NET_COMPONENTS = [BUILDINGTYPE_RESIDENTIAL,
                      BUILDINGTYPE_DETACHED_RESIDENTIAL,
                      BUILDINGTYPE_ATTACHED_AND_MULTIFAMILY,
                      BUILDINGTYPE_OFFICE_INDUSTRIAL,
                      BUILDINGTYPE_COMMERCIAL_RETAIL,
                      BUILDINGTYPE_MIXED_USE,
                      BUILDINGTYPE_INSTITUTIONAL,
                      BUILDINGTYPE_BLANK,
                      BUILDINGTYPE_AGRICULTURAL]

    GROSS_COMPONENTS = INFRASTRUCTURE_TYPES + [BUILDINGTYPE_CIVIC]

    COMPONENT_CATEGORIES = NET_COMPONENTS + GROSS_COMPONENTS

    DETACHED_SINGLE_FAMILY = 'Detached Single Family'
    ATTACHED_SINGLE_FAMILY = 'Attached Single Family'
    MULTIFAMILY_2_TO_4 = 'Multifamily 2 To 4'
    MULTIFAMILY_5P = 'Multifamily 5 Plus'

    LARGE_LOT_SINGLE_FAMILY = 'Single Family Large Lot'
    SMALL_LOT_SINGLE_FAMILY = 'Single Family Small Lot'

    RESIDENTIAL_SUBCATEGORIES = [DETACHED_SINGLE_FAMILY, ATTACHED_SINGLE_FAMILY, MULTIFAMILY_2_TO_4, MULTIFAMILY_5P]
    DETACHED_SINGLE_FAMILY_SUBCATEGORIES = [LARGE_LOT_SINGLE_FAMILY, SMALL_LOT_SINGLE_FAMILY]

    RESIDENTIAL_CATEGORY = 'Residential'
    RETAIL_CATEGORY = 'Retail'
    OFFICE_CATEGORY = 'Office'
    PUBLIC_CATEGORY = 'Public'
    INDUSTRIAL_CATEGORY = 'Industrial'
    AGRICULTURE_CATEGORY = 'Agriculture'
    MILITARY_CATEGORY = 'Military'


    TOP_LEVEL_EMPLOYMENT_CATEGORIES = [RETAIL_CATEGORY,
                                       OFFICE_CATEGORY,
                                       INDUSTRIAL_CATEGORY]

    RETAIL_SUBCATEGORIES = [
        'Retail Services',
        'Restaurant',
        'Accommodation',
        'Arts Entertainment',
        'Other Services'
    ]

    OFFICE_SUBCATEGORIES = [
        'Office Services',
        'Medical Services',
        'Public Admin',
        'Education Services'
    ]

    INDUSTRIAL_SUBCATEGORIES = [
        'Manufacturing',
        'Wholesale',
        'Transport Warehouse',
        'Construction Utilities',
        'Agriculture',
        'Extraction',
        'Military'
    ]


    COMMERCIAL_SUBCATEGORIES = RETAIL_SUBCATEGORIES + OFFICE_SUBCATEGORIES + \
                               INDUSTRIAL_SUBCATEGORIES

    BUILDING_USE_DEFINITION_METACATEGORIES = [
        RESIDENTIAL_CATEGORY,
        OFFICE_CATEGORY,
        RETAIL_CATEGORY,
        INDUSTRIAL_CATEGORY
    ]

    BUILDING_USE_DEFINITION_CATEGORIES = {
        'Retail Services': RETAIL_CATEGORY,
        'Restaurant': RETAIL_CATEGORY,
        'Accommodation': RETAIL_CATEGORY,
        'Arts Entertainment': RETAIL_CATEGORY,
        'Other Services': RETAIL_CATEGORY,

        'Office Services': OFFICE_CATEGORY,
        'Medical Services': OFFICE_CATEGORY,

        'Public Admin': PUBLIC_CATEGORY,
        'Education Services': PUBLIC_CATEGORY,

        'Manufacturing': INDUSTRIAL_CATEGORY,
        'Wholesale': INDUSTRIAL_CATEGORY,
        'Transport Warehouse': INDUSTRIAL_CATEGORY,
        'Construction Utilities': INDUSTRIAL_CATEGORY,

        'Agriculture': AGRICULTURE_CATEGORY,
        'Extraction': AGRICULTURE_CATEGORY,
        'Military': MILITARY_CATEGORY,

        DETACHED_SINGLE_FAMILY: RESIDENTIAL_CATEGORY,
        ATTACHED_SINGLE_FAMILY: RESIDENTIAL_CATEGORY,
        MULTIFAMILY_2_TO_4: RESIDENTIAL_CATEGORY,
        MULTIFAMILY_5P: RESIDENTIAL_CATEGORY,
    }
