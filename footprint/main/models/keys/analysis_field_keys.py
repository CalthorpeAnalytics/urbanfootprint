
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


class AnalysisFieldKeys(object):

    DENSITY_FIELD_MAP = {
            'pop': ['population'],
            'hh': ['household'],
            'du': ['dwelling_units'],
            'detsf_ll': ['single_family_large_lot'],
            'detsf_sl': ['single_family_small_lot'],
            'attsf': ['attached_single_family_density'],
            'mf': ['multifamily_2_to_4', 'multifamily_5_plus'],
            'mf2to4': ['multifamily_2_to_4'],
            'mf5p': ['multifamily_5p'],
            'emp': ['employment'],
            'emp_ret': ['retail'],
            'emp_retail_services': ['retail_services'],
            'emp_accommodation': ['accomodation'],
            'emp_arts_entertainment': ['arts_entertainment'],
            'emp_other_services': ['other_services'],
            'emp_off': ['office_density'],
            'emp_office_services': ['office_services'],
            'emp_education': ['education_services'],
            'emp_public_admin': ['public_admin'],
            'emp_medical_services': ['medical_services'],
            'emp_ind': ['industrial'],
            'emp_wholesale': ['wholesale'],
            'emp_transport_warehousing': ['transport_warehouse'],
            'emp_manufacturing': ['manufacturing'],
            'emp_construction_utilities': ['construction_utilities'],
            'emp_ag': ['agricultural'],
            'emp_agriculture': ['agriculture'],
            'emp_extraction': ['extraction'],
            'emp_military': ['armed_forces']
        }

    ACRES_PARCEL_MAP = {
        'acres_parcel': None,
        'acres_parcel_res': 'acres_parcel_residential',
        'acres_parcel_res_detsf_ll': 'acres_parcel_residential_single_family_large_lot',
        'acres_parcel_res_detsf_sl': 'acres_parcel_residential_single_family_small_lot',
        'acres_parcel_res_attsf': 'acres_parcel_residential_attached_single_family',
        'acres_parcel_res_mf': 'acres_parcel_residential_multifamily',
        'acres_parcel_emp': 'acres_parcel_employment',
        'acres_parcel_emp_ret': 'acres_parcel_employment_retail',
        'acres_parcel_emp_off': 'acres_parcel_employment_office',
        'acres_parcel_emp_ind': 'acres_parcel_employment_industrial',
        'acres_parcel_emp_ag': 'acres_parcel_employment_agriculture',
        'acres_parcel_emp_mixed': 'acres_parcel_employment_mixed',
        'acres_parcel_mixed': 'acres_parcel_mixed_use',
        'acres_parcel_mixed_w_off': 'acres_parcel_mixed_use_with_office',
        'acres_parcel_mixed_no_off': 'acres_parcel_mixed_use_no_office',
        'acres_parcel_no_use': None,
    }

    BUILDING_SQUARE_FOOTAGE_MAP = {
        'bldg_sqft_detsf_ll': 'building_sqft_single_family_large_lot',
        'bldg_sqft_detsf_sl': 'building_sqft_single_family_small_lot',
        'bldg_sqft_attsf': 'building_square_feet_attached_single_family',
        'bldg_sqft_mf': ['']

    }
    attributes = [

            'pop',
            'hh',
            'du',
            'du_detsf_ll',
            'du_detsf_sl',
            'du_detsf',
            'du_attsf',
            'du_mf',
            'du_mf2to4',
            'du_mf5p',
            'emp',
            'emp_ret',
            'emp_retail_services',
            'emp_restaurant',
            'emp_accomodation',
            'emp_arts_entertainment',
            'emp_other_services',
            'emp_off',
            'emp_office_services',
            'emp_education',
            'emp_public_admin',
            'emp_medical_services',
            'emp_ind',
            'emp_wholesale',
            'emp_transport_warehousing',
            'emp_manufacturing',
            'emp_construction_utilities',
            'emp_ag',
            'emp_agriculture',
            'emp_extraction',
            'emp_military',
            'bldg_sqft_detsf_ll',
            'bldg_sqft_detsf_sl',
            'bldg_sqft_attsf',
            'bldg_sqft_mf',
            'bldg_sqft_retail_services',
            'building_sqft_restaurant',
            'building_sqft_accommodation',
            'bldg_sqft_arts_entertainment',
            'bldg_sqft_other_services',
            'bldg_sqft_office_services',
            'bldg_sqft_public_admin',
            'bldg_sqft_medical_services',
            'bldg_sqft_education',
            'bldg_sqft_wholesale',
            'bldg_sqft_transport_warehousing',
            'commercial_irrigated_sqft',
            'residential_irrigated_sqft'
        ]
