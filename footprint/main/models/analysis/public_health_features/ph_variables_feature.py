
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

from django.contrib.gis.db import models
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.geospatial.feature import Feature


__author__ = 'calthorpe_analytics'



class PhVariablesFeature(Feature):
    """
    A full-coverage grid that gathers attributes from the pre-processed grid and the scenario-dependent grid
    """
    objects = GeoInheritanceManager()

    pop = models.FloatField(default=0)
    pop_children = models.FloatField(default=0)
    pop_teen = models.FloatField(default=0)
    pop_adult = models.FloatField(default=0)
    pop_senior = models.FloatField(default=0)

    pop_adult_low = models.FloatField(default=0)
    pop_adult_med = models.FloatField(default=0)
    pop_adult_high = models.FloatField(default=0)

    hh = models.FloatField(default=0)

    gender2 = models.FloatField(default=0)

    age_children = models.FloatField(default=0)
    age_teens = models.FloatField(default=0)
    age_adult = models.FloatField(default=0)
    age_seniors = models.FloatField(default=0)

    racehisp1 = models.FloatField(default=0)
    racehisp2 = models.FloatField(default=0)
    racehisp4 = models.FloatField(default=0)
    racehisp97 = models.FloatField(default=0)
    emply2 = models.FloatField(default=0)
    educa2 = models.FloatField(default=0)
    educa3 = models.FloatField(default=0)
    educa4 = models.FloatField(default=0)
    educa5 = models.FloatField(default=0)
    own2 = models.FloatField(default=0)
    hhsize = models.FloatField(default=0)
    hhveh = models.FloatField(default=0)
    incom2 = models.FloatField(default=0)
    incom3 = models.FloatField(default=0)
    incom4 = models.FloatField(default=0)
    incom5 = models.FloatField(default=0)
    incom6 = models.FloatField(default=0)
    incom7 = models.FloatField(default=0)
    child_any1 = models.FloatField(default=0)

    disabled1_children = models.FloatField(default=0)
    disabled2_children = models.FloatField(default=0)
    disabled1_teens = models.FloatField(default=0)
    disabled2_teens = models.FloatField(default=0)
    disabled1_adult = models.FloatField(default=0)
    disabled2_adult = models.FloatField(default=0)
    disabled1_seniors = models.FloatField(default=0)
    disabled2_seniors = models.FloatField(default=0)

    pop_age_children = models.FloatField(default=0)
    pop_age_teens = models.FloatField(default=0)
    pop_age_adult = models.FloatField(default=0)
    pop_age_seniors = models.FloatField(default=0)

    emply_hh = models.FloatField(default=0)
    educa_hh2 = models.FloatField(default=0)
    educa_hh3 = models.FloatField(default=0)
    educa_hh4 = models.FloatField(default=0)
    educa_hh5 = models.FloatField(default=0)

    bldg_sqft_res = models.FloatField(default=0)
    bldg_sqft_ret1 = models.FloatField(default=0)
    bldg_sqft_off = models.FloatField(default=0)
    b1 = models.FloatField(default=0)
    b2 = models.FloatField(default=0)
    b3 = models.FloatField(default=0)
    b4 = models.FloatField(default=0)
    b5 = models.FloatField(default=0)
    a = models.FloatField(default=0)
    du_1km_tr = models.FloatField(default=0)
    resmix_dens = models.FloatField(default=0)
    bldg_sqft_ret = models.FloatField(default=0)
    far_nonres = models.FloatField(default=0)
    mix5 = models.FloatField(default=0)
    rail_any = models.FloatField(default=0)
    transit_distance = models.FloatField(default=0)
    transit_count = models.FloatField(default=0)
    school_distance = models.FloatField(default=0)
    retail_distance = models.FloatField(default=0)
    restaurant_distance = models.FloatField(default=0)
    intersection_density_sqmi = models.FloatField(default=0)
    local_street = models.FloatField(default=0)
    major_street = models.FloatField(default=0)
    freeway_arterial_any = models.FloatField(default=0)
    park_open_space_distance = models.FloatField(default=0)
    acres_parcel_park_open_space = models.FloatField(default=0)
    du_variable = models.FloatField(default=0)
    emp_variable = models.FloatField(default=0)

    res_index = models.FloatField(default=0)
    com_index = models.FloatField(default=0)
    park_access = models.FloatField(default=0)
    regional_access = models.FloatField(default=0)
    network_index = models.FloatField(default=0)
    transit_access = models.FloatField(default=0)
    major_road_index = models.FloatField(default=0)

    walk_index = models.FloatField(default=0)
    walk_index_chts_senior_walk_any = models.FloatField(default=0)
    walk_index_chts_senior_auto_min = models.FloatField(default=0)
    walk_index_chts_teens_walk_any = models.FloatField(default=0)
    walk_index_chts_child_walk_any = models.FloatField(default=0)
    walk_index_chts_adult_bike_any = models.FloatField(default=0)
    walk_index_chts_adult_walk_min = models.FloatField(default=0)
    walk_index_chts_senior_walk_min = models.FloatField(default=0)
    walk_index_chts_teens_walk_min = models.FloatField(default=0)
    walk_index_chts_adult_auto_min = models.FloatField(default=0)
    walk_index_chis_adult_modpa_any = models.FloatField(default=0)
    walk_index_chis_adult_overweight = models.FloatField(default=0)
    walk_index_chis_senior_overweight = models.FloatField(default=0)
    walk_index_chis_adult_obese = models.FloatField(default=0)
    walk_index_chis_senior_gh = models.FloatField(default=0)
    walk_index_chis_senior_walk_le_min = models.FloatField(default=0)
    walk_index_chis_adult_modpa_min = models.FloatField(default=0)
    walk_index_chis_adult_bmi = models.FloatField(default=0)
    walk_index_chis_child_pa60 = models.FloatField(default=0)
    walk_index_chis_child_walk_school = models.FloatField(default=0)

    class Meta(object):
        app_label = 'main'
        abstract = True
