
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

from json import dumps
from django.conf import settings

import redis

def send_message_to_client(userid, message_dictionary):
    """
    Sends a message to the web client through websockets
    """
    r = redis.StrictRedis(host=settings.CELERY_REDIS_HOST, port=settings.CELERY_REDIS_PORT, db=settings.CELERY_REDIS_DB)
    channel = 'channel_{0}'.format(userid)
    json_message = dumps(message_dictionary)
    r.publish(channel, json_message)
