#!/usr/bin/env python

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


import sys


def reduce():
    last_msg = None
    last_delta = None
    running_total = 0
    counts = 0

    for line in sys.stdin:
        line = line.strip()
        msg, delta = line.split('\t')

        if last_msg and last_delta:

            if msg == last_msg:
                running_total += float(delta)
                counts += 1

            else:
                if running_total and counts:
                    print "{}\t{}\t{}".format(running_total, counts, last_msg)

                running_total = float(delta)
                counts = 1

        last_msg = msg
        last_delta = delta

    # include the last line
    if running_total and counts:
        print "{}\t{}\t{}".format(running_total, counts, last_msg)


if __name__ == "__main__":
    reduce()
