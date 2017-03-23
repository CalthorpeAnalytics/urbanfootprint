
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

import json

__author__ = 'calthorpe_analytics'
placetype_example_json = """{

        "pt__town_commercial" : [
            {
                "example_name"        : "Downtown Ashland",
                "example_url"         : "http://www.ashland.or.us/"
            },
            {
                "example_name"        : "Downtown Redwood City",
                "example_url"         : "http://www.redwoodcity.org/"
            }

        ],
        "pt__campus_university" : [
            {
                "example_name"  : "University of California, Berkeley",
                "example_url"   : "http://www.berkeley.edu/index.html"
            },
            {
                "example_name"  : "University of Oregon",
                "example_url"   : "http://uoregon.edu/"
            }

        ],
        "default" : [
            {
                "example_name"  : "Placetype example region 1",
                "example_url"   : "http://www.berkeley.edu/index.html"
            },
            {
                "example_name"  : "Placetype example region 2",
                "example_url"   : "http://uoregon.edu/"
            }

        ]
    }"""
PLACETYPE_EXAMPLES = json.loads(placetype_example_json)
