
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

from footprint.main.models.built_form.flat_built_form import FlatBuiltForm
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class FlatBuiltFormResource(FootprintResource):

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = FlatBuiltForm.objects.all()
        resource_name = 'flat_built_form'
        filtering = {
            "built_form_id": ('exact',),
        }
