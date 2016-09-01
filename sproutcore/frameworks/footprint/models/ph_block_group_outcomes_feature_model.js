/*
 * UrbanFootprint v1.5
 * Copyright (C) 2016 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */


sc_require('models/feature_model');

Footprint.PhBlockGroupOutcomesFeature = Footprint.Feature.extend({

    blockgroup: SC.Record.attr(String),
    tract: SC.Record.attr(String),
    county_name: SC.Record.attr(String),

    hh: SC.Record.attr(Number),
    pop: SC.Record.attr(Number),
    pop_adult: SC.Record.attr(Number),
    pop_adult_high: SC.Record.attr(Number),
    pop_adult_med: SC.Record.attr(Number),
    pop_adult_low: SC.Record.attr(Number),
    pop_senior: SC.Record.attr(Number),
    pop_teen: SC.Record.attr(Number),
    pop_children: SC.Record.attr(Number),

    adult_all_walk_minutes: SC.Record.attr(Number),
    adult_all_bike_minutes: SC.Record.attr(Number),
    adult_all_auto_minutes: SC.Record.attr(Number),
    adult_all_rec_pa_minutes: SC.Record.attr(Number),
    adult_all_walk_tr_minutes: SC.Record.attr(Number),
    adult_all_walk_le_minutes: SC.Record.attr(Number),
    adult_all_mod_pa_minutes: SC.Record.attr(Number),
    adult_all_vig_pa_minutes: SC.Record.attr(Number),
    adult_all_bmi: SC.Record.attr(Number),
    adult_all_overweight: SC.Record.attr(Number),
    adult_all_obese: SC.Record.attr(Number),
    adult_all_high_bp: SC.Record.attr(Number),
    adult_all_heart_dis: SC.Record.attr(Number),
    adult_all_dia_type2: SC.Record.attr(Number),
    adult_all_gh_poor: SC.Record.attr(Number),

    adult_low_walk_minutes: SC.Record.attr(Number),
    adult_low_bike_minutes: SC.Record.attr(Number),
    adult_low_auto_minutes: SC.Record.attr(Number),
    adult_low_rec_pa_minutes: SC.Record.attr(Number),
    adult_low_walk_tr_minutes: SC.Record.attr(Number),
    adult_low_walk_le_minutes: SC.Record.attr(Number),
    adult_low_mod_pa_minutes: SC.Record.attr(Number),
    adult_low_vig_pa_minutes: SC.Record.attr(Number),
    adult_low_bmi: SC.Record.attr(Number),
    adult_low_overweight: SC.Record.attr(Number),
    adult_low_obese: SC.Record.attr(Number),
    adult_low_high_bp: SC.Record.attr(Number),
    adult_low_heart_dis: SC.Record.attr(Number),
    adult_low_dia_type2: SC.Record.attr(Number),
    adult_low_gh_poor: SC.Record.attr(Number),

    adult_med_walk_minutes: SC.Record.attr(Number),
    adult_med_bike_minutes: SC.Record.attr(Number),
    adult_med_auto_minutes: SC.Record.attr(Number),
    adult_med_rec_pa_minutes: SC.Record.attr(Number),
    adult_med_walk_tr_minutes: SC.Record.attr(Number),
    adult_med_walk_le_minutes: SC.Record.attr(Number),
    adult_med_mod_pa_minutes: SC.Record.attr(Number),
    adult_med_vig_pa_minutes: SC.Record.attr(Number),
    adult_med_bmi: SC.Record.attr(Number),
    adult_med_overweight: SC.Record.attr(Number),
    adult_med_obese: SC.Record.attr(Number),
    adult_med_high_bp: SC.Record.attr(Number),
    adult_med_heart_dis: SC.Record.attr(Number),
    adult_med_dia_type2: SC.Record.attr(Number),
    adult_med_gh_poor: SC.Record.attr(Number),

    adult_high_walk_minutes: SC.Record.attr(Number),
    adult_high_bike_minutes: SC.Record.attr(Number),
    adult_high_auto_minutes: SC.Record.attr(Number),
    adult_high_rec_pa_minutes: SC.Record.attr(Number),
    adult_high_walk_tr_minutes: SC.Record.attr(Number),
    adult_high_walk_le_minutes: SC.Record.attr(Number),
    adult_high_mod_pa_minutes: SC.Record.attr(Number),
    adult_high_vig_pa_minutes: SC.Record.attr(Number),
    adult_high_bmi: SC.Record.attr(Number),
    adult_high_overweight: SC.Record.attr(Number),
    adult_high_obese: SC.Record.attr(Number),
    adult_high_high_bp: SC.Record.attr(Number),
    adult_high_heart_dis: SC.Record.attr(Number),
    adult_high_dia_type2: SC.Record.attr(Number),
    adult_high_gh_poor: SC.Record.attr(Number),

    seniors_all_walk_minutes: SC.Record.attr(Number),
    seniors_all_auto_minutes: SC.Record.attr(Number),
    seniors_all_rec_pa_minutes: SC.Record.attr(Number),
    seniors_all_walk_tr_minutes: SC.Record.attr(Number),
    seniors_all_walk_le_minutes: SC.Record.attr(Number),
    seniors_all_mod_pa_minutes: SC.Record.attr(Number),
    seniors_all_vig_pa_minutes: SC.Record.attr(Number),
    seniors_all_bmi: SC.Record.attr(Number),
    seniors_all_overweight: SC.Record.attr(Number),
    seniors_all_obese: SC.Record.attr(Number),
    seniors_all_high_bp: SC.Record.attr(Number),
    seniors_all_heart_dis: SC.Record.attr(Number),
    seniors_all_dia_type2: SC.Record.attr(Number),
    seniors_all_gh_poor: SC.Record.attr(Number),

    teens_all_walk_minutes: SC.Record.attr(Number),
    teens_all_auto_minutes: SC.Record.attr(Number),
    teens_all_rec_pa_minutes: SC.Record.attr(Number),
    teens_all_pa60_daysperweek: SC.Record.attr(Number),
    teens_all_walkfrom_any: SC.Record.attr(Number),
    teens_all_bmipct: SC.Record.attr(Number),
    teens_all_overweight: SC.Record.attr(Number),
    teens_all_obese: SC.Record.attr(Number),
    teens_all_gh_poor: SC.Record.attr(Number),

    children_all_walk_minutes: SC.Record.attr(Number),
    children_all_auto_minutes: SC.Record.attr(Number),
    children_all_rec_pa_minutes: SC.Record.attr(Number),
    children_all_pa60_daysperweek: SC.Record.attr(Number),
    children_all_walkfrom_any: SC.Record.attr(Number),
    children_all_bmipct: SC.Record.attr(Number),
    children_all_overweight: SC.Record.attr(Number),
    children_all_obese: SC.Record.attr(Number),
    children_all_gh_poor: SC.Record.attr(Number)
});
