
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

import logging
from footprint.main.management.commands.footprint_init import FootprintInit
logging.getLogger('south').setLevel(logging.CRITICAL)

def setUp(self):
    # Suppress annoying SQL logging that is turned on by testing
    logging.disable(logging.INFO)
    logging.getLogger('south').setLevel(logging.CRITICAL)
    FootprintInit().run_footprint_init()

def tearDown(self):
    logging.disable(logging.NOTSET)
    logging.getLogger('south').setLevel(logging.NOTSET)
    pass
