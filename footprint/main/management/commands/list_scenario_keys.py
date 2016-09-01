
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

import logging
from django.core.management.base import BaseCommand

from footprint.main.models.config.config_entity import ConfigEntity

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """This command lists all config_entity_keys for scenarios"""

    def handle(self, *args, **options):
        print ','.join(sorted([c.key for c in ConfigEntity.objects.all() if c.key.endswith('_s')]))
