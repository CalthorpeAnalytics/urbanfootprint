# coding=utf-8

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

import logging
from django.db import models
from picklefield import PickledObjectField
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.presentation.style_attribute import ZoomLevelStyleValueContext


__author__ = 'calthorpe_analytics'
logger = logging.getLogger(__name__)

class LayerStyle(Medium):
    """
        Represents a Django-style template that needs additional data to be a usable Medium. It thus references a
        LayerStyle which might be XML, JSON, etc that has been parsed to python and can be used to populate the
        template. The Django style template string with wildcards (handlebars) must be stored in the content property.
        The template.layer_style contains the default python dictionary to use to fill in the handlebars ({{ }})
        in the template.

        For Layers and Results, their medium attribute is a Template instance, whose content contains a cartocss
        and css template and whose layer_style is a LayerStyle instance which completes the template.
    """
    objects = GeoInheritanceManager()
    # class properties used as defaults for subclass declarations
    geometry_type = models.CharField(max_length=200, null=True, blank=True)
    html_class = models.CharField(max_length=200, null=True, blank=True)

    style_attributes = models.ManyToManyField('StyleAttribute', null=True)

    @property
    def defined_attributes(self):
        """
            Convenience method to return the attributes defined in the StyleAttributes
        :return:
        """
        return filter(lambda x: x is not None, map(lambda style_attribute: style_attribute.attribute,
                                                   self.style_attributes.all()))


    @property
    def limited_content(self):
        """
            Hides all content from the API until we need it
        :return:
        """
        return {}

    class Meta(object):
        app_label = 'main'
