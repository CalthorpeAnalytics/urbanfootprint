
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


from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.geospatial.feature import Feature
from django.db import models
__author__ = 'calthorpe_analytics'


class CensusRatesFeature(Feature):

    objects = GeoInheritanceManager()
    blockgroup = models.CharField(max_length=20)
    tract = models.CharField(max_length=20)
    county_name = models.CharField(max_length=100, null=True, blank=True)

    #hh tenure - owner/renter
    hh_own_occ_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_rent_occ_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #hh by income class as proportion of total hh
    hh_inc_00_10_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_10_20_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_20_30_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_30_40_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_40_50_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_50_60_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_60_75_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_75_100_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_100_125_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_125_150_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_150_200_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    hh_inc_200p_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #avg income per hh - multiply by hh totals to get aggregate income
    hh_agg_inc_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #avg vehicles per hh - multiply by hh to get aggregate vehicles
    hh_agg_veh_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #gender
    pop_female_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_male_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #age categories specified for the PH model
    pop_avg_age5_11 = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_avg_age12_17 = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_avg_age18_64 = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_avg_age65_up = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #age groups to match the PH model age groups
    pop_age_5_11_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age_12_17_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age_18_64_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #standard uf/census age groupings
    pop_age0_4_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age5_9_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age10_14_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age15_17_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age18_19_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age20_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age21_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age22_24_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age25_29_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age30_39_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age40_49_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age50_64_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age65_up_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #legacy age groupings
    pop_age16_up_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age25_up_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #legacy gender categories by age groups
    pop_female_age20_64_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_male_age20_64_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #population educational attainment as proportion of population
    pop_hs_not_comp_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_hs_diploma_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_assoc_some_coll_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_coll_degree_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_grad_degree_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_employed_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_unemployed_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #race proportion of population added for the PH model - this stays constant into any future
    pop_hispanic_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_white_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_black_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_asian_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_american_indian_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_hawaiian_islander_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_other_ethnicity_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #disability rates added for PH model - stay constant into any future
    pop_age5_17_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age5_17_ambulatory_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age18_64_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age18_64_ambulatory_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age65up_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)
    pop_age65up_ambulatory_disability_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    #hh with children under 18 years of age
    hh_with_children_under_18yr_rate = models.DecimalField(max_digits=14, decimal_places=6, default=0)

    class Meta:
        abstract = True
        app_label = 'main'
