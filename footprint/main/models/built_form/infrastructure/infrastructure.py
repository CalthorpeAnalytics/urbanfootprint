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



__author__ = 'calthorpe_analytics'

from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.infrastructure_attributes import InfrastructureAttributeSet
class Infrastructure(InfrastructureAttributeSet, BuiltForm):
    """
        Infrastructure is the container for streets, parks, detention/utilities
    """

    class Meta(object):
        app_label = 'main'

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name
