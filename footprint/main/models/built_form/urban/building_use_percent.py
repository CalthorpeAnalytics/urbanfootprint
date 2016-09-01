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

from django.db import models

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.mixins.percent import Percent
from footprint.main.models.constants import Constants
from footprint.main.models.keys.keys import Keys


__author__ = 'calthorpe_analytics'


class BuildingUsePercent(Percent):
    """
    Describes the percent of :model:`main.BuildingUseDefinition` present in a particular
    :model:`main.BuildingAttributeSet`.
    """
    objects = GeoInheritanceManager()

    building_attribute_set = models.ForeignKey('BuildingAttributeSet')
    building_use_definition = models.ForeignKey('BuildingUseDefinition')

    # describes the ratio : use areas / (common areas + use areas)
    efficiency = models.DecimalField(max_digits=6, decimal_places=4, default=.85)

    # describes the number of square feet per unit ( dwelling unit or employee ) of the building
    square_feet_per_unit = models.DecimalField(max_digits=11, decimal_places=3, null=True)

    ## derived attributes
    # area measured in acres
    floor_area_ratio = models.DecimalField(max_digits=12, decimal_places=10, null=True)
    unit_density = models.DecimalField(max_digits=16, decimal_places=10, null=True)

    # area measured in square feet
    gross_built_up_area = models.DecimalField(max_digits=13, decimal_places=3, null=True)
    net_built_up_area = models.DecimalField(max_digits=13, decimal_places=3, null=True)

    class Meta(object):
        app_label = 'main'
    def __unicode__(self):
        use = self.building_use_definition
        return use.name

    def calculate_derived_attributes(self):
        """
        Calculates floor_area_ratio, gross_built_up_area, net_built_up_area, and use_density based on the
        inputs self.built_form.total_far, self.built_form.gross_net_ratio, self.percent, self.efficiency, and
        either self.square_feet_per_unit or self.built_form.residential_average_lot_size (the latter for detached
        residential building_use_definitions).
        """

        parcel_far = self.building_attribute_set.total_far  # / self.building_attribute_set.gross_net_ratio
        self.floor_area_ratio = self.percent * parcel_far

        if self.building_use_definition.name == Keys.DETACHED_SINGLE_FAMILY:
            self.gross_built_up_area = self.square_feet_per_unit * (Constants.SQUARE_FEET_PER_ACRE / self.building_attribute_set.lot_size_square_feet)
        else:
            self.gross_built_up_area = self.floor_area_ratio * self.building_attribute_set.lot_size_square_feet * \
                (Constants.SQUARE_FEET_PER_ACRE / self.building_attribute_set.lot_size_square_feet)

        self.net_built_up_area = self.gross_built_up_area * self.efficiency

        percent_of_parcel_acres = self.percent  # / self.building_attribute_set.gross_net_ratio

        if self.building_use_definition.name == Keys.DETACHED_SINGLE_FAMILY and self.building_attribute_set.lot_size_square_feet:
            residential_lots_per_acre = Constants.SQUARE_FEET_PER_ACRE / self.building_attribute_set.lot_size_square_feet
            self.unit_density = percent_of_parcel_acres * residential_lots_per_acre
        else:
            self.unit_density = self.net_built_up_area / self.square_feet_per_unit

        self.save()
