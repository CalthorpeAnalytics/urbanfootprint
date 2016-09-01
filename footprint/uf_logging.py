
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
import logging

LOG_FORMAT = "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s"
LOG_TIME_FORMAT = '%Y/%b/%d %H:%M:%S'

if not hasattr(logging, "set_up_done"):
    logging.set_up_done = False


COLORLOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)-8s%(reset)s %(message)s"
        },
        'verbose': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(asctime)s %(name)s %(levelname)s]%(reset)s %(message)s"

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
            'formatter': 'colored'
        }
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'footprint': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'WARN',
        },
        'nose': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}


def set_up(debug=False):
    if logging.set_up_done:
        return
    from logging.config import dictConfig

    COLORLOGGING['handlers']['console']['formatter'] = 'verbose'
    try:
        dictConfig(COLORLOGGING)
    except:
        del COLORLOGGING['formatters']['colored']
        del COLORLOGGING['formatters']['verbose']
        COLORLOGGING['handlers']['console']['formatter'] = 'simple'
        dictConfig(COLORLOGGING)
    logging.set_up_done = True

    # handler = logging.StreamHandler()
    #
    # formatter = logging.Formatter(LOG_FORMAT)
    # formatter.datefmt = LOG_TIME_FORMAT
    # handler.setFormatter(formatter)
    # l = logging.getLogger()
    #
    # l.setLevel(logging.DEBUG)
    # l.addHandler(handler)
