
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

from footprint.main.models.analysis_module.core_module.core_revert_to_base_condition import core_increment_revert_to_base_condition
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey

__author__ = 'calthorpe_analytics'


def update_increment_feature(config_entity, annotated_features):

    base_class = config_entity.db_entity_feature_class(DbEntityKey.BASE_CANVAS)
    increment_class = config_entity.db_entity_feature_class(DbEntityKey.INCREMENT)

    for feature in annotated_features:
        increment = increment_class.objects.get(id=feature.scenario_increment)
        base = base_class.objects.get(id=feature.base_canvas)

        if not feature.built_form_base:
            # If the user reverted the built_form, it will be null and we need to set it to the base built_form
            core_increment_revert_to_base_condition(increment)
            continue

        increment.built_form_key = feature.built_form_key
        increment.built_form_id = feature.built_form_id
        increment.land_development_category = feature.land_development_category

        increment.pop = feature.pop - base.pop
        increment.hh = feature.hh - base.hh
        increment.du = feature.du - base.du
        increment.emp = feature.emp - base.emp
        increment.du_detsf = feature.du_detsf - base.du_detsf
        increment.du_detsf_ll = feature.du_detsf_ll - base.du_detsf_ll
        increment.du_detsf_sl = feature.du_detsf_sl - base.du_detsf_sl
        increment.du_attsf = feature.du_attsf - base.du_attsf
        increment.du_mf = feature.du_mf - base.du_mf

        increment.emp_ret = feature.emp_ret - base.emp_ret
        increment.emp_retail_services = feature.emp_retail_services - base.emp_retail_services
        increment.emp_restaurant = feature.emp_restaurant - base.emp_restaurant
        increment.emp_accommodation = feature.emp_accommodation - base.emp_accommodation
        increment.emp_arts_entertainment = feature.emp_arts_entertainment - base.emp_arts_entertainment
        increment.emp_other_services = feature.emp_other_services - base.emp_other_services

        increment.emp_off = feature.emp_off - base.emp_off
        increment.emp_office_services = feature.emp_office_services - base.emp_office_services
        increment.emp_medical_services = feature.emp_medical_services - base.emp_medical_services

        increment.emp_pub = feature.emp_pub - base.emp_pub
        increment.emp_education = feature.emp_education - base.emp_education
        increment.emp_public_admin = feature.emp_public_admin - base.emp_public_admin

        increment.emp_ind = feature.emp_ind - base.emp_ind
        increment.emp_wholesale = feature.emp_wholesale - base.emp_wholesale
        increment.emp_transport_warehousing = feature.emp_transport_warehousing - base.emp_transport_warehousing
        increment.emp_manufacturing = feature.emp_manufacturing - base.emp_manufacturing
        increment.emp_utilities = feature.emp_utilities - base.emp_utilities
        increment.emp_construction = feature.emp_construction - base.emp_construction

        increment.emp_ag = feature.emp_ag - base.emp_ag
        increment.emp_agriculture = feature.emp_agriculture - base.emp_agriculture
        increment.emp_extraction = feature.emp_extraction - base.emp_extraction

        increment.emp_military = feature.emp_military - base.emp_military

        increment.save()
