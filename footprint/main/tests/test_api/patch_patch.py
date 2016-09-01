
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

from urlparse import urlparse
from django.test.client import FakePayload, Client, MULTIPART_CONTENT

__author__ = 'calthorpe_analytics'

class Client2(Client):
    """
    Construct a second test client which can do PATCH requests.
    """
    def patch(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        """
            Construct a PATCH request."
        :param path:
        :param data:
        :param content_type:
        :param extra:
        :return:
        """
        patch_data = self._encode_data(data, content_type)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(patch_data),
        }
        r.update(extra)
        return self.request(**r)
