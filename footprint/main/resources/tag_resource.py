
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

from django.db.models import Count
from tastypie.resources import ModelResource
from footprint.main.models.tag import Tag
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class TagResource(ModelResource):
    """
        When tags are returned as ToMany properties of other classes, like DbEntity, they are simplified to an array of strings. I'm not sure what format they should be for individual requests. Maybe only lists should be supported
    """
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = Tag.objects.all()

class BuiltFormTagResource(ModelResource):
    """
        Simple filter for tags of BuiltForms
    """
    class Meta(FootprintResource.Meta):
        resource_name = 'built_form_tag'
        always_return_data = True
        queryset = Tag.objects.annotate(
            count=Count('builtform')).filter(count__gt=0)

class DbEntityTagResource(ModelResource):
    """
        Simple filter for tags of BuiltForms
    """
    class Meta(FootprintResource.Meta):
        resource_name = 'db_entity_tag'
        always_return_data = True
        queryset = Tag.objects.annotate(
            count=Count('dbentity')).filter(count__gt=0)
