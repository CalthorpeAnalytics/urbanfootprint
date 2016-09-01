
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

from django.conf import settings
from django.core.management import BaseCommand

from footprint.client.configuration.fixture import ConfigEntityFixture
from footprint.main.database.import_data import ImportData
from footprint.main.models.config.project import Project
from footprint.main.utils.utils import postgres_url_to_connection_dict
from footprint.utils.utils import drop_db

__author__ = 'calthorpe_analytics'


class Command(BaseCommand):
    """
        This command connects to the source of the sample data and populates a local db
    """

    def handle(self, *args, **options):
        drop_db('sample_data')
        project = Project.objects.all()[0]
        client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(project)
        default_db_entities = client_fixture.default_db_entities
        for db_entity_config in default_db_entities:
            importer = ImportData(config_entity=project, db_entity=db_entity_config)
            importer.target_database = settings.DATABASES['sample_data']
            importer.create_target_db_string()

            # For now we only import data for DbEntity instances with a configured database url
            connection_dict = postgres_url_to_connection_dict(db_entity_config['url'])
            # The import database currently stores tables as public.[config_entity.key]_[feature_class._meta.db_table (with schema removed)][_sample (for samples)]
            # We always use the table name without the word sample for the target table name
            source_table = "{0}_{1}_{2}".format(project.key, db_entity_config['table'], 'sample')
            importer._dump_tables_to_target('-t %s' % source_table,
                                            source_schema='public',
                                            target_schema='public',
                                            source_table=source_table,
                                            target_table=source_table,
                                            connection_dict=connection_dict)
