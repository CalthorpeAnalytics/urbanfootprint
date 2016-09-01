
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

import unittest
from nose import with_setup
from nose.tools import assert_equal
from footprint.main.lib.functions import deep_merge

__author__ = 'calthorpe_analytics'

class TestFunctions(unittest.TestCase):
    def setup(self):
        pass

    def teardown(self):
        pass

    @with_setup(setup, teardown)
    def test(self):
        result = deep_merge({1:{1:1}, 'a':{'b':{'b':'b'}}}, {1:{2:2}, 2:2}, {3:3, 'a':{'b':{'c':'c'}}})
        assert_equal(result, {1:{1:1, 2:2}, 2:2, 3:3, 'a':{'b':{'b':'b', 'c':'c'}}})
