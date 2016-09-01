
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


class PhGridOutcomesFeature(Feature):
    """
    A class of geographic features containing the outcomes of the Public Health analyses at the 150m grid scale
    """
    objects = GeoInheritanceManager()

    hh = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_adult = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_adult_high = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_adult_med = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_adult_low = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_senior = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_teen = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    pop_children = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    adult_all_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_bike_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_walk_tr_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_walk_le_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_mod_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_vig_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_bmi = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_high_bp = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_heart_dis = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_dia_type2 = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_all_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    adult_low_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_bike_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_walk_tr_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_walk_le_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_mod_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_vig_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_bmi = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_high_bp = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_heart_dis = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_dia_type2 = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_low_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    adult_med_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_bike_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_walk_tr_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_walk_le_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_mod_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_vig_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_bmi = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_high_bp = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_heart_dis = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_dia_type2 = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_med_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    adult_high_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_bike_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_walk_tr_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_walk_le_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_mod_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_vig_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_bmi = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_high_bp = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_heart_dis = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_dia_type2 = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    adult_high_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    seniors_all_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_walk_tr_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_walk_le_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_mod_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_vig_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_bmi = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_high_bp = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_heart_dis = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_dia_type2 = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    seniors_all_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    teens_all_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_pa60_daysperweek = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_walkfrom_any = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_bmipct = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    teens_all_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    children_all_walk_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_auto_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_rec_pa_minutes = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_pa60_daysperweek = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_walkfrom_any = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_bmipct = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_overweight = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_obese = models.DecimalField(decimal_places=8, max_digits=20, default=0)
    children_all_gh_poor = models.DecimalField(decimal_places=8, max_digits=20, default=0)

    class Meta(object):
        app_label = 'main'
        abstract = True
