
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

"""Profiling middleware"""

import time
import cProfile
import pyprof2calltree


class ProfilingMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.REQUEST.get('profile'):
            return view_func(request, *view_args, **view_kwargs)

        profile = cProfile.Profile()

        result = profile.runcall(view_func, request, *view_args, **view_kwargs)

        short_url = request.path.replace('/footprint/api/v1/', '').replace('//', '/').replace('/', '_')
        pyprof2calltree.convert(profile.getstats(), 'profile_%s_%s.kgrind' % (short_url, int(time.time())))

        return result
