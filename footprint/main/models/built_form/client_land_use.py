
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

from model_utils.managers import InheritanceManager
from footprint.main.models.built_form.built_form import BuiltForm

__author__ = 'calthorpe_analytics'


class ClientLandUse(BuiltForm):
    """
        A generic class describing land use for clients to subclass. This is used by the API to deliver client-specific BuiltForm classes
    """
    objects = InheritanceManager()
    class Meta(object):
        abstract = True
        app_label = 'main'
