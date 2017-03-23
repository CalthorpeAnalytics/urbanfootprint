
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
from django.core.management import call_command
from django.conf import settings
from footprint.client.configuration.fixture import InitFixture
from footprint.client.configuration.scag_dm.built_form.scag_dm_land_use_definition import ScagDmLandUseDefinition
import logging
logger = logging.getLogger(__name__)

class ScagDmInitFixture(InitFixture):
    client = 'scag_dm'

    def import_database(self):
        dct = settings.DATABASES['source']
        return dict(
            host     = dct['HOST'],
            database = dct['NAME'],
            user     = dct['USER'],
            password = dct['PASSWORD'],
        )

    def model_class_modules(self):
        """
            SCAG defines additional concrete model classes in the following modules
        :return:
        """
        return [
            ("built_form", "land_use_definition"),
            ("built_form", "land_use")
        ]

    def populate_models(self):
        if ScagDmLandUseDefinition.objects.count() == 0:
            logger.info("Loading SCAG land use definitions")
            fixture_path = os.path.join(settings.ROOT_PATH, 'footprint', 'client', 'configuration',
                                        'scag_dm', 'built_form', 'scag_land_use_definitions.json')
            call_command('loaddata', fixture_path)
        else:
            logger.info("Skipping because of " + str(ScagDmLandUseDefinition.objects.count()) + " objects already there")

    def groups(self):
        return self.parent_fixture.groups()

    def users(self):
        return self.parent_fixture.users()
