
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

# https://gist.github.com/tobych/6372218
# Monkey patch to work around https://code.djangoproject.com/ticket/13843

import django
from functools import wraps

def discard_exceptions(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    try:
      f(*args, **kwds)
    except (AttributeError, TypeError):
      pass
  return wrapper

django.contrib.gis.geos.prototypes.threadsafe.GEOSContextHandle.__del__ = \
  discard_exceptions(django.contrib.gis.geos.prototypes.threadsafe.GEOSContextHandle.__del__)
django.contrib.gis.geos.prototypes.io.IOBase.__del__ = \
  discard_exceptions(django.contrib.gis.geos.prototypes.io.IOBase.__del__)
