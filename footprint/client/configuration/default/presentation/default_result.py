
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from string import capitalize
from footprint.client.configuration.fixture import ResultConfigurationFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.keys.content_type_key import ContentTypeKey
from footprint.main.publishing.result_initialization import ResultLibraryConfiguration, \
    ResultLibraryKey, ResultMediumKey
from footprint.main.models.config.scenario import Scenario
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.utils.utils import create_media_subdir


class DefaultResultConfigurationFixtures(DefaultMixin, ResultConfigurationFixture):

    def result_libraries(self):
        """
            Used to update or create ResultLibraries per ConfigEntity instance
            Returns the result library(ies) scoped for the class of self.config_entity
        :return:
        """
        return FixtureList(map(lambda result_library_key:
            ResultLibraryConfiguration(
                key=result_library_key,
                name='{0} %s Result Library' % capitalize(result_library_key),
                description='The %s result library for {0}' % capitalize(result_library_key)
            ),
            [ResultLibraryKey.DEFAULT, ResultLibraryKey.APPLICATION, ResultLibraryKey.WATER, ResultLibraryKey.ENERGY, ResultLibraryKey.VMT,
             ResultLibraryKey.FISCAL, ResultLibraryKey.AGRICULTURE_ANALYSIS, ResultLibraryKey.PUBLIC_HEALTH]
        ))

    def results(self):
        """
            Used to update or create Results per ConfigEntity instance
            Returns the result library(ies) scoped for the class of self.config_entity.
            The Result will belong to the ResultLibrary specified by result_library_key

            To update this in the DB, use footprint_init --skip --result
        :return:
        """
        return []

    def update_or_create_media(self, config_entity, db_entity_keys=None):
        """
        :return: Creates a Media used by the default results
        """

        # Make sure the styles directory exists so that Result css can be stored there
        # TODO do we need to store styles in the filesystem. Or can they just be in the DB??
        create_media_subdir('styles')

        # Used by any Result that has no explicit Medium
        Medium.objects.update_or_create(
            key=ResultMediumKey.DEFAULT,
            name=ResultMediumKey.DEFAULT,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#A0A2A3', '#413e40']
                },
                'description': 'Default'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.BASE_EMPLOYMENT_BY_TYPE,
            name=ResultMediumKey.BASE_EMPLOYMENT_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['purple', 'pink']
                },
                'description': 'Base: Employment by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.BASE_DWELLING_UNITS_BY_TYPE,
            name=ResultMediumKey.BASE_DWELLING_UNITS_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['yellow', 'red']
                },
                'description': 'Base: Dwelling Units by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.INCREMENTS,
            name=ResultMediumKey.INCREMENTS,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['yellow', 'purple']
                },
                'description': 'Increments'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.INCREMENTS_EMPLOYMENT_BY_TYPE,
            name=ResultMediumKey.INCREMENTS_EMPLOYMENT_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['purple', 'pink']
                },
                'description': 'Increments: Employment by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.INCREMENTS_DWELLING_UNITS_BY_TYPE,
            name=ResultMediumKey.INCREMENTS_DWELLING_UNITS_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['yellow', 'red']
                },
                'description': 'Increments: Dwelling Units by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.END_STATE,
            name=ResultMediumKey.END_STATE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['yellow', 'purple']
                },
                'description': 'End State'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.END_STATE_EMPLOYMENT_BY_TYPE,
            name=ResultMediumKey.END_STATE_EMPLOYMENT_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['purple', 'pink']
                },
                'description': 'End State: Employment by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.END_STATE_DWELLING_UNITS_BY_TYPE,
            name=ResultMediumKey.END_STATE_DWELLING_UNITS_BY_TYPE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['yellow', 'red']
                },
                'description': 'End State: Dwelling Units by Type'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.WATER_INDOOR_OUTDOOR,
            name=ResultMediumKey.WATER_INDOOR_OUTDOOR,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#05B8CC', '#00688B']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.WATER_TOTAL,
            name=ResultMediumKey.WATER_TOTAL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#05B8CC', '#00688B']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.WATER_COSTS_TOTAL,
            name=ResultMediumKey.WATER_COSTS_TOTAL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#05B8CC', '#00688B']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.VMT_PER_CAPITA,
            name=ResultMediumKey.VMT_PER_CAPITA,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#aa8cc5', '#3b1261']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.VMT_FUEL,
            name=ResultMediumKey.VMT_FUEL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#aa8cc5', '#3b1261']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.VMT_COSTS,
            name=ResultMediumKey.VMT_COSTS,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#aa8cc5', '#3b1261']
                },
                'description': 'water colors'}
        ),
        Medium.objects.update_or_create(
            key=ResultMediumKey.VMT_EMISSIONS,
            name=ResultMediumKey.VMT_EMISSIONS,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#aa8cc5', '#3b1261']
                },
                'description': 'water colors'}
        ),
        Medium.objects.update_or_create(
            key=ResultMediumKey.ENERGY_TOTAL,
            name=ResultMediumKey.ENERGY_TOTAL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#dea66c', '#a05508']
                },
                'description': 'water colors'}
        ),
        Medium.objects.update_or_create(
            key=ResultMediumKey.ENERGY_RES_USE,
            name=ResultMediumKey.ENERGY_RES_USE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#dea66c', '#a05508']
                },
                'description': 'water colors'}
        ),
        Medium.objects.update_or_create(
            key=ResultMediumKey.ENERGY_COM_USE,
            name=ResultMediumKey.ENERGY_COM_USE,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#dea66c', '#a05508']
                },
                'description': 'water colors'}
        )

        Medium.objects.update_or_create(
            key=ResultMediumKey.ENERGY_COSTS_TOTAL,
            name=ResultMediumKey.ENERGY_COSTS_TOTAL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#dea66c', '#a05508']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.ENERGY_EMISSIONS_TOTAL,
            name=ResultMediumKey.ENERGY_EMISSIONS_TOTAL,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#dea66c', '#a05508']
                },
                'description': 'water colors'}
        ),

        Medium.objects.update_or_create(
            key=ResultMediumKey.FISCAL_CHART,
            name=ResultMediumKey.FISCAL_CHART,
            defaults={
                'content_type': ContentTypeKey.PYTHON,
                'content': {
                    'colorRange': ['#84c284', '#236b23']
                },
                'description': 'water colors'}
        )
