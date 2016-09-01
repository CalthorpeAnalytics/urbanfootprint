
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

from django.core.management import call_command

__author__ = 'calthorpe_analytics'

import glob
import os


def import_feeds_in_directory(path):
    """
    runs the manage command to import all GTFS zipfiles in a given directory
    """

    os.chdir(path)
    files_to_import = glob.glob("*.zip")

    for filename in files_to_import:
        filepath = os.path.join(path, filename)
        call_command('importgtfs', filepath)
