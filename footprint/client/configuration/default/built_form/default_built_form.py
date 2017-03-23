
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

from footprint.client.configuration.sacog.built_form.sacog_built_form import RUCS_CROPTYPE_COLORS
from footprint.main.models.built_form.placetype import Placetype
from footprint.main.models.built_form.placetype_component_percent import PlacetypeComponentPercent
from footprint.main.models.built_form.primary_component import PrimaryComponent
from footprint.main.models.built_form.primary_component_percent import PrimaryComponentPercent
from footprint.main.models.built_form.urban.building_use_percent import BuildingUsePercent
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.keys.user_group_key import UserGroupKey

__author__ = 'calthorpe_analytics'
import itertools
import csv
import random
from django.contrib.auth import get_user_model
from footprint.main.models.built_form.urban.building_attribute_set import BuildingAttributeSet
from django.template.defaultfilters import slugify
from footprint.main.initialization.built_form.built_form_importer import BuiltFormImporter
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.lib.functions import map_to_dict
from footprint.client.configuration.fixture import BuiltFormFixture
from footprint.main.models.built_form.agriculture.agriculture_attribute_set import AgricultureAttributeSet
from footprint.main.models.built_form.agriculture.crop import Crop
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.models.built_form.placetype_component import PlacetypeComponentCategory, PlacetypeComponent
from footprint.main.models.built_form.urban.building import Building
from footprint.main.models.built_form.urban.building_type import BuildingType
from footprint.main.models.built_form.urban.urban_placetype import UrbanPlacetype
from footprint.main.models.keys.keys import Keys
from footprint.main.models.tag import Tag
from django.conf import settings
from footprint.main.utils.fixture_list import FixtureList

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


