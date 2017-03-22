
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


import os
import logging
from footprint.main.models.keys.user_group_key import UserGroupKey

logger = logging.getLogger(__name__)
from django.core.management import call_command
from django.conf import settings

from footprint.client.configuration.fixture import InitFixture
from footprint.client.configuration.sacog.built_form.sacog_land_use_definition import SacogLandUseDefinition


class SacogInitFixture(InitFixture):
    client = 'sacog'

    def model_class_modules(self):
        """
        SACOG defines additional concrete model classes in the following modules
        :return:
        """
        return [
            ("built_form", "land_use_definition"),
            ("built_form", "land_use")
        ]

    def import_database(self):
        dct = settings.DATABASES['source']
        return dict(
            host     = dct['HOST'],
            database = dct['NAME'],
            user     = dct['USER'],
            password = dct['PASSWORD'],
        )

    def populate_models(self):
        if SacogLandUseDefinition.objects.count() == 0:
            logger.info("Loading SACOG land use definitions")
            fixture_path = os.path.join(settings.ROOT_PATH, 'footprint', 'client', 'configuration',
                            'sacog', 'built_form', 'sacog_land_use_definitions.json')
            call_command('loaddata', fixture_path)
        else:
            print logger.info("Skipping because of " + str(SacogLandUseDefinition.objects.count()) + " objects already there")

    def users(self):
        return self.parent_fixture.users() + [
            dict(group=UserGroupKey.ADMIN, username='test', password='testd@uf', email='test@example.com')
        ]
