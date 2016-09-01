#!/bin/env python

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


from unittest import TestCase
from testfixtures import Replacer

from footprint.main.management.commands.footprint_init import FootprintInit


class TestFootprintInit(TestCase):

    def test_empty_init(self):
        FootprintInit().run_footprint_init(skip=True)

    def test_wrong_celery_setting(self):
        with Replacer() as r:
            r.replace('django.conf.settings.CELERY_ALWAYS_EAGER', False)
            with self.assertRaises(Exception):
                FootprintInit().run_footprint_init(skip=True)

    def test_recalculate_bounds(self):
        FootprintInit().run_footprint_init(skip=True, recalculate_bounds=True)

    def test_all_publishers(self):
        FootprintInit().run_footprint_init(skip=False)

    def test_all_publishers_nodb_entity(self):
        FootprintInit().run_footprint_init(skip=False, nodb_entity=True)

    def test_all_publishers_noimport(self):
        FootprintInit().run_footprint_init(skip=False, noimport=True)

    def test_all_publishers_nolayer(self):
        FootprintInit().run_footprint_init(skip=False, nolayer=True)

    def test_all_publishers_noresult(self):
        FootprintInit().run_footprint_init(skip=False, noresult=True)

    def test_all_publishers_notilestache(self):
        FootprintInit().run_footprint_init(skip=False, notilestache=True)

    def test_all_publishers_nobuilt_form(self):
        FootprintInit().run_footprint_init(skip=False, form=True)

    def test_all_publishers_nouser(self):
        FootprintInit().run_footprint_init(skip=False, nouser=True)

    def test_delete_clones(self):
        FootprintInit().run_footprint_init(skip=True, delete_clones=True)

    # Doesn't work until we have FutureScenario objects in the test database
    def disabled_layer_from_selection(self):
        FootprintInit().run_footprint_init(skip=True, test_layer_from_selection=True)

    # Doesn't work until we have FutureScenario objects in the test database
    def disabled_clone_scenarios(self):
        FootprintInit().run_footprint_init(skip=True, test_clone_scenarios=True)
