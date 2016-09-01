
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
from tastypie.resources import ModelResource
from footprint.main.lib.functions import get_first

from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.urban.urban_placetype import Placetype
from footprint.main.models.built_form.placetype_component import PlacetypeComponent, PlacetypeComponentCategory
from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.models.built_form.urban.building_use_definition import BuildingUseDefinition
from footprint.main.models.built_form.urban.building_use_percent import BuildingUsePercent
from footprint.main.models.built_form.primary_component_percent import PrimaryComponentPercent
from footprint.main.models.built_form.urban.building_attribute_set import BuildingAttributeSet
from footprint.main.models.built_form.built_form_set import BuiltFormSet
from footprint.main.models.presentation.built_form_example import BuiltFormExample
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.publishing.built_form_publishing import add_built_forms_to_built_form_sets
from footprint.main.resources.medium_resources import MediumResource, LayerStyleResource
from footprint.main.resources.mixins.mixins import TagResourceMixin, ToManyFieldWithSubclasses, ToManyCustomAddField, PublisherControlMixin, \
    CloneableResourceMixin, ToOneFieldWithSubclasses
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.pickled_dict_field import PickledDictField

from footprint.main.models.built_form.flat_built_form import FlatBuiltForm
from footprint.main.models.built_form.placetype_component_percent import PlacetypeComponentPercent
from footprint.main.models.built_form.agriculture.agriculture_attribute_set import AgricultureAttributeSet
from footprint.main.models.built_form.agriculture.crop import Crop
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.models.built_form.agriculture.landscape_type import LandscapeType

from footprint.main.models.built_form.urban.building import Building
from footprint.main.models.built_form.urban.building_type import BuildingType
from footprint.main.models.built_form.urban.urban_placetype import UrbanPlacetype
from footprint.main.resources.flat_built_form_resource import FlatBuiltFormResource
from footprint.main.resources.caching import using_bundle_cache

__author__ = 'calthorpe_analytics'


class BuiltFormResource(FootprintResource, TagResourceMixin, PublisherControlMixin, CloneableResourceMixin):

    # The Medium of the BuiltForm, like Layer, is a LayerStyle. Unlike Layer, we set full=False so that
    # we won't load all the layer styles for BuiltForms that the user never looks at
    medium = ToOneFieldWithSubclasses(
        LayerStyleResource,
        attribute='medium_subclassed',
        full=False,
        null=True)
    media = fields.ToManyField(MediumResource, 'media', null=True, full=False)
    examples = fields.ToManyField('footprint.main.resources.built_form_resources.BuiltFormExampleResource', 'examples', null=True, full=False)

    # Do not wrap with using_bundle_cache. It fails since this doesn't return a query
    def flat_building_densities_query(bundle):
        return get_first(FlatBuiltForm.objects.filter(built_form_id=bundle.obj.id))

    flat_building_densities = fields.ToOneField(FlatBuiltFormResource,
        attribute=flat_building_densities_query,
        full=False,
        null=True,
        readonly=True)
    built_form_set_query = lambda bundle: bundle.obj.builtformset_set.all()

    built_form_sets = fields.ToManyField(
        'footprint.main.resources.built_form_resources.BuiltFormSetResource',
        attribute=built_form_set_query,
        full=False,
        null=True,
        readonly=True)

    def hydrate(self, bundle):
        """
            Set the user who created the ConfigEntity
        :param bundle:
        :return:
        """
        if not bundle.obj.id:
            bundle.obj.creator = self.resolve_user(bundle.request.GET)
        bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return super(BuiltFormResource, self).hydrate(bundle)

    def full_hydrate(self, bundle):
        # There's no memory of the bundle.data layer_style being a LayerStyle class,
        # so wrap it here. We can't do this in hydate or hydrate_medium_context because Tastypie
        # will overwrite the value after
        super(BuiltFormResource, self).full_hydrate(bundle)
        if bundle.obj.medium_context.__class__ == dict:
            bundle.obj.medium_context = LayerStyle(**bundle.obj.medium_context)
        return bundle

    def full_dehydrate(self, bundle, for_list=False):
        # Make sure new built_forms are added to the built_form_sets prior to dehydration
        # This normally happens in post_save, which is too late for the create case
        add_built_forms_to_built_form_sets([bundle.obj])
        return super(BuiltFormResource, self).full_dehydrate(bundle)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuiltForm.objects.filter(deleted=False).all().select_subclasses()
        resource_name = 'built_form'


