
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

# footprint_init required celery to run synchronously
from __future__ import absolute_import

from .default_settings import *

CELERY_ALWAYS_EAGER = True
DEBUG = False
FOOTPRINT_INIT = True
USE_SAMPLE_DATA_SETS = False

# Uncomment USE_SAMPLE_DATA_SETS and DEV for development, but
# DO NOT CHECK IN! These are both set to False in default_settings.py
# USE_SAMPLE_DATA_SETS = True
# DEV = True

from footprint import uf_logging
uf_logging.set_up(DEBUG)
