# coding=utf-8

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

from django.db import models
from django.contrib.auth import get_user_model
from footprint.main.models.geospatial.feature import PaintingFeature
import logging

logger = logging.getLogger(__name__)
__author__ = 'calthorpe_analytics'

class CanvasFeature(PaintingFeature):

    # removed and added to VMT preprocess
    # point = PointField(null=True, spatial_index=True)

    source_id = models.CharField(max_length=250, null=True, blank=True, default=None)
    region_lu_code = models.CharField(max_length=250, null=True, blank=True, default=None)
    built_form_key = models.CharField(max_length=250, null=True, blank=True, default=None)
    land_development_category = models.CharField(max_length=250, null=True, blank=True, default=None)
    intersection_density_sqmi = models.DecimalField(max_digits=14, null=True, decimal_places=4, default=0)

    acres_gross = models.DecimalField(max_digits=14, null=True, decimal_places=4, default=0)
    sqft_parcel = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    acres_parcel_res = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_mixed_use = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_no_use = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    pop = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    hh = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    du_detsf = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du_attsf = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du_mf = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp_ret = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_off = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_pub = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_ind = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_ag = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_military = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    du_detsf_sl = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du_detsf_ll = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du_mf2to4 = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    du_mf5p = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp_retail_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_restaurant = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_accommodation = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_arts_entertainment = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_other_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp_office_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_public_admin = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_education = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_medical_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp_manufacturing = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_wholesale = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_transport_warehousing = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_utilities = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_construction = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    emp_agriculture = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    emp_extraction = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    bldg_sqft_detsf_sl = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_detsf_ll = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_attsf = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_mf = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    bldg_sqft_retail_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_restaurant = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_accommodation = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_arts_entertainment = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_other_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_office_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_public_admin = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_education = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_medical_services = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_wholesale = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    bldg_sqft_transport_warehousing = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    residential_irrigated_sqft = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    commercial_irrigated_sqft = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    acres_parcel_res_detsf = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_res_detsf_sl = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_res_detsf_ll = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_res_attsf = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_res_mf = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    acres_parcel_emp_off = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp_pub = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp_ret = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp_ind = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp_ag = models.DecimalField(max_digits=14, null=True, decimal_places=4)
    acres_parcel_emp_military = models.DecimalField(max_digits=14, null=True, decimal_places=4)

    class Meta(object):
        abstract = True
        app_label = 'main'


    @classmethod
    def post_save(cls, user_id, objects, **kwargs):
        """
            Called after Features are saved by the FeatureResource. This calls post save publishing for
            Features, which includes updating tilestache for impacted layers and calling the
            Scenario Builder Analysis Tool
        :param user_id:
        :param objects:
        :param kwargs:
        :return:
        """

        ids = map(lambda obj: obj.id, objects)
        from footprint.main.publishing.feature_publishing import on_feature_post_save
        on_feature_post_save(cls, instance=objects, ids=ids, user_id=user_id)

        from footprint.main.models.analysis_module.analysis_module import AnalysisModuleKey, AnalysisModule
        core = AnalysisModule.objects.get(config_entity=cls.config_entity, key=AnalysisModuleKey.SCENARIO_BUILDER)
        # Update the core user to the current user
        if not core.updater or core.updater.id != user_id:
            core.updater = get_user_model().objects.get(id=user_id)
            core._no_post_save_task_run = True
            core.save()
            core._no_post_save_task_run = False

        core.start(ids=ids)
