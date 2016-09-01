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

from decimal import Decimal

__author__ = 'calthorpe_analytics'


class Constants(object):
    USE_EFFICIENCY_DEFAULT = .85

    RESIDENTIAL_SQUARE_FEET_PER_DWELLING_UNIT = 1
    OFFICE_SQUARE_FEET_PER_EMPLOYEE = 1
    RETAIL_SQUARE_FEET_PER_EMPLOYEE = 1
    INDUSTRIAL_SQUARE_FEET_PER_EMPLOYEE = 1

    HH1_PERCENT = .4
    HH2_PERCENT = .2
    HH3_PERCENT = .2
    HH4_PERCENT = .1
    HH5P_PERCENT = .1

    AVERAGE_HH_SIZE = 2.5

    VACANCY_RATE = 0

    SQUARE_FEET_PER_ACRE = Decimal(43560.00000)
    PARKING_STALL_SQUARE_FEET =  Decimal(330.00000)
