
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
from tastypie.fields import ListField
from footprint.main.models.presentation.layer_style import LayerStyle
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.presentation.style_attribute import StyleAttribute
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class StyleAttributeResource(FootprintResource):

    style_value_contexts = ListField(attribute='style_value_contexts', null=True, blank=True, default=lambda:{})

    def full_hydrate(self, bundle):
        """
            Sets the style value contexts
        :param bundle:
        :return:
        """
        if hasattr(bundle.obj, 'style_value_contexts'):
            bundle = super(StyleAttributeResource, self).full_hydrate(bundle)
            bundle.obj.style_value_contexts = bundle.data['style_value_contexts']
        return bundle

    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = StyleAttribute.objects.all()

class MediumResource(FootprintResource):
    content = PickledDictField(attribute='limited_content', null=True, blank=True, default=lambda:{}, readonly=True)
    style_attributes = fields.ToManyField(StyleAttributeResource, 'style_attributes', full=True, null=True)

    class Meta(FootprintResource.Meta):
        always_return_data = True
        resource_name = 'medium'
        queryset = LayerStyle.objects.all()



class LayerStyleResource(MediumResource):

    class Meta(MediumResource.Meta):
        always_return_data = True
        resource_name = 'layer_style'
        queryset = LayerStyle.objects.all()
