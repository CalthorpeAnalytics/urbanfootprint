
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
from footprint.main.models.category import Category
from footprint.main.resources.footprint_resource import FootprintResource

__author__ = 'calthorpe_analytics'

class CategoryResource(ModelResource):
    class Meta(FootprintResource.Meta):
        always_return_data = True
        queryset = Category.objects.all()
        filtering = {
            # Accept the django query id__in
            "key": ('in','exact'),
        }

class ConfigEntityCategoryResource(ModelResource):
    """
        Simple filter for categories of ConfigEntities
    """
    class Meta(FootprintResource.Meta):
        resource_name = 'config_entity_category'
        always_return_data = True
        queryset = Category.objects.annotate(
            count=Count('configentity')).filter(count__gt=0)

class DbEntityCategoryResource(ModelResource):
    """
        Simple filter for categories of DbEntities
    """
    class Meta(FootprintResource.Meta):
        resource_name = 'db_entity_category'
        always_return_data = True
        queryset = Category.objects.annotate(
            count=Count('dbentity')).filter(count__gt=0)
