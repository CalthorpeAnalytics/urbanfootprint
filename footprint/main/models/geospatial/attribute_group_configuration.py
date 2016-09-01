
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

from django.db import models
from picklefield import PickledObjectField
from footprint.main.lib.functions import remove_keys, map_to_dict
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.permissions import Permissions

__author__ = 'calthorpe_analytics'

class AttributeGroupConfiguration(Permissions):

    attribute_group = models.ForeignKey('AttributeGroup', null=False)
    feature_behavior = models.ForeignKey('FeatureBehavior', null=False)

    # A dictionary that maps the AttributeGroup's attributes to FeatureBehavior's Feature class fields by name to the attributes
    # For instance if the attributes in AttributeGroup are ['relation', 'primitive'] and a
    # feature class had the field land_use_defintion and lu12, then the dictionary would be
    # dict(relation=land_use_definition, primitive=lu12)
    # If not defined then the attribute names are assumed to match (unlikely)
    attribute_mapping = PickledObjectField(null=True)

    @property
    def attribute_names(self):
        # introspect the attribute_group_class and cache the results. Return the names
        return map(lambda field: field.name, self.attribute_fields)

    @property
    def attribute_fields(self):
        # introspect the attribute_group_class and cache the results. Return the fields
        feature_class = self.feature_behavior.db_entity.feature_class
        field_dict = map_to_dict(lambda field: [field.name, field], feature_class._meta.fields)
        return map(lambda attribute_name: field_dict[self.attribute_mapping.get(attribute_name, attribute_name)], self.attribute_group.attribute_keys)

    objects = GeoInheritanceManager()
    class Meta(object):
        abstract = False
        app_label = 'main'
        # Custom permissions in addition to the default add, change, delete
        permissions = (
            ('view_attributegroupconfiguration', 'View AttributeGroupConfiguration'),
        )
