
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

from __future__ import absolute_import

from .default_settings import *

TILE_CACHE = "Disk"

USE_SAMPLE_DATA_SETS = False

# Run celery as the main process
CELERY_ALWAYS_EAGER = False

# Indicates that the system should use test data for default data sets
import warnings
warnings.filterwarnings(
    'error', r"DateTimeField received a naive datetime", RuntimeWarning, r'django\.db\.models\.fields'
)

DEV = False
DEBUG = False
TASTYPIE_FULL_DEBUG = False
CONSOLE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG

REUSE_DB = 1

# Set the source for built form imports, or don't import them at all
IMPORT_BUILT_FORMS = 'CSV'  # set to 'CSV' to run full import, 'JSON' to use fixtures, or 'FALSE' to skip import
# Skip slow calculations for testing
SKIP_ALL_BUILT_FORMS = False
TEST_SKIP_BUILT_FORM_COMPUTATIONS = False

SQL_PATH = "/srv/calthorpe/urbanfootprint/calthorpe/server/footprint/main/static/sql"

from footprint import uf_logging
uf_logging.set_up(DEBUG)
