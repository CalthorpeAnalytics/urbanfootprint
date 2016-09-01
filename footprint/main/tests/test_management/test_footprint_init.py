
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

from django.core.management import call_command

from footprint.main.models.config.scenario import Scenario
from footprint.main.publishing.config_entity_initialization import update_or_create_scenarios


__author__ = 'calthorpe_analytics'

import unittest

class TestFootprintInit(unittest.TestCase):
    def test_import(self):
        call_command('footprint_init')
        assert(Scenario.objects.count(), update_or_create_scenarios())
