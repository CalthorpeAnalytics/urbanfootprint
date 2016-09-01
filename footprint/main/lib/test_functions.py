
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
from nose.tools import assert_equal
from footprint.main.lib.functions import remove_keys

class TestFunctions(unittest.TestCase):
    def test_remove_keys(self):
        x = dict(foo=dict(bar=dict(car=1)))
        assert_equal(len(remove_keys(x, [])), 1)
        assert_equal(len(remove_keys(x, ['foo'])), 0)
        # Use a two-segment string
        assert_equal(len(remove_keys(x, ['foo.bar'])), 1) # foo remains
        assert_equal(len(remove_keys(x, ['foo.bar'])['foo']), 0) # bar does not
        # Use a *
        assert_equal(len(remove_keys(x, ['foo.*.car'])), 1) # foo remains
        assert_equal(len(remove_keys(x, ['foo.*.car'])['foo']), 1) # bar remains
        assert_equal(len(remove_keys(x, ['foo.*.car'])['foo']['bar']), 0) # car does not
