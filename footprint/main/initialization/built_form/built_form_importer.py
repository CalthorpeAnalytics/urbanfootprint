
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

import importlib
import os

from django.template.defaultfilters import slugify
from django.conf import settings

from footprint.client.configuration.default.built_form.default_import_crop import ImportCrop
from footprint.main.initialization.built_form.built_form_derivatives import BuiltFormDerivatives
from footprint.main.initialization.built_form.import_primary_component import ImportPrimaryComponent
from footprint.main.initialization.built_form.import_placetype import ImportedPlacetype
from footprint.main.lib.functions import map_to_dict, remove_keys
from footprint.main.models import AgricultureAttributeSet
from footprint.main.models.built_form.urban.urban_placetype import Placetype
from footprint.main.models.built_form.placetype_component_percent import PlacetypeComponentPercent
from footprint.main.models.built_form.urban.building_use_percent import BuildingUsePercent
from footprint.main.models.built_form.primary_component_percent import PrimaryComponentPercent
from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.models.built_form.placetype_component import PlacetypeComponent
from footprint.main.models.keys.keys import Keys


class BuiltFormImporter(BuiltFormDerivatives):
    def __init__(self):
        super(BuiltFormImporter, self).__init__()
        self.dir = os.path.dirname(__file__)

    def built_form_path(self, client):
        # TODO Let the client resolve this via a fixture
        client_built_form_path = "{ROOT_PATH}/footprint/client/configuration/{client}/built_form/import_csv".format(
            ROOT_PATH=settings.ROOT_PATH, client=client)

        return client_built_form_path

    def load_crops_csv(self, client):
        """
        :param self.dir csv file self.directory
        :return: ImportedBuilding objects imported from UrbanFootprint v0.1 Built Form default set, csv or a custom
        set defined for the client
        """
        # Load building attribute data from a csv and used it to create Building instances
        path = '{0}/crops.csv'.format(self.built_form_path(client))
        if not os.path.exists(path):
            return []
        file = open(path, "rU")
        imported_crops = ImportCrop.import_from_file(file)  # import_from_filename(path)
        return imported_crops

    def load_buildings_csv(self, client):
        """
        :param self.dir csv file self.directory
        :return: ImportedBuilding objects imported from UrbanFootprint v0.1 Built Form default set, csv or a custom
        set defined for the client
        """
        # Load building attribute data from a csv and used it to create Building instances
        path = '{0}/buildings.csv'.format(self.built_form_path(client))
        if not os.path.exists(path):
            return []
        file = open(path, "rU")
        imported_buildings = ImportPrimaryComponent.import_from_file(file) #import_from_filename(path)
        return imported_buildings

    def load_croptypes(self, client):
        """
        :return: ImportedBuildingtype objects imported from UrbanFootprint v0.1 Built Form default set, csv or a custom
        set defined for the client
        """
        client_built_form = "footprint.client.configuration.{client}.built_form.{client}_import_placetype_component".format(
            ROOT_PATH=settings.ROOT_PATH, client=client)
        if hasattr(importlib.import_module(client_built_form), 'CROP_TYPES'):
            return importlib.import_module(client_built_form).CROP_TYPES
        else:
            return {}

    def load_buildingtype_csv(self, client):
        """
        :return: ImportedBuildingtype objects imported from UrbanFootprint v0.1 Built Form default set, csv or a custom
        set defined for the client
        """
        if not os.path.exists(self.built_form_path(client)):
            return []
        client_built_form = "footprint.client.configuration.{client}.built_form.{client}_import_placetype_component".format(
            ROOT_PATH=settings.ROOT_PATH, client=client)
        importer_module = importlib.import_module(client_built_form)
        placetype_component_importer = importer_module.ImportPlacetypeComponent
        imported_buildingtypes = placetype_component_importer.import_from_filename(
            '{0}/buildingtypes.csv'.format(self.built_form_path(client)))
        return imported_buildingtypes

    def load_placetype_csv(self, client):
        """
        :return: ImportedPlacetype objects imported from UrbanFootprint v0.1 Built Form default set, csv or a custom
        set defined for the client
        """
        if not os.path.exists(self.built_form_path(client)):
            return []
        imported_placetypes = ImportedPlacetype.import_from_filename(
            '{0}/placetypes.csv'.format(self.built_form_path(client)))
        return imported_placetypes

    def construct_primary_components(self, client='default'):
        """
        :return: Dictionary keyed by Building name and valued by Building objects (UrbanFootprint v0.1 Built
        Form default set)
        """
        primary_components = {}
        for import_primary_component in self.load_crops_csv(client):
            fields = AgricultureAttributeSet._meta.fields
            agriculture_attribute_set = remove_keys(map_to_dict(
                lambda field: [field.attname, getattr(import_primary_component, field.attname)],
                fields), ['id'])
            agriculture_attribute_set['name'] = import_primary_component.name
            if import_primary_component.name in primary_components:
                raise Exception("Duplicate entry for primary component: " + import_primary_component.name)
            primary_components[import_primary_component.name] = dict(agriculture_attribute_set=agriculture_attribute_set)

        for import_primary_component in self.load_buildings_csv(client):
            building_attribute_set = dict(
                name=import_primary_component.name,
                address=import_primary_component.address,
                website=import_primary_component.website,
                lot_size_square_feet=import_primary_component.lot_size_square_feet,
                floors=import_primary_component.floors,
                total_far=import_primary_component.total_far,
                average_parking_space_square_feet=import_primary_component.average_parking_space_square_feet,
                surface_parking_spaces=import_primary_component.surface_parking_spaces,
                below_ground_structured_parking_spaces=import_primary_component.below_ground_parking_spaces,
                above_ground_structured_parking_spaces=import_primary_component.above_ground_parking_spaces,
                building_footprint_square_feet=import_primary_component.building_footprint_square_feet,
                surface_parking_square_feet=import_primary_component.surface_parking_square_feet,
                hardscape_other_square_feet=import_primary_component.hardscape_other_square_feet,
                irrigated_softscape_square_feet=import_primary_component.irrigated_softscape_square_feet,
                nonirrigated_softscape_square_feet=import_primary_component.nonirrigated_softscape_square_feet,
                irrigated_percent=import_primary_component.irrigated_percent,
                vacancy_rate=import_primary_component.vacancy_rate,
                household_size=import_primary_component.household_size
            )
            if import_primary_component.name in primary_components:
                raise Exception("Duplicate entry for primary component: " + import_primary_component.name)
            primary_components[import_primary_component.name] = dict(building_attribute_set=building_attribute_set)

        return primary_components

    def construct_placetype_components(self, client):
        """
        :return: A dict keyed by BuildingType name and valued by BuildingType objects (UrbanFootprint v0.1 Built Form
        default set)
        """
        placetype_components = {}
        buildingtype_imports = self.load_buildingtype_csv(client)
        for b in buildingtype_imports:
            placetype_components[b.name] = dict(
                type='building_type',
                key='bt__' + slugify(b.name).replace('-', '_'),
                name=b.name,
                color=b.color if b.color else '#B0B0B0',
                component_category=b.category
            )

        for croptype, attributes in self.load_croptypes(client).items():
            placetype_components[croptype] = dict(
                type='crop_type',
                key='ct__' + slugify(croptype).replace('-', '_'),
                name=croptype,
                component_category=Keys.BUILDINGTYPE_AGRICULTURAL
            )


        return placetype_components

    def construct_placetypes(self, client):
        """
        :return: PlaceType objects (UrbanFootprint v0.1 Built Form default set)
        """

        placetypes = []
        for placetype in self.load_placetype_csv(client):
            building_attribute_set = dict(name=placetype.name)
            placetype = dict(
                type='urban_placetype',
                building_attribute_set=building_attribute_set,
                color=placetype.color if placetype.color else '#B0B0B0',
                intersection_density=placetype.intersection_density
            )
            placetypes.append(placetype)
        return map_to_dict(
            lambda placetype: [placetype['building_attribute_set']['name'], placetype], placetypes)


    def construct_built_forms(self, client):
        """
        Calls all the functions necessary to generate the Built Forms to mimic the
        starter set of v0.1 UrbanFootprint Built Forms
         """
        if not os.path.exists(self.built_form_path(client)):
            return {}

        primary_component_lookup = self.construct_primary_components(client)
        placetype_component_lookup = self.construct_placetype_components(client)
        placetype_lookup = self.construct_placetypes(client)

        results = {
            'placetypes': placetype_lookup.values(),
            'placetype_components': placetype_component_lookup.values(),
            'primary_components': primary_component_lookup.values(),
            'primary_component_percents': self.construct_primary_component_percents(
                placetype_component_lookup,
                primary_component_lookup,
                client=client),
            'building_use_percents': self.construct_building_use_percents(primary_component_lookup, client=client),
            'placetype_component_percents': self.construct_placetype_component_percents(placetype_lookup,
                placetype_component_lookup, client=client),
        }
        return results

    def construct_sample_built_forms(self, client):
        """
        Builds a sample set of built forms for testing
        """
        placetypes = self.construct_sample_placetypes()
        buildingtypes = self.construct_sample_placetype_components(placetypes)

        building_percents = self.construct_sample_primary_component_percents(buildingtypes)

        buildings = [building['building'] for building in building_percents]
        building_dict = map_to_dict(lambda building: [building['building_attribute_set']['name'], building], buildings)
        buildingtype_dict = map_to_dict(
            lambda buildingtype: [buildingtype['building_attribute_set']['name'], buildingtype], buildingtypes)

        return {'placetypes': placetypes,
                'placetype_components': buildingtypes,
                'primary_components': buildings,
                'primary_component_percents': building_percents,
                'building_use_percents': self.construct_building_use_percents(building_dict, client=client),
                'placetype_component_percents': self.construct_placetype_component_percents(
                    map_to_dict(lambda placetype: [placetype['building_attribute_set']['name'], placetype], placetypes),
                    buildingtype_dict, client=client)}


    def construct_sample_placetypes(self):
        """
        :return: a sample set of four placetypes
        """
        pt_ids = [1, 2, 3, 8, 9, 10, 16, 20, 25, 29, 30]
        sample_placetypes = list(self.construct_placetypes(client='default')[i] for i in pt_ids)

        return sample_placetypes


    def construct_sample_placetype_components(self, sample_placetypes):
        sample_placetype_components = []
        all_placetype_components = self.construct_placetype_components(client='default')
        placetype_component_dict = map_to_dict(
            lambda placetype_component: [placetype_component['building_attribute_set']['name'], placetype_component],
            all_placetype_components
        )

        sample_buildingtype_percents = self.construct_placetype_component_percents(
            map_to_dict(lambda placetype: [placetype['building_attribute_set']['name'], placetype], sample_placetypes),
            placetype_component_dict)

        placetype_components = []
        for placetype, components in sample_buildingtype_percents.items():
            for placetype_components, attributes in components['placetype_components'].items():
                placetype_components.append(placetype_components)

        for placetype_components in set(placetype_components):
            sample_placetype_components.append({'building_attribute_set': {'name': placetype_components}})

        return sample_placetype_components

    def construct_sample_primary_component_percents(self, sample_placetype_components, client):
        all_primary_components = self.construct_primary_components()
        primary_component_dict = map_to_dict(lambda building: [building['building_attribute_set']['name'], building],
                                             all_primary_components)

        sample_placetype_component_dict = map_to_dict(
            lambda placetype_component: [placetype_component['building_attribute_set']['name'], placetype_component],
            sample_placetype_components
        )
        sample_primary_component_percents = []

        for import_primary_component in self.load_buildings_csv(client):
            component = import_primary_component.placetype_component
            if component not in sample_placetype_component_dict:
                print "BuildingType " + import_primary_component.placetype + " is not used in this set :: skipping"
                continue

            placetype_component = sample_placetype_component_dict[component]
            building_percent = dict(
                primary_component_name=import_primary_component.name,
                primary_component=primary_component_dict[import_primary_component.name],
                placetype_component_name=import_primary_component.building_type,
                placetype_component=placetype_component,
                percent=import_primary_component.percent_of_building_type
            )
            sample_primary_component_percents.append(building_percent)

        return sample_primary_component_percents

    @staticmethod
    def delete_built_forms(self):
        """
        Deletes all BuiltForm objects from the database.
        """

        Placetype.objects.all().delete()
        PlacetypeComponentPercent.objects.all().delete()
        BuildingUsePercent.objects.all().delete()
        PrimaryComponentPercent.objects.all().delete()
        PrimaryComponent.objects.all().delete()
        PlacetypeComponent.objects.all().delete()
        PlacetypeComponentPercent.objects.all().delete()
