
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

from tastypie.fields import DictField, ListField
from footprint.main.resources.presentation_medium_resource import PresentationMediumResource
from footprint.main.resources.presentation_resources import PresentationResource
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.presentation.result.result import Result
from footprint.main.resources.mixins.mixins import ToManyFieldWithSubclasses

class ResultLibraryResource(PresentationResource):

    results = ToManyFieldWithSubclasses(
        'footprint.main.resources.result_resources.ResultResource',
        attribute='results',
        full=False,
        null=True)

    class Meta(PresentationResource.Meta):
        resource_name = 'result_library'
        always_return_data = True
        queryset = ResultLibrary.objects.all()
        excludes = ['configuration', 'presentation_media']


class ResultResource(PresentationMediumResource):

    # Returns the results of the DbEntity query
    query = ListField(attribute='query', null=False)

    class Meta(PresentationMediumResource.Meta):
        resource_name = 'result'
        always_return_data = True
        queryset = Result.objects.all()
