
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


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def length(self):
        return self.end - self.start

    def overlaps(self, other):
        return not(self.end < other.start or other.end < self.start)

    def name(self):
        return '_'.join([str(self.start), str(self.end)])

    def __unicode__(self):
        return u'%s' % self.name()

    def __str__(self):
        return self.__unicode__().encode('utf-8')


def make_ranges(min, max, count, explicit_increments=[]):
    full_range = max-min
    increment = full_range/count
    if len(explicit_increments) > 0:
        if len(explicit_increments)+1 != count:
            raise Exception("explicit_increments count ({0}) is not one less than count ({1})".format(len(explicit_increments), count))
        all_increments = [min]+explicit_increments+[max]
        new_ranges_index_list = range(len(all_increments)-1)
        new_ranges = [Range(all_increments[i], all_increments[i+1]) for i in new_ranges_index_list]
        return new_ranges
    else:
        new_ranges = [Range(min+increment*i, min+increment*(i+1)) for i in range(count)]
        return new_ranges


# Complements make_ranges by creating a sequence of values between and including min and max
def make_increments(min, max, count):
    full_range = max-min
    # Decrease the count so that our last increment is max
    increment = full_range/count-1
    # Creates a sequence starting a min and ending at max, with intermediates equidistant
    increments = [(min + increment * i) for i in range(count)]
    return increments
