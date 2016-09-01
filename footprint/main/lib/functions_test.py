
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

from functions import deep_merge


class TestDeepMerge(unittest.TestCase):

    def test_simple_merge(self):
        d1 = {'one': 1}
        d2 = {'two': 2}

        self.assertEquals({'one': 1, 'two': 2},
                          deep_merge(d1, d2))

    def test_conflicting_merge(self):
        d1 = {'one': 1}
        d2 = {'one': 2}

        # Last one wins
        self.assertEquals({'one': 2},
                          deep_merge(d1, d2))

    def test_merge_with_extra(self):
        d1 = {'one': 1}
        d2 = {'one': 1, 'two': 2}

        # Last one still wins even with other keys
        self.assertEquals({'one': 1, 'two': 2},
                          deep_merge(d1, d2))

    def test_compatible_merge(self):
        d1 = {'one': 1}
        d2 = {'one': 1}

        self.assertEquals({'one': 1},
                          deep_merge(d1, d2))

    def test_list_merge(self):
        d1 = {'one': [1, 2, 3]}
        d2 = {'one': [4, 5, 6]}

        # Doesn't add them together, last one wins?!
        self.assertEquals({'one': [4, 5, 6]},
                          deep_merge(d1, d2))

    def test_merge_dicts_of_dicts(self):
        d1 = {'one': {'inner': [1, 2, 3]}}
        d2 = {'two': {'inner': [4, 5, 6]}}

        # Safely merges non-conflicting dicts
        self.assertEquals({'one': {'inner': [1, 2, 3]},
                           'two': {'inner': [4, 5, 6]}},
                          deep_merge(d1, d2))

    def test_merge_overlapping_dicts_of_dicts(self):
        d1 = {'one': {'inner': [1, 2, 3]}}
        d2 = {'one': {'inner': [4, 5, 6]}}

        # Still odd last-one-wins behavior
        self.assertEquals({'one': {'inner': [4, 5, 6]}},
                          deep_merge(d1, d2))

    def test_merge_deep(self):
        d1 = {'one': {'inner': {'deep': (1, 2, 3)}}}
        d2 = {'one': {'inner': {'deep': (4, 5, 6)}}}

        # Still odd last-one-wins behavior
        self.assertEquals({'one': {'inner': {'deep': (4, 5, 6)}}},
                          deep_merge(d1, d2))

    def test_merge_deep_with_extra(self):
        d1 = {'one': {'inner': {'deep': (1, 2, 3),
                                'deep_extra': 1},
                      'inner_extra': 7}}
        d2 = {'one': {'inner': {'deep': (4, 5, 6)}}}

        self.assertEquals({'one': {'inner': {'deep': (4, 5, 6),
                                             'deep_extra': 1},
                                   'inner_extra': 7}},
                          deep_merge(d1, d2))

    def test_merge_deep_with_extra_on_both(self):
        d1 = {'one': {'inner': {'deep': (1, 2, 3),
                                'deep_extra': 1},
                      'inner_extra': 7}}
        d2 = {'one': {'inner': {'deep': (4, 5, 6),
                                'deep_extra': 11}}}

        # not adding up 'deep_extra' this time around?
        self.assertEquals({'one': {'inner': {'deep': (4, 5, 6), 'deep_extra': 11}, 'inner_extra': 7}},
                          deep_merge(d1, d2))

    def test_merge_incompatible_types(self):
        d1 = {'one': 1}
        d2 = {'one': [1, 2, 3]}

        # No collisions between int and list?
        self.assertEquals({'one': [1, 2, 3]},
                          deep_merge(d1, d2))

        self.assertEquals({'one': 1},
                          deep_merge(d2, d1))

    def test_merge_incompatible_sequences(self):
        d1 = {'one': (4, 5, 6)}
        d2 = {'one': [1, 2, 3]}

        # No collisions between int and list?
        with self.assertRaises(Exception):
            deep_merge(d1, d2)

        with self.assertRaises(Exception):
            deep_merge(d2, d1)

    def test_merge_non_dict(self):

        with self.assertRaises(Exception):
            deep_merge({'one': 1}, 4)

    def test_merge_lists(self):
        d1 = [1, 2, 3]
        d2 = [4, 5, 6]
        self.assertEquals([4, 5, 6], deep_merge(d1, d2))

    def test_merge_lists_of_dicts(self):
        d1 = [{'one': 1}, {'two': 2}]
        d2 = [{'three': 3}, {'four': 4}]
        self.assertEquals([{'one': 1, 'three': 3},
                           {'four': 4, 'two': 2}],
                          deep_merge(d1, d2))

    def test_merge_lists_of_dicts(self):
        d1 = [{'one': 1}, {'two': 2}]
        d2 = [{'three': 3}, {'four': 4}]
        # Merged lists get returned as lists
        self.assertEquals([{'one': 1, 'three': 3},
                           {'four': 4, 'two': 2}],
                          deep_merge(d1, d2))

    def test_merge_tuples_of_dicts(self):
        d1 = ({'one': 1}, {'two': 2})
        d2 = ({'three': 3}, {'four': 4})
        # Merged tuples get returned as tuples
        self.assertEquals(({'one': 1, 'three': 3},
                           {'four': 4, 'two': 2}),
                          deep_merge(d1, d2))

    def test_merge_empty(self):
        d1 = {'one': None}
        d2 = {'two': 2}
        self.assertEquals({'two': 2, 'one': None},
                          deep_merge(d1, d2))

    def test_merge_empty_collision(self):
        d1 = {'one': None}
        d2 = {'one': 1}
        self.assertEquals({'one': 1},
                          deep_merge(d1, d2))

        # but last one doesn't win when the first is None
        self.assertEquals({'one': None},
                          deep_merge(d2, d1))

    def test_single(self):
        d1 = {'one': 1}
        self.assertEquals({'one': 1},
                          deep_merge(d1))

        # but we always create a new object
        self.assertIsNot(d1, deep_merge(d1))

if __name__ == '__main__':
    unittest.main()
