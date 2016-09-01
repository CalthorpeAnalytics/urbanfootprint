
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

from tastypie.bundle import Bundle
from footprint.main.lib.functions import map_dict_to_dict, is_list_or_tuple

__author__ = 'calthorpe_analytics'

def unbundle(bundle):
    if isinstance(bundle, Bundle):
        return map_dict_to_dict(lambda attr, value: [attr, unbundle(value)], bundle.data)
    elif is_list_or_tuple(bundle):
        return map(lambda value: unbundle(value), bundle)
    else:
        return bundle

def unbundle_list(values):
    map(lambda value: unbundle(value) if isinstance(value, Bundle) else value, values)
