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


import itertools
from footprint.main.mixins.built_form_aggregate import BuiltFormAggregate

__author__ = 'calthorpe_analytics'

from footprint.main.models.built_form.urban.building_use_percent import BuildingUsePercent
from django.db.models import Sum
from collections import defaultdict


class BuildingAttributeAggregate(BuiltFormAggregate):
    """
    An abstract class that describes a high-level built form that has a
    :model:`built_forms.building_attribute_set.BuildingAttributeSet`, defines methods to aggregate attributes
    the classes :model:`built_forms.buildingtype.BuildingType` and :model:`built_forms.placetype.Placetype`
    according to the mix of their components.
    """
    class Meta:
        abstract = True
        app_label = 'main'

    AGGREGATE_ATTRIBUTES = [
        'lot_size_square_feet',
        'floors',
        'total_far',
        'vacancy_rate',
        'household_size',
        'surface_parking_spaces',
        'above_ground_structured_parking_spaces',
        'below_ground_structured_parking_spaces',
        'average_parking_space_square_feet',
        'surface_parking_square_feet',
        'building_footprint_square_feet',
        'hardscape_other_square_feet',
        'irrigated_softscape_square_feet',
        'nonirrigated_softscape_square_feet',
        'irrigated_percent'
        ]

    def complete_aggregate_definition(self):
        """
        Checks that all the components have been established, to avoid redundant calculations
        :return: True or False
        """

        if self.get_all_component_percents().aggregate(Sum('percent'))['percent__sum'] < .98:
            return False
        else:
            return True

    def get_all_component_percents(self):
        """
        Identifies the component class and returns the component_percent objects representing the relationship
        between the components and the BuildingAggregate
        :return: BuildingAggregate component_percents
        """
        component_percent_field = self.get_component_field().through.__name__
        component_percents = getattr(self, "{0}_set".format(component_percent_field.lower())).all()
        return component_percents

    def aggregate_building_attribute_set(self):
        """
        Grabs the component buildings of the BuildingAggregate and does a weighted average of their core attributes,
        before passing the building_attribute_set to the calculate_derived_fields() method.
        """
        if not hasattr(self, 'building_attribute_set'):
            return

        self.building_attribute_set.gross_net_ratio = self.calculate_gross_net_ratio()

        for attribute in self.AGGREGATE_ATTRIBUTES:
            if attribute in ['vacancy_rate', 'household_size']:
                component_percents = sum(map(lambda component_percent: component_percent.percent,
                    filter(lambda component_percent: (getattr(component_percent.component().building_attribute_set, attribute) or 0) > 0,
                           self.get_all_component_percents())))

                attribute_value = sum(map(lambda component_percent:
                 getattr(component_percent.component().building_attribute_set, attribute) * (component_percent.percent / component_percents),
                    filter(lambda component_percent: (getattr(component_percent.component().building_attribute_set, attribute) or 0) > 0,
                           self.get_all_component_percents())))


            else:
                attribute_value = sum([
                    (getattr(component_percent.component().building_attribute_set, attribute) or 0) *
                    component_percent.percent for component_percent in self.get_all_component_percents()
                ])

            setattr(self.building_attribute_set, attribute, attribute_value)

        self.building_attribute_set.save()
        self.aggregate_building_uses()
        self.building_attribute_set.calculate_derived_fields()

        self.no_post_save_publishing = True
        self.save()
        self.no_post_save_publishing = False

    def aggregate_building_uses(self):
        """
        Aggregates the attributes of the :model:`main.BuildingUsePercent` objects associated with the components
        of the aggregate built form, and creates new :model:`main.BuildingUsePercent` objects associated with the
        aggregate object.

        For each type of use (single family large lot, restaurant, etc) that is present in the components of the
        aggregate being assembled, a new BuildingUsePercent object is created and connected to the aggregate's
        BuildingAttributes. Attributes of the new BuildingUsePercent object are derived from the attributes of
        BuildingUsePercent objects in the components.

        Attributes are averaged with the method:
            Σ(attribute_value * component_use_percent * component_percent) / aggregate_use_percent

        where
            component_percent = the percent of the component within the aggregate
            component_use_percent = the percent of the use within the component
            aggregate_use_percent = the percent of the use within the aggregate

        for each use matching the current type of use in all of the components of the aggregate

        """

        def get_component_percent(use_percent, component_percents):
            """
            gets the component_percent for the component_use_percent
            :param use_percent:
            :return:
            """
            building_attribute_set = use_percent.building_attribute_set
            components = [component_percent for component_percent in component_percents
                          if component_percent.component().building_attribute_set == building_attribute_set]
            return components[0].percent

        #first collect all component percents, component use percents, and component use definition and remove any from previous saves.
        component_percents = self.get_all_component_percents()

        component_use_percents = list(itertools.chain.from_iterable([
            list(component_percent.component().building_attribute_set.buildingusepercent_set.all())
            for component_percent in component_percents
        ]))

        component_use_definitions = set([
            component_use_percent.building_use_definition for component_use_percent in component_use_percents
        ])

        BuildingUsePercent.objects.filter(
                building_attribute_set=self.building_attribute_set).exclude(
                building_use_definition__in=component_use_definitions
        ).delete()

        component_percents = self.get_all_component_percents()

        component_use_percents = list(itertools.chain.from_iterable([
            list(component_percent.component().building_attribute_set.buildingusepercent_set.all())
            for component_percent in component_percents
        ]))

        component_use_definitions = set([
            component_use_percent.building_use_definition for component_use_percent in component_use_percents
        ])

        for use_definition in component_use_definitions:

            aggregate_use_attributes = defaultdict(lambda: 0.0000000000000000000000000)

            # makes a list of BuildingUsePercent objects of the use currently being aggregated
            use_percent_components = [component_use_percent for component_use_percent in component_use_percents
                                      if component_use_percent.building_use_definition.name == use_definition.name]

            aggregate_use_attributes['percent'] = sum([
                component_use_percent.percent *
                get_component_percent(component_use_percent, component_percents)
                for component_use_percent in use_percent_components
            ])

            attributes = use_definition.get_attributes()

            for attr in attributes:
                if attr in ['efficiency', 'square_feet_per_unit']:
                    aggregate_use_attributes[attr] = sum([

                        getattr(component_use_percent, attr) *
                        component_use_percent.percent *
                        get_component_percent(component_use_percent, component_percents)

                        for component_use_percent in use_percent_components

                    ]) / aggregate_use_attributes['percent']

                else:
                    aggregate_use_attributes[attr] = sum([
                        getattr(component_use_percent, attr) *
                        get_component_percent(component_use_percent, component_percents)
                        for component_use_percent in use_percent_components
                    ])

            BuildingUsePercent.objects.update_or_create(
                building_attribute_set=self.building_attribute_set,
                building_use_definition=use_definition,
                defaults=aggregate_use_attributes
            )
