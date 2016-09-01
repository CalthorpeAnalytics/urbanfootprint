
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
from django.db.models import CharField, ManyToManyField
from picklefield.fields import PickledObjectField

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.scoped_key import ScopedKey
from footprint.main.models.keys.keys import Keys
from footprint.main.utils.model_utils import model_dict


__author__ = 'calthorpe_analytics'

class AttributeGroup(ScopedKey):
    objects = GeoInheritanceManager()
    class Meta(object):
        abstract = False
        app_label = 'main'
        # Custom permissions in addition to the default add, change, delete
        permissions = (
            ('view_attribute_group', 'View AttributeGroup'),
        )

    # An array of attribute identifiers. These will normally be mapped to the actually attribute names
    # of a certain class in AttributeGroupConfiguration.attribute_mappings
    attribute_keys = PickledObjectField(default=lambda:[], null=False)

    # AttributePermission allow for fine-grained permission to the attributes of the AttributeGroup
    # This is only needed if individual attributes need different permissions for a single user
    # This probably only happens for a visual grouping of attributes. For instance, a group
    # that has a created date attribute but also editable attribute.
    attribute_permissions = ManyToManyField('main.AttributePermission')

class AttributePermission(models.Model):
    """
        Permissions may be added to these to specify fine-grained access on an attribute
    """
    attribute_name = CharField(max_length=100, null=False)

    class Meta(object):
        abstract = False
        app_label = 'main'

def update_or_create_attribute_group(attribute_group):
    """
        Update or create a behavior based on the given behavior
    """

    return AttributeGroup.objects.update_or_create(
        key=attribute_group.key,
        defaults=model_dict(attribute_group, omit_fields=['key'])
    )[0]

class AttributeGroupKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'attribute_group'
