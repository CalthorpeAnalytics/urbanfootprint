
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

from . import range


class TestRange(TestCase):

    def test_make_ranges_with_increments(self):
        r = range.make_ranges(0, 10, 3, [1, 2])
        self.assertEqual(1, r[1].length())
        self.assertEqual('0_1', r[0].name())
        self.assertEqual(2, r[2].start)
        self.assertEqual(10, r[2].end)

    # not sure if min should be allowed to be greater than max, but currently can
    def test_make_ranges_min_greater_than_max(self):
        r = range.make_ranges(5, 1, 3)
        self.assertEqual(-1, r[2].end)
        self.assertEqual(3, r[1].start)

    def test_make_ranges_overlap_zero(self):
        r = range.make_ranges(1, -1, 1)
        r2 = range.make_ranges(-1, 1, 1)
        r_zero = range.make_ranges(0, 0, 1)
        self.assertEqual(False, r[0].overlaps(r_zero[0]))  # weird doesn't think (0,0) range is an overlap for (1,-1)
        self.assertEqual(True, r_zero[0].overlaps(r2[0]))

    def test_make_ranges_overlap_true(self):
        r = range.make_ranges(0, 10, 2)  # makes Range(0,5) & Range(5,10)
        r5 = range.make_ranges(5, 5, 1)  # Range(5,5)
        self.assertEqual(True, r[0].overlaps(r5[0]))
        self.assertEqual(True, r[1].overlaps(r5[0]))

    def test_make_increments(self):
        r_inc = range.make_increments(0, 10, 3)
        print(r_inc)
        self.assertEqual([0, 2, 4], r_inc)

    # not sure if increment should be allowed to be greater than max? currently can
    def test_make_increments_count_greater_than_range(self):
        r_inc = range.make_increments(1, 5, 10)  # when max-min is less than count, increment is -1
        print(r_inc)
        self.assertEqual([1, 0, -1, -2, -3, -4, -5, -6, -7, -8], r_inc)

    def test_make_increments_and_ranges(self):
        r_inc = range.make_increments(0, 10, 3)
        r = range.make_ranges(0, 10, 4, r_inc)
        self.assertEqual(4, r[3].start)
        self.assertEqual(4, r[2].end)
