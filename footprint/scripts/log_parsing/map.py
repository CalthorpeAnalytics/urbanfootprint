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


import re
import sys
from datetime import datetime

LOG_LINE_RE = r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (?P<module>\S*) [A-Z]*\](?P<msg>.*)'


def map():
    last_timestamp = None
    last_log_msg = None

    for line in sys.stdin:
        line = line.strip()
        match = re.search(LOG_LINE_RE, line)

        if match:
            timestamp = datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S,%f')
            log_msg = match.group('msg')

            if last_timestamp and last_log_msg:
                delta = (timestamp - last_timestamp).total_seconds()

                print '{}\t{}'.format(last_log_msg, delta)

            last_timestamp = timestamp
            last_log_msg = log_msg


if __name__ == "__main__":
    map()
