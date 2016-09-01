
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

from tastypie.resources import ModelResource

__author__ = 'calthorpe_analytics'

class EditorResourceMixin(ModelResource):
    """
        Minimizes the creator and updater fields to the username
    """

    def dehydrate_creator(self, bundle):
        """
            Expose only the username
        :param bundle:
        :return:
        """
        creator = bundle.data.get('creator')
        return creator.data['username'] if creator else None

    def dehydrate_updater(self, bundle):
        """
            Expose only the username
        :param bundle:
        :return:
        """
        updater = bundle.data.get('updater')
        return updater.data['username'] if updater else None
