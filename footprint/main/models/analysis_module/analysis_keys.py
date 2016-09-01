
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
RESIDENTIAL_TYPES = ['du_detsf_ll', 'du_detsf_sl', 'du_attsf', 'du_mf']

# COMMERCIAL_TYPES = ['retail_services', 'restaurant', 'accommodation', 'other_services', 'office_services', 'education',
#                     'public_admin', 'medical_services', 'wholesale', 'transport_warehousing']
COMMERCIAL_TYPES = ['retail_services', 'restaurant', 'accommodation', 'other_services', 'office_services', 'education',
                    'public_admin', 'medical_services', 'wholesale', 'transport_warehousing', 'construction', 'utilities',
                    'manufacturing', 'extraction', 'military', 'agriculture']

ALL_TYPES_AND_CATEGORIES = RESIDENTIAL_TYPES + COMMERCIAL_TYPES + ['residential', 'commercial']

RESIDENTIAL_TYPES = ['du_detsf_ll', 'du_detsf_sl', 'du_attsf', 'du_mf']
