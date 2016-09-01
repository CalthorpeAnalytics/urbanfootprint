
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

from django.db import models
from footprint.main.models.geospatial.feature import Feature

class VmtVariablesFeature(Feature):

    du = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_res_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_emp_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_mixed_use_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pop_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_ret_qtrmi = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_1mile = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_res_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_emp_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    acres_parcel_mixed_use_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pop_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    emp_ret_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    du_mf_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_00_10_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_10_20_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_20_30_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_30_40_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_40_50_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_50_60_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_60_75_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_75_100_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    hh_inc_100p_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pop_employed_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pop_age16_up_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    pop_age65_up_vb = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transit_1km = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta(object):
        abstract = True
        app_label = 'main'
