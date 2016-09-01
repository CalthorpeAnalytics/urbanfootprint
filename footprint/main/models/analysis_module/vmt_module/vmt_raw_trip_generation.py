
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

from footprint.main.models.analysis_module.vmt_module.vmt_model_constants import cJobConversionRate

__author__ = 'calthorpe_analytics'


def generate_raw_trips(vmt_feature):
    #------------------------------------------------------
    #single family trips
    #------------------------------------------------------
    if vmt_feature['du_detsf'] == 0 or vmt_feature['du_detsf'] is None:
        single_family_trips = 0
    else:
        single_family_trips = vmt_feature['du_detsf'] * 9.57 #mk9

    vmt_feature['raw_trips_sf'] = int(round(single_family_trips))

    #------------------------------------------------------
    #multifamily trips
    #------------------------------------------------------
    if vmt_feature['du_mf2to4'] == 0 or vmt_feature['du_mf2to4'] is None:
        multifamily_2to4_trips = 0.0
    else:
        multifamily_2to4_trips = vmt_feature['du_mf2to4'] * 6.65 #mk9

    if vmt_feature['du_mf5p'] == 0 or vmt_feature['du_mf5p'] is None:
        multifamily_5plus_trips = 0.0
    else:
        multifamily_5plus_trips = vmt_feature['du_mf5p'] * 4.18 #mk9

    vmt_feature['raw_trips_mf24'] = int(round(multifamily_2to4_trips))
    vmt_feature['raw_trips_mf5'] = int(round(multifamily_5plus_trips))

    #------------------------------------------------------
    #retail trips
    #------------------------------------------------------
    if vmt_feature['emp_retail'] == 0 or vmt_feature['emp_retail'] is None:
        retail_trips = 0.0
    else:
        retail_trips = (vmt_feature['emp_retail'] / cJobConversionRate) * 42.94 #mk9

    vmt_feature['raw_trips_retail'] = int(round(retail_trips))

    #------------------------------------------------------
    #restaurant trips
    #------------------------------------------------------
    if vmt_feature['emp_restaccom'] == 0 or vmt_feature['emp_restaccom'] is None:
        restaurant_trips = 0.0
    else:
        restaurant_trips = (vmt_feature['emp_restaccom'] / 2.0) * 75.0

    vmt_feature['raw_trips_restaurant'] = int(round(restaurant_trips))

    #------------------------------------------------------
    #arts/entertainment trips
    #------------------------------------------------------
    if vmt_feature['emp_arts_entertainment'] == 0 or vmt_feature['emp_arts_entertainment'] is None:
        arts_entertainment_trips = 0.0
    else:
        arts_entertainment_trips = (vmt_feature['emp_arts_entertainment'] / 2.0) * 20.0

    vmt_feature['raw_trips_entertainment'] = int(round(arts_entertainment_trips))

    #------------------------------------------------------
    #Office trips
    #------------------------------------------------------
    if vmt_feature['emp_office'] == 0 or vmt_feature['emp_office'] is None:
        office_trips = 0.0
    else:
        office_trips = vmt_feature['emp_office'] * 3.32

    vmt_feature['raw_trips_office'] = int(round(office_trips))

    #------------------------------------------------------
    #Public Administration Trips
    #------------------------------------------------------
    if vmt_feature['emp_public'] == 0 or vmt_feature['emp_public'] is None:
        public_trips = 0.0
    else:
        public_trips = vmt_feature['emp_public'] * 3.32 #mk9

    vmt_feature['raw_trips_public'] = int(round(public_trips))

    #------------------------------------------------------
    #Industrial trips
    #------------------------------------------------------
    if vmt_feature['emp_industry'] == 0 or vmt_feature['emp_industry'] is None:
        industrial_trips = 0.0
    else:
        industrial_trips = vmt_feature['emp_industry'] * 3.02 #mk9

    vmt_feature['raw_trips_industry'] = int(round(industrial_trips))

    #------------------------------------------------------
    #K-12 School trips
    #------------------------------------------------------

    if vmt_feature['du_detsf'] + vmt_feature['du_mf2to4'] + vmt_feature['du_mf5p'] == 0 or vmt_feature['du_detsf'] + \
            vmt_feature['du_mf2to4'] + vmt_feature[
        'du_mf5p'] is None:
        education_trips = 0.0
    else:
        education_trips = ((vmt_feature['du_detsf'] * 9.57) + (vmt_feature['du_mf2to4'] * 6.65) + (
            vmt_feature['du_mf5p'] * 4.18)) * 0.097

    vmt_feature['raw_trips_k12'] = int(round(education_trips))
    vmt_feature['raw_trips_h_ed'] = 0

    return vmt_feature
