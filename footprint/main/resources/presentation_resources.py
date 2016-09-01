
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


from tastypie import fields
from footprint.main.models.presentation.presentation_configuration import PresentationConfiguration
from footprint.main.models.presentation.presentation import Presentation
from footprint.main.resources.config_entity_resources import ConfigEntityResource
from footprint.main.resources.mixins.mixins import ToManyFieldWithSubclasses
from footprint.main.resources.pickled_dict_field import PickledObjField
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'


class PresentationResource(FootprintResource):

    # Returns the computed and subclassed PresentationMedia
    presentation_media_query = lambda bundle: bundle.obj.computed_presentation_media.all().select_subclasses()
    presentation_media = ToManyFieldWithSubclasses(
        'footprint.main.resources.presentation_medium_resource.PresentationMediumResource',
        attribute=presentation_media_query,
        full=False,
        null=True)

    # Just return the URI of thie config_entity, since it should always already be loaded by the user beforehand
    config_entity = fields.ToOneField(ConfigEntityResource, 'config_entity', full=False)

    # Only turn on for debugging. This represents the initial configuration of the PresentationMedia, such as visibility
    #configuration = fields.ToOneField('footprint.main.resources.presentation_resources.PresentationConfigurationResource', 'configuration', full=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = Presentation.objects.all()
        excludes = ['configuration']


class PresentationConfigurationResource(FootprintResource):
    """
        These are not serialized as part of the API since they represent initial state and all important attributes are copied to the PresentationMedium instances. They can be turned on in PresentationResource for debugging purposes
    """

    data = PickledObjField(attribute='data', readonly=True, null=False, blank=False)

    class Meta(FootprintResource.Meta):
        resource_name = 'presentation_configuration'
        always_return_data = True
        queryset = PresentationConfiguration.objects.all()