# By default we create a BuiltFormSet for each class, one for Placetypes, BuildingTypes, and Buildings.
# Sets can contain instances of multiple classes, but this is the configuration is easiest to understand
class DefaultBuiltFormFixture(DefaultMixin, BuiltFormFixture):

    def update_or_create_building_attribute_set(self, built_form, building_attribute_set_dict, built_form_created):
        if built_form.key.startswith('c') or built_form.key.startswith('ct'):
            return
        if built_form_created or not built_form.building_attribute_set:
            building_attribute_set = BuildingAttributeSet.objects.create(**building_attribute_set_dict)
            built_form.building_attribute_set = building_attribute_set
            built_form.save()
        else:
            building_attribute_set = built_form.building_attribute_set
            for (key, value) in building_attribute_set_dict.items():
                setattr(building_attribute_set, key, value)
            building_attribute_set.save()

    def update_or_create_agriculture_attribute_set(self, built_form, agriculture_attribute_set_dict, built_form_created):
        if built_form.key.startswith('b') or built_form.key.startswith('bt'):
            return
        if built_form_created:
            built_form.agriculture_attribute_set = AgricultureAttributeSet.objects.create(**agriculture_attribute_set_dict)
            built_form.save()
        else:
            agriculture_attribute_set = built_form.agriculture_attribute_set
            for (key, value) in agriculture_attribute_set_dict.items():
                setattr(agriculture_attribute_set, key, value)
            agriculture_attribute_set.save()

    @staticmethod
    def construct_placetype_examples():
        examples_file = 'placetype_example_areas.csv'
        # # Read in placetype examples and create a dictionary so you
        bf_examples_path = '%s/sproutcore/apps/fp/resources/Text/%s' % (settings.ROOT_PATH, examples_file)
        reader = csv.DictReader(open(bf_examples_path, "rU"))
        #This dictionary has builtform id's as the key, and the value is an array of dictionaries, each containing
        #data about an example area
        bf_examples = {}
        for row in reader:
            if row:
                pt__key = row["pt__key"]
                if bf_examples.get(pt__key):
                    bf_examples[pt__key].append(row)
                else:
                    bf_examples[pt__key] = [row]
        return bf_examples

    def built_forms(self, client='default'):
        """
            Returns an unpersisted dict with lists placetypes, buildingtypes, buildings, etc. fixtures
        :param default_built_forms:
        :return:
        """
        #todo : switch out this user
        user = get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)
        # Create the definitions for all default built_forms in the system. These depend on one another and are
        # made into actual instances in persist_built_forms
        if not isinstance(self.config_entity, GlobalConfig) or settings.SKIP_ALL_BUILT_FORMS:
            return {
                'placetypes': [],
                'placeptype_components': [],
                'primary_components': [],
                'primary_component_percents': [],
                'placetype_component_percents': [],
                'building_use_percents': [],
            }

        built_forms_dict = BuiltFormImporter().construct_built_forms(client)
        built_forms = []

        logger.info("Beginning Primary Components")

        for primary_component_dict in built_forms_dict['primary_components']:

            if 'building_attribute_set' in primary_component_dict:
                name = primary_component_dict['building_attribute_set'].pop('name', None)
                primary_component, created, updated = Building.objects.update_or_create(
                    key='b__' + slugify(name).replace('-', '_'),
                    defaults=dict(name=name, creator=user, updater=user)
                )
                self.update_or_create_building_attribute_set(primary_component, primary_component_dict['building_attribute_set'], created)
                del primary_component, name, created, updated

            if 'agriculture_attribute_set' in primary_component_dict:
                name = primary_component_dict['agriculture_attribute_set'].pop('name', None)

                primary_component, created, updated = Crop.objects.update_or_create(
                    key='c__' + slugify(name).replace('-', '_'),
                    defaults=dict(name=name, creator=user, updater=user),
                )
                self.update_or_create_agriculture_attribute_set(primary_component, primary_component_dict['agriculture_attribute_set'], created)

                del primary_component, name, created, updated

        logger.info("Beginning Building Use Percents")
        for building_use_percent_dict in built_forms_dict['building_use_percents']:
            built_form = Building.objects.get(name=building_use_percent_dict['built_form_name'])
            use_attributes = building_use_percent_dict['built_form_uses']
            definition = use_attributes.pop('building_use_definition')
            use_percent, created, updated = BuildingUsePercent.objects.update_or_create(
                building_attribute_set=built_form.building_attribute_set,
                building_use_definition=definition,
                defaults=use_attributes
            )
            del use_attributes, use_percent, definition, built_form

        if not settings.TEST_SKIP_BUILT_FORM_COMPUTATIONS:
            logger.info("Calculating Primary Components")
            for primary_component in Building.objects.all():
                primary_component.building_attribute_set.calculate_derived_fields()
                primary_component.update_or_create_flat_built_form()
                del primary_component

        for primary_component in Crop.objects.all():
            # we want to create croptypes from sacog's provided crops. this may need to change if this datasource
            # is widely implemented, but this should be fine for now
            pt_component_key = 'ct__' + slugify(primary_component.name).replace('-', '_')
            placetype_component, created, updated = CropType.objects.update_or_create(
                key=pt_component_key,
                defaults=dict(name=primary_component.name,
                              creator=user,
                              updater=user,
                              component_category=PlacetypeComponentCategory.objects.get(name=Keys.BUILDINGTYPE_AGRICULTURAL)),
            )

            color = RUCS_CROPTYPE_COLORS.get(placetype_component.name, None)
            logger.info("using {0} for {1}".format(color, placetype_component))
            if not color:
                logger.warn("Did not find color match for {0}.".format(placetype_component))
                color = random_greyscale_hexcode()

            logger.info("using {0} for {1}".format(color, placetype_component))
            placetype_component.create_built_form_template(color)
            if created or not placetype_component.agriculture_attribute_set:
                placetype_component.agriculture_attribute_set = AgricultureAttributeSet.objects.create()

            PrimaryComponentPercent.objects.update_or_create(
                placetype_component=placetype_component,
                primary_component=primary_component,
                percent=1,
            )

            placetype_component.aggregate_agriculture_attribute_set()
            placetype_component.save()
            del primary_component, placetype_component

        logger.info("Beginning Placetype Components")
        for placetype_component in built_forms_dict['placetype_components']:
            name = placetype_component['name']
            category = placetype_component['component_category']
            component_category = PlacetypeComponentCategory.objects.get_or_create(name=category)[0]

            if placetype_component['type'] == 'building_type':
                color = placetype_component.get('color', "#909090")
                placetype_component, created, updated = BuildingType.objects.update_or_create(
                    key=placetype_component['key'],
                    defaults=dict(
                        name=name,
                        creator=user,
                        updater=user,
                        component_category=component_category
                    ))
                self.update_or_create_building_attribute_set(placetype_component, {}, created)

            elif placetype_component['type'] == 'crop_type':
                logger.info("Loading CropType Mix: {0}".format(placetype_component.name))
                color = RUCS_CROPTYPE_COLORS.get(placetype_component.name, None)

                placetype_component, created, updated = CropType.objects.update_or_create(
                    key=placetype_component['key'],
                    defaults=dict(
                        name=name,
                        creator=user,
                        updater=user,
                        component_category=component_category,
                        agriculture_attribute_set=AgricultureAttributeSet.objects.create() if placetype_component['key'].startswith('c') else None,
                    )
                )

                self.update_or_create_agriculture_attribute_set(placetype_component, {}, created)

            placetype_component.create_built_form_template(color)

            placetype_component.save()
            built_forms.append(placetype_component)
            del placetype_component, name, color, category, created, updated

        logger.info("Beginning Primary Component Percents")
        for primary_component_percent in built_forms_dict['primary_component_percents']:

            if primary_component_percent['type'] == 'building_type':
                placetype_component = BuildingType.objects.get(name=primary_component_percent['placetype_component_name'])

            elif primary_component_percent['type'] == 'crop_type':
                placetype_component = CropType.objects.get(name=primary_component_percent['placetype_component_name'])

            if primary_component_percent['percent'] > 0:
                PrimaryComponentPercent.objects.update_or_create(
                    primary_component=PrimaryComponent.objects.get(
                        name=primary_component_percent['primary_component_name']
                    ),

                    placetype_component=placetype_component,
                    defaults=dict(percent=primary_component_percent['percent'])
                )
            if not settings.TEST_SKIP_BUILT_FORM_COMPUTATIONS:
                if primary_component_percent['type'] == 'building_type':
                    placetype_component.aggregate_building_attribute_set()
                    placetype_component.update_or_create_flat_built_form()
                elif primary_component_percent['type'] == 'crop_type':
                    placetype_component.aggregate_agriculture_attribute_set()

        placetypes = BuiltFormImporter().load_placetype_csv(client)

        placetype_color_lookup = map_to_dict(lambda placetype: [placetype.name, placetype.color], placetypes)

        bf_examples = self.construct_placetype_examples()

        logger.info("Beginning Placetypes")
        for placetype_dict in built_forms_dict['placetypes']:
            name = placetype_dict['building_attribute_set'].pop('name', None)

            placetype, created, updated = UrbanPlacetype.objects.update_or_create(
                key='pt__' + slugify(name).replace('-', '_'),
                defaults=dict(
                    updater=user,
                    creator=user,
                    name=name,
                    intersection_density=placetype_dict['intersection_density'])
            )
            building_attribute_set_dict = placetype_dict['building_attribute_set']
            self.update_or_create_building_attribute_set(placetype, building_attribute_set_dict, created)
            placetype.create_built_form_template(placetype_color_lookup.get(placetype.name, "#909090"))
            placetype.update_or_create_built_form_media()
            placetype.update_or_create_built_form_examples(bf_examples.get(placetype.key) if bf_examples.get(placetype.key) else [])

            # built_forms.append(placetype)

            placetype.save()

            placetype_dict = built_forms_dict['placetype_component_percents'].get(placetype.name, None)
            if not placetype_dict:
                logger.warning("Expected built_forms_dict['placetype_component_percents'] to have key %s",
                               placetype.name)
            else:
                for placetype_component, attributes in placetype_dict.items():
                    component = BuildingType.objects.get(name=placetype_component)
                    if attributes['percent'] > 0:
                        PlacetypeComponentPercent.objects.update_or_create(
                            placetype=placetype,
                            placetype_component=component,
                            defaults=dict(percent=attributes['percent']))

        if not settings.TEST_SKIP_BUILT_FORM_COMPUTATIONS:
            logger.info("Computing Placetypes")
            for placetype in UrbanPlacetype.objects.all():
                placetype.aggregate_building_attribute_set()
                placetype.update_or_create_flat_built_form()

        built_forms_dict = {
            'placetypes': Placetype.objects.all(),
            'placetype_components': PlacetypeComponent.objects.all(),
            'primary_components': PrimaryComponent.objects.all(),

            'urban_placetypes': UrbanPlacetype.objects.all(),
            'building_types': BuildingType.objects.all(),
            'buildings': Building.objects.all(),

            # 'landscape_types': LandscapeType.objects.all(),
            'crop_types': CropType.objects.all(),
            'crops': Crop.objects.all(),

            'primary_component_percents': PrimaryComponentPercent.objects.all(),
            'building_use_percents': BuildingUsePercent.objects.all(),
            'placetype_component_percents': PlacetypeComponentPercent.objects.all()
        }

        return built_forms_dict

    def tag_built_forms(self, built_forms_dict, client='default'):
        """
            Tag BuiltForms based on their character
        :return:
        """
        if settings.SKIP_ALL_BUILT_FORMS:
            return

        built_form_importer = BuiltFormImporter()

        for placetype_component in built_forms_dict.get('placetype_components', []):
            placetype_component.tags.add(
                Tag.objects.update_or_create(tag=placetype_component.component_category.name)[0])

        for built_form in itertools.chain(built_forms_dict.get('placetypes', []),
                                          built_forms_dict.get('primary_components', [])):
            tag, created, updated = Tag.objects.update_or_create(tag='Unsorted')
            if len(built_form.tags.filter(tag=tag.tag)) == 0:
                built_form.tags.add(tag)

    def built_form_sets(self):
        return FixtureList([
            dict(
                scope=GlobalConfig,
                key='uf_urban_placetypes',
                name='UF Placetypes',
                description='BuiltFormSet containing only placetypes',
                attribute='building_attribute_set',

                clazz=UrbanPlacetype,
                client='default'
            ),
            dict(
                scope=GlobalConfig,
                key='uf_building_types',
                name='UF BuildingTypes',
                description='BuiltFormSet containing only buildingtypes',
                attribute='building_attribute_set',

                clazz=BuildingType,
                client='default'
            )
            # We never present a Building BuiltFormSet
            # dict(
            #     scope=GlobalConfig,
            #     key='uf_buildings',
            #     name='Buildings',
            #     description='BuiltFormSet containing only buildings',
            #     attribute='building_attribute_set',
            #
            #     clazz=Building,
            #     client='default'
            # )
        ]).matching_scope(class_scope=self.config_entity and self.config_entity.__class__)


def random_greyscale_hexcode():
    rgb_values = random.randint(85, 200)
    hex_component = hex(rgb_values)[2:]
    hex_code = '#' + hex_component*3
    logger.info('random gray color: ' + hex_code)
    return hex_code
