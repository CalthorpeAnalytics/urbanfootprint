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
from django.db.models import Sum
from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.constants import Constants
from django.contrib.gis.db import models
from footprint.main.models.built_form.urban.building_use_definition import BuildingUseDefinition
from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)

class BuildingAttributeSet(models.Model):
    """
    Attributes of a :models:`main.Building`, :models:`main.BuildingType`, or :models:`main.Placetype`,
    including a reference to its uses through :model:`built_form.building_use_percent.BuildingUsePercent`.
    """
    objects = GeoInheritanceManager()

    class Meta(object):
        abstract = False
        app_label = 'main'

    def attributes(self):
        return "building"

    ## fields applicable at the Building level and above :
    building_uses = models.ManyToManyField(BuildingUseDefinition, through="BuildingUsePercent")

    address = models.CharField(max_length=200, null=True, blank=True, default=None)
    website = models.CharField(max_length=300, null=True, blank=True, default=None)

    vacancy_rate = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    household_size = models.DecimalField(max_digits=5, decimal_places=3, default=0)

    #fields related to the building and the associated lot attributes
    lot_size_square_feet = models.DecimalField(max_digits=14, decimal_places=7, default=0)
    floors = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    total_far = models.DecimalField(max_digits=10, decimal_places=7, default=0)

    surface_parking_spaces = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    above_ground_structured_parking_spaces = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    below_ground_structured_parking_spaces = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    #components to the hardscape area, the hardscape other field is imported from building csv while parking and
    # building footprint square feet are calculated from import variables in this class
    average_parking_space_square_feet = models.DecimalField(max_digits=14, decimal_places=4, null=True, default=0)
    surface_parking_square_feet = models.DecimalField(max_digits=14, decimal_places=4, null=True, default=0)
    building_footprint_square_feet = models.DecimalField(max_digits=14, decimal_places=4, null=True, default=0)
    hardscape_other_square_feet = models.DecimalField(max_digits=14, decimal_places=4, null=True, default=0)

    #the softscape is the remaining non-hardscape area. The irrigated percentage represents the area of the hardscape
    #that is irrigated.
    irrigated_softscape_square_feet = models.DecimalField(max_digits=14, decimal_places=3, null=True, default=0)
    nonirrigated_softscape_square_feet = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    irrigated_percent = models.DecimalField(max_digits=14, decimal_places=10, default=0)

    residential_irrigated_square_feet = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=0)
    commercial_irrigated_square_feet = models.DecimalField(max_digits=9, decimal_places=2, null=True, default=0)

    gross_net_ratio = models.DecimalField(max_digits=14, decimal_places=7, default=1)

    # methods to get at derived facts about building attributes
    def calculate_derived_fields(self):
        """
        takes the basic input data about the building attributes of a built form, and calculates useful derived fields
        for use by the flat_built_forms exporter and eventually in integrated UF analyses
        :return:
        """
        for building_use_percent in self.buildingusepercent_set.all():
            if not building_use_percent.percent:
                building_use_percent.delete()
                continue
            if self.building_set.count() > 0:
                building_use_percent.calculate_derived_attributes()

        commercial_uses = self.buildingusepercent_set.filter(
            building_use_definition__name__in=Keys.COMMERCIAL_SUBCATEGORIES
        )
        residential_uses = self.buildingusepercent_set.filter(
            building_use_definition__name__in=Keys.RESIDENTIAL_SUBCATEGORIES
        )

        percent_residential = residential_uses.aggregate(Sum('percent'))['percent__sum'] or 0
        percent_commercial = commercial_uses.aggregate(Sum('percent'))['percent__sum'] or 0

        lot_size_to_per_acre_density_factor = Constants.SQUARE_FEET_PER_ACRE / self.lot_size_square_feet if self.lot_size_square_feet > 0 else 0

        self.residential_irrigated_square_feet = float(percent_residential or 0) * \
            float(self.irrigated_softscape_square_feet or 0) * float(lot_size_to_per_acre_density_factor)

        self.commercial_irrigated_square_feet = float(percent_commercial or 0) * \
            float(self.irrigated_softscape_square_feet or 0) * float(lot_size_to_per_acre_density_factor)

        self.save()

    def get_unit_density(self, use_percent_set):
        return sum(building_use.unit_density for building_use in use_percent_set)
