
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

from unittest import TestCase

from . import utils

class TestUtils(TestCase):

    def test_resolve_module_attr(self):

        self.assertEquals(self.__class__,
                          utils.resolve_module_attr('footprint.main.utils.utils_test.TestUtils'))

    def test_resolve_bad_module(self):
        with self.assertRaises(AttributeError):
            utils.resolve_module_attr('footprint.main.utils.utils_test.TestUTILS')

    def test_resolve_bad_package(self):
        with self.assertRaises(KeyError):
            utils.resolve_module_attr('footprint.main.utils.utils_zest.TestUtils')