class BuiltFormSetResource(FootprintResource):
    # These are readonly for now
    built_forms = ToManyFieldWithSubclasses(
        BuiltFormResource,
        attribute="built_forms",
        full=False,
        readonly=False)

    # built_forms = ToManyField(BuiltFormResource, 'built_forms', full=True)
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuiltFormSet.objects.filter(deleted=False)
        resource_name = 'built_form_set'

class ComponentPercentMixin(ModelResource):
    """
        Generically describes ComponentPercent
    """
    component_class = fields.CharField(attribute='component_class', null=False, readonly=True)
    container_class = fields.CharField(attribute='container_class', null=False, readonly=True)

class BuildingUseDefinitionResource(FootprintResource):

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuildingUseDefinition.objects.all()
        resource_name = 'building_use_definition'


class BuildingUsePercentResource(FootprintResource):

    building_attribute_set = fields.ToOneField('footprint.main.resources.built_form_resources.BuildingAttributeSetResource', 'building_attribute_set', full=False, null=False)
    building_use_definition = fields.ToOneField(BuildingUseDefinitionResource, 'building_use_definition', full=False, null=False)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuildingUsePercent.objects.all()
        resource_name = 'building_use_percent'


class AgricultureAttributeSetResource(FootprintResource):
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = AgricultureAttributeSet.objects.all()
        resource_name = 'agriculture_attribute_set'


class BuildingAttributeSetResource(FootprintResource):

    building_use_percents_query = lambda bundle: bundle.obj.buildingusepercent_set.all()
    def hydrate_m2m(self, bundle):
        for building_use_percent in bundle.data['building_use_percents']:
            # Fill in the backreference to building_attribute_set for this nested instance
            # TODO there must be a better to handle this
            # One option is to just not set the foreign_key on the client, since it becomes 0, and then set it belowing in add_builidng_use_percents
            building_use_percent['building_attribute_set'] = building_use_percent['building_attribute_set'].replace('/0/', '/%s/' % bundle.obj.id)
        return super(BuildingAttributeSetResource, self).hydrate_m2m(bundle)

    def add_building_use_percents(bundle, *building_use_percents):
        # Save the instances explicitly since they are based on the set query
        for building_use_percent in building_use_percents:
            building_use_percent.save()
    def remove_building_use_percents(bundle, *building_use_percents):
        for building_use_percent in building_use_percents:
            building_use_percent.delete()

    # The BuildingUsePercents
    building_use_percents = ToManyCustomAddField(BuildingUsePercentResource,
            attribute=building_use_percents_query,
            add=add_building_use_percents,
            remove=remove_building_use_percents,
            full=True,
            null=True)


    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuildingAttributeSet.objects.all()
        resource_name = 'building_attribute_set'


class BuiltFormExampleResource(FootprintResource):
    content = PickledDictField(attribute='content', null=True, blank=True, default=lambda: {})

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = BuiltFormExample.objects.all()
        resource_name = 'built_form_example'





