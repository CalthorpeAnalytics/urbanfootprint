
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


from tastypie.fields import BooleanField
from footprint.client.configuration import resolve_fixture
from footprint.client.configuration.fixture import LayerConfigurationFixture
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.publishing.layer_publishing import resolve_layer_configuration
from footprint.main.resources.medium_resources import LayerStyleResource
from footprint.main.resources.mixins.mixins import ToManyFieldWithSubclasses, CloneableResourceMixin, \
    ToOneFieldWithSubclasses
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.resources.presentation_medium_resource import PresentationMediumResource
from footprint.main.resources.presentation_resources import PresentationResource


class LayerLibraryResource(PresentationResource):

    layers = ToManyFieldWithSubclasses(
        'footprint.main.resources.layer_resources.LayerResource',
        attribute='computed_layers',
        full=False,
        null=True)

    class Meta(PresentationResource.Meta):
        resource_name = 'layer_library'
        always_return_data = True
        queryset = LayerLibrary.objects.all()
        excludes = ['configuration', 'presentation_media']

class LayerResource(PresentationMediumResource, CloneableResourceMixin):

    create_from_selection = BooleanField(attribute='create_from_selection')
    medium = ToOneFieldWithSubclasses(
        LayerStyleResource,
        attribute='medium_subclassed',
        full=True,
        null=True)

    def full_hydrate(self, bundle):
        """
            Defaults the template of new Layers
        :param bundle:
        :return:
        """
        bundle = super(LayerResource, self).full_hydrate(bundle)
        if not bundle.obj.id:
            # If the layer is new, create its template.
            # This used to be done in the layer_publisher, but since the refactoring
            # to support style editing it the layer.medium is required, so this
            # must be done pre-save of the Layer
            config_entity = bundle.obj.db_entity_interest.config_entity

            db_entity_interest = bundle.obj.db_entity_interest
            #for debugging, delete existing layers on layer save
            db_entity_interest.presentationmedium_set.all().delete()

            # layer_fixture = resolve_fixture(
            #     "presentation",
            #     "layer",
            #     LayerConfigurationFixture,
            #     config_entity.schema())
            #
            # layer_configuration = create_layer_configuration_for_import(
            #     config_entity,
            #     bundle.obj.db_entity_key)
            #
            # template = layer_fixture.update_or_create_layer_style(
            #     config_entity,
            #     layer_configuration,
            #     bundle.obj)
            # bundle.obj.medium = template
        return bundle

    class Meta(PresentationMediumResource.Meta):
        resource_name = 'layer'
        always_return_data = True
        # Don't allow any Layer of and incomplete uploaded DbEntity
        queryset = Layer.objects.filter(db_entity_interest__db_entity__setup_percent_complete=100)
        filtering = {
            "id": ('exact',),
        }
