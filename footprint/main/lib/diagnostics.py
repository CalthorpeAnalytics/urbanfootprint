
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

from Queue import Queue

__author__ = 'calthorpe_analytics'

from footprint.main.urls  import urlpatterns

queue = Queue()
def show_urls(urllist=urlpatterns, depth=0):
    """
    Inspects the URL regexes
    :param urllist:
    :param depth:
    :return:
    """
    if (depth > 50):
        return
    for entry in urllist:
        queue.put(entry)
    while not queue.empty():
        entry = queue.get()
        print "{0} - {1}".format("  " * depth, entry.regex.pattern)
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)
