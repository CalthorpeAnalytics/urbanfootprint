
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

"""Settings just for testing.

This modules imports from the default settings, which means it
currently imports both settings.py and local_settings.py before
overriding a few variables.

This is meant to be used by setting DJANGO_SETTINGS_MODULE or passing --settings to manage.py.

"""

from __future__ import absolute_import

from .default_settings import *

# Fixtures for the given client will be loaded
CLIENT = 'demo'

USE_SAMPLE_DATA_SETS = True

# Run celery as the main process
CELERY_ALWAYS_EAGER = True

# Indicates that the system should use test data for default data sets
import warnings
warnings.filterwarnings(
    'error', r"DateTimeField received a naive datetime", \
    RuntimeWarning, r'django\.db\.models\.fields')

DEBUG = True
TASTYPIE_FULL_DEBUG = True
CONSOLE_DEBUG = DEBUG
TEMPLATE_DEBUG = DEBUG


# Set the source for built form imports, or don't import them at all
IMPORT_BUILT_FORMS = 'CSV' #  set to 'CSV' to run full import, 'JSON' to use fixtures, or 'FALSE' to skip import
# Skip slow calculations for testing
SKIP_ALL_BUILT_FORMS = True
TEST_SKIP_BUILT_FORM_COMPUTATIONS = False

MEDIA_ROOT = '/srv/calthorpe_media'

SOUTH_TESTS_MIGRATE = False

# We only want the main database, not any of the import or sample_data
# TODO: Move those others out of the default settings and into some
# kind of dev-only or deploy-only setting, so that tests don't have to
# special-case them.
_default_database = DATABASES['default']
DATABASES = {
    'default': _default_database
}


SQL_PATH = "/srv/calthorpe/urbanfootprint/calthorpe/server/footprint/main/static/sql"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            #'class': 'footprint.main.color_logger.ColorHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
            },
        'footprint': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
            },
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'INFO',
            },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'DEBUG',
            },
        'nose': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
            },
        'sarge': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'CRITICAL',
            },
        }
}
from logging.config import dictConfig
dictConfig(LOGGING)
