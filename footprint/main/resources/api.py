
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

import os
from django.conf import settings

__author__ = 'calthorpe_analytics'

def detail_url(instance, format='json'):
    """
        Given a model instance returns the base tastypie API url
    :param instance: Any model instance supported by the API
    :return: the string URL
    """
    return os.path.join(settings.API_PATH, instance.__class__._meta.verbose_name_raw, str(instance.pk), '?format={0}'.format(format))

def list_url(cls, format='json'):
    return os.path.join(settings.API_PATH, cls._meta.verbose_name_raw, '?format={0}'.format(format))
