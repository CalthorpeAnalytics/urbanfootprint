
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

from decimal import Decimal
from footprint.main.lib.functions import map_to_dict
from footprint.main.models.analysis_module.core_module.core_revert_to_base_condition import \
    core_end_state_revert_to_base_condition
from footprint.main.models.built_form.flat_built_form import FlatBuiltForm
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey

import logging

__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)


def calculate_land_development_category(feature):

    if feature.intersection_density_sqmi >= 150 and feature.emp / feature.acres_gross > 70:
        land_development_category = 'urban'

    elif feature.intersection_density_sqmi >= 150 and feature.du / feature.acres_gross > 45:
        land_development_category = 'urban'

    elif feature.intersection_density_sqmi >= 150 and feature.emp / feature.acres_gross <= 70:
        land_development_category = 'compact'

    elif feature.intersection_density_sqmi >= 150 and feature.du / feature.acres_gross <= 45:
        land_development_category = 'compact'

    elif feature.intersection_density_sqmi < 150:
        land_development_category = 'standard'
    else:
        land_development_category = None

    feature.land_development_category = land_development_category
    feature.save()



def update_future_scenario(config_entity, annotated_features):
    base_class = config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)

    logger.info("annotating features for {0}".format(config_entity))

    flat_built_forms = map_to_dict(
        lambda flat_built_form: [flat_built_form.built_form_id, flat_built_form],
        FlatBuiltForm.objects.filter(built_form_id__in=map(lambda feature: feature.built_form.id,
                                                           filter(lambda feature: feature.built_form, annotated_features)))
    )
    logger.info("processing {0} future scenario features".format(len(annotated_features)))
    for update_feature in annotated_features:
        base = base_class.objects.get(id=update_feature.base_canvas)
        flat_built_form = flat_built_forms.get(update_feature.built_form.id, FlatBuiltForm()) if update_feature.built_form else FlatBuiltForm()

        if not update_feature.built_form_id:
            # If the user reverted the built_form, it will be null and we need to set it to the base built_form
            core_end_state_revert_to_base_condition(update_feature, base)
            continue

        applied_acres = update_feature.acres_developable * update_feature.dev_pct * update_feature.gross_net_pct

        density_adjusted_acres = applied_acres * update_feature.density_pct
        remaining_development = (1 - update_feature.dev_pct)

        update_feature.built_form_key = flat_built_form.key
        update_feature.built_form_base = base.built_form_key

        update_feature.intersection_density_sqmi = flat_built_form.intersection_density * update_feature.dev_pct * \
            update_feature.gross_net_pct * update_feature.density_pct

        update_feature.acres_parcel_res = flat_built_form.acres_parcel_residential * applied_acres + remaining_development \
            * update_feature.acres_parcel_res

        update_feature.acres_parcel_emp = flat_built_form.acres_parcel_employment * applied_acres + remaining_development \
            * update_feature.acres_parcel_emp

        update_feature.acres_parcel_mixed_use = flat_built_form.acres_parcel_mixed_use * applied_acres + \
           remaining_development * update_feature.acres_parcel_mixed_use

        update_feature.acres_parcel_no_use = update_feature.acres_developable - applied_acres if update_feature.clear_flag is True else \
            (update_feature.acres_developable - applied_acres) + remaining_development * update_feature.acres_parcel_no_use

        update_feature.acres_parcel = update_feature.acres_parcel_res + update_feature.acres_parcel_emp + \
                                 update_feature.acres_parcel_mixed_use + update_feature.acres_parcel_no_use

        update_feature.pop = flat_built_form.population_density * density_adjusted_acres + remaining_development * update_feature.pop

        update_feature.hh = flat_built_form.household_density * density_adjusted_acres + remaining_development * update_feature.hh

        update_feature.du = flat_built_form.dwelling_unit_density * density_adjusted_acres + remaining_development * update_feature.du

        update_feature.du_detsf_ll = flat_built_form.single_family_large_lot_density * density_adjusted_acres + \
                                remaining_development * update_feature.du_detsf_ll

        update_feature.du_detsf_sl = flat_built_form.single_family_small_lot_density * density_adjusted_acres + \
                                remaining_development * update_feature.du_detsf_sl

        update_feature.du_detsf = update_feature.du_detsf_sl + update_feature.du_detsf_ll

        update_feature.du_attsf = flat_built_form.attached_single_family_density * density_adjusted_acres + \
                             remaining_development * update_feature.du_attsf

        update_feature.du_mf2to4 = flat_built_form.multifamily_2_to_4_density * density_adjusted_acres + remaining_development * update_feature.du_mf2to4
        update_feature.du_mf5p = flat_built_form.multifamily_5_plus_density * density_adjusted_acres + remaining_development * update_feature.du_mf5p

        update_feature.du_mf = update_feature.du_mf2to4 + update_feature.du_mf5p

        update_feature.emp = flat_built_form.employment_density * density_adjusted_acres + remaining_development * update_feature.emp
        update_feature.emp_ret = flat_built_form.retail_density * density_adjusted_acres + remaining_development * update_feature.emp_ret

        update_feature.emp_off = (flat_built_form.office_services_density + flat_built_form.medical_services_density) * density_adjusted_acres + remaining_development * update_feature.emp_off
        update_feature.emp_pub = (flat_built_form.education_services_density + flat_built_form.public_admin_density) * density_adjusted_acres + remaining_development * update_feature.emp_pub

        update_feature.emp_ind = flat_built_form.industrial_density * density_adjusted_acres + remaining_development * update_feature.emp_ind
        update_feature.emp_ag = flat_built_form.agricultural_density * density_adjusted_acres + remaining_development * update_feature.emp_ag
        update_feature.emp_military = flat_built_form.military_density * density_adjusted_acres + remaining_development * update_feature.emp_military

        update_feature.emp_retail_services = flat_built_form.retail_services_density * density_adjusted_acres + remaining_development * update_feature.emp_retail_services

        update_feature.emp_restaurant = flat_built_form.restaurant_density * density_adjusted_acres + remaining_development * update_feature.emp_restaurant

        update_feature.emp_accommodation = flat_built_form.accommodation_density * density_adjusted_acres + remaining_development * update_feature.emp_accommodation

        update_feature.emp_arts_entertainment = flat_built_form.arts_entertainment_density * density_adjusted_acres + \
                                                remaining_development * update_feature.emp_arts_entertainment

        update_feature.emp_other_services = flat_built_form.other_services_density * density_adjusted_acres + \
                                            remaining_development * update_feature.emp_other_services

        update_feature.emp_office_services = flat_built_form.office_services_density * density_adjusted_acres + \
                                             remaining_development * update_feature.emp_office_services

        update_feature.emp_medical_services = flat_built_form.medical_services_density * density_adjusted_acres + \
                                              remaining_development * update_feature.emp_medical_services

        update_feature.emp_education = flat_built_form.education_services_density * density_adjusted_acres + \
                                       remaining_development * update_feature.emp_education
        update_feature.emp_public_admin = flat_built_form.public_admin_density * density_adjusted_acres + \
                                          remaining_development * update_feature.emp_public_admin

        update_feature.emp_wholesale = flat_built_form.wholesale_density * density_adjusted_acres + \
                                       remaining_development * update_feature.emp_wholesale
        update_feature.emp_transport_warehousing = flat_built_form.transport_warehouse_density * density_adjusted_acres + \
                                                   remaining_development * update_feature.emp_transport_warehousing
        update_feature.emp_manufacturing = flat_built_form.manufacturing_density * density_adjusted_acres + remaining_development * update_feature.emp_manufacturing
        update_feature.emp_construction = flat_built_form.construction_utilities_density * Decimal(0.5) * density_adjusted_acres + remaining_development * update_feature.emp_construction
        update_feature.emp_utilities = flat_built_form.construction_utilities_density * Decimal(0.5) * density_adjusted_acres + remaining_development * update_feature.emp_utilities

        update_feature.emp_agriculture = flat_built_form.agriculture_density * density_adjusted_acres + remaining_development * update_feature.emp_agriculture
        update_feature.emp_extraction = flat_built_form.extraction_density * density_adjusted_acres + remaining_development * update_feature.emp_extraction

        update_feature.bldg_sqft_detsf_ll = flat_built_form.building_sqft_single_family_large_lot * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_detsf_ll
        update_feature.bldg_sqft_detsf_sl = flat_built_form.building_sqft_single_family_small_lot * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_detsf_sl
        update_feature.bldg_sqft_attsf = flat_built_form.building_sqft_attached_single_family * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_attsf
        update_feature.bldg_sqft_mf = (flat_built_form.building_sqft_multifamily_2_to_4 + flat_built_form.building_sqft_multifamily_5_plus) * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_mf
        update_feature.bldg_sqft_retail_services = flat_built_form.building_sqft_retail_services * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_retail_services
        update_feature.bldg_sqft_restaurant = flat_built_form.building_sqft_restaurant * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_restaurant
        update_feature.bldg_sqft_accommodation = flat_built_form.building_sqft_accommodation * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_accommodation
        update_feature.bldg_sqft_arts_entertainment = flat_built_form.building_sqft_arts_entertainment * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_arts_entertainment
        update_feature.bldg_sqft_other_services = flat_built_form.building_sqft_other_services * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_other_services
        update_feature.bldg_sqft_office_services = flat_built_form.building_sqft_office_services * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_office_services
        update_feature.bldg_sqft_public_admin = flat_built_form.building_sqft_public_admin * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_public_admin
        update_feature.bldg_sqft_medical_services = flat_built_form.building_sqft_medical_services * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_medical_services
        update_feature.bldg_sqft_education = flat_built_form.building_sqft_education_services * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_education
        update_feature.bldg_sqft_wholesale = flat_built_form.building_sqft_wholesale * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_wholesale
        update_feature.bldg_sqft_transport_warehousing = flat_built_form.building_sqft_transport_warehouse * density_adjusted_acres + remaining_development * update_feature.bldg_sqft_transport_warehousing

        update_feature.commercial_irrigated_sqft = flat_built_form.commercial_irrigated_square_feet * density_adjusted_acres + remaining_development * update_feature.commercial_irrigated_sqft
        update_feature.residential_irrigated_sqft = flat_built_form.residential_irrigated_square_feet * density_adjusted_acres + remaining_development * update_feature.residential_irrigated_sqft

        update_feature.acres_parcel_res_detsf_ll = flat_built_form.acres_parcel_residential_single_family_large_lot * applied_acres + remaining_development * update_feature.acres_parcel_res_detsf_ll
        update_feature.acres_parcel_res_detsf_sl = flat_built_form.acres_parcel_residential_single_family_small_lot * applied_acres + remaining_development * update_feature.acres_parcel_res_detsf_sl
        update_feature.acres_parcel_res_attsf = flat_built_form.acres_parcel_residential_attached_single_family * applied_acres + remaining_development * update_feature.acres_parcel_res_attsf
        update_feature.acres_parcel_res_mf = flat_built_form.acres_parcel_residential_multifamily * applied_acres + remaining_development * update_feature.acres_parcel_res_mf

        update_feature.acres_parcel_emp_ret = flat_built_form.acres_parcel_employment_retail * applied_acres + remaining_development * update_feature.acres_parcel_emp_ret
        update_feature.acres_parcel_emp_off = flat_built_form.acres_parcel_employment_office * applied_acres + remaining_development * update_feature.acres_parcel_emp_off
        update_feature.acres_parcel_emp_pub = flat_built_form.acres_parcel_employment_public * applied_acres + remaining_development * update_feature.acres_parcel_emp_pub
        update_feature.acres_parcel_emp_ind = flat_built_form.acres_parcel_employment_industrial * applied_acres + remaining_development * update_feature.acres_parcel_emp_ind
        update_feature.acres_parcel_emp_ag = flat_built_form.acres_parcel_employment_agriculture * applied_acres + remaining_development * update_feature.acres_parcel_emp_ag

        update_feature.save()

        calculate_land_development_category(update_feature)