class PrimaryComponentResource(BuiltFormResource):
    # Reverse Lookup of the each PlacetypeComponent that uses the PrimaryComponent and its percent of use
    primary_component_percent_query = lambda bundle: bundle.obj.primarycomponentpercent_set.all()
    primary_component_percent_set = fields.ToManyField(
        'footprint.main.resources.built_form_resources.PrimaryComponentPercentResource',
         attribute=primary_component_percent_query,
         full=True,
         null=True,
         readonly=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = PrimaryComponent.objects.filter(deleted=False)
        resource_name = 'primary_component'


class PrimaryComponentPercentResource(FootprintResource, ComponentPercentMixin):
    primary_component = fields.ToOneField('footprint.main.resources.built_form_resources.PrimaryComponentResource', 'primary_component', full=False, null=True)
    placetype_component = fields.ToOneField(
        'footprint.main.resources.built_form_resources.PlacetypeComponentResource', 'placetype_component',
        full=False, null=True, readonly=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = PrimaryComponentPercent.objects.all()
        resource_name = 'primary_component_percent'


class PlacetypeComponentCategoryResource(FootprintResource):
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = PlacetypeComponentCategory.objects.filter()
        resource_name = 'placetype_component_category'


class PlacetypeComponentResource(BuiltFormResource):

    component_category = fields.ToOneField(PlacetypeComponentCategoryResource, attribute='component_category')

    # The readonly through instances that show what primary components this placetype component contains and at what percent
    primary_component_percent_query = lambda bundle: bundle.obj.primarycomponentpercent_set.all()

    def add_primary_component_percents(bundle, *primary_component_percents):
        for primary_component_percent in primary_component_percents:
            primary_component_percent.placetype_component = bundle.obj
            primary_component_percent.save()

    def remove_primary_component_percents(bundle, *primary_component_percents):
        for primary_component_percent in primary_component_percents:
            primary_component_percent.delete()

    primary_component_percents = ToManyCustomAddField(
        PrimaryComponentPercentResource,
        attribute=primary_component_percent_query,
        add=add_primary_component_percents,
        remove=remove_primary_component_percents,
        full=True,
        null=True)

    # The readonly through instances that show what placetypes contain this placetype component and at what percent
    placetype_component_percent_query = lambda bundle: bundle.obj.placetypecomponentpercent_set.all()
    placetype_component_percent_set = fields.ToManyField(
       'footprint.main.resources.built_form_resources.PlacetypeComponentPercentResource',
       attribute=placetype_component_percent_query,
       full=True,
       null=True,
       readonly=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = PlacetypeComponent.objects.filter(deleted=False)
        resource_name = 'placetype_component'


class PlacetypeComponentPercentResource(FootprintResource, ComponentPercentMixin):
    placetype_component = fields.ToOneField('footprint.main.resources.built_form_resources.PlacetypeComponentResource', 'placetype_component', full=False, null=True)
    placetype = fields.ToOneField('footprint.main.resources.built_form_resources.PlacetypeResource', 'placetype',
                                  full=False, null=True, readonly=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = PlacetypeComponentPercent.objects.all()
        resource_name = 'placetype_component_percent'


class PlacetypeResource(BuiltFormResource):
    placetype_component_percent_query = lambda bundle: bundle.obj.placetypecomponentpercent_set.all()

    def add_placetype_component_percents(bundle, *placetype_component_percents):
        for placetype_component_percent in placetype_component_percents:
            placetype_component_percent.placetype = bundle.obj
            placetype_component_percent.save()

    def remove_placetype_component_percents(bundle, *placetype_component_percents):
        for placetype_component_percent in placetype_component_percents:
            placetype_component_percent.delete()

    placetype_component_percents = ToManyCustomAddField(PlacetypeComponentPercentResource,
                                                      attribute=placetype_component_percent_query,
                                                      add=add_placetype_component_percents,
                                                      remove=remove_placetype_component_percents,
                                                      full=True,
                                                      null=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = Placetype.objects.filter(deleted=False)
        resource_name = 'placetype'


class BuildingResource(PrimaryComponentResource):
    building_attribute_set = fields.ToOneField(BuildingAttributeSetResource, 'building_attribute_set', full=False, null=True)
    class Meta(PrimaryComponentResource.Meta):
        always_return_data = True
        queryset = Building.objects.filter(deleted=False)
        resource_name = 'building'


class BuildingTypeResource(PlacetypeComponentResource):
    building_attribute_set = fields.ToOneField(BuildingAttributeSetResource, 'building_attribute_set', full=False, null=True)
    class Meta(PlacetypeComponentResource.Meta):
        always_return_data = True
        queryset = BuildingType.objects.filter(deleted=False)
        resource_name = 'building_type'


class UrbanPlacetypeResource(PlacetypeResource):
    building_attribute_set = fields.ToOneField(BuildingAttributeSetResource, 'building_attribute_set', full=False, null=True)
    class Meta(PlacetypeResource.Meta):
        always_return_data = True
        queryset = UrbanPlacetype.objects.filter(deleted=False)
        resource_name = 'urban_placetype'


class CropResource(PrimaryComponentResource):
    agriculture_attribute_set = fields.ToOneField(AgricultureAttributeSetResource, 'agriculture_attribute_set', full=False, null=True)
    class Meta(PrimaryComponentResource.Meta):
        always_return_data = True
        queryset = Crop.objects.filter(deleted=False)
        resource_name = 'crop'


class CropTypeResource(PlacetypeComponentResource):
    agriculture_attribute_set = fields.ToOneField(AgricultureAttributeSetResource, 'agriculture_attribute_set', full=False, null=True)
    class Meta(PlacetypeComponentResource.Meta):
        always_return_data = True
        queryset = CropType.objects.filter(deleted=False)
        resource_name = 'crop_type'


class LandscapeTypeResource(PlacetypeResource):
    agriculture_attribute_set = fields.ToOneField(AgricultureAttributeSetResource, 'agriculture_attribute_set', full=False, null=True)
    class Meta(PlacetypeResource.Meta):
        always_return_data = True
        queryset = LandscapeType.objects.filter(deleted=False)
        resource_name = 'landscape_type'
