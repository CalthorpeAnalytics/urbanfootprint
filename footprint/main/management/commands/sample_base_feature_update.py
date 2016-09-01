
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

from optparse import make_option
from random import randrange
from django.core.management.base import BaseCommand
from footprint.main.models.config.project import Project
from footprint.main.models.built_form.placetype import Placetype
from footprint.main.models.application_initialization import application_initialization, update_or_create_config_entities
from footprint.main.models.keys.keys import Keys

class Command(BaseCommand):
    """
        This command initializes/syncs the footprint server with default and sample data. I'd like this to happen automatically in response to the post_syncdb event, but that event doesn't seem to fire (see management/__init__.py for the attempted wiring)
    """
    option_list = BaseCommand.option_list + (
        make_option('-r', '--resave',  action='store_true', default=False, help='Resave all the config_entities to trigger signals'),
        make_option('-s', '--skip', action='store_true',  default=False, help='Skip initialization and data creation (for just doing resave)'),
        make_option('--scenario', default='', help='String matching a key of or more Scenario to run'),
    )

    def handle(self, *args, **options):
        if not options['skip']:
            application_initialization()
            update_or_create_config_entities()

        projects = Project.objects.filter()
        placetypes = Placetype.objects.all()
        for project in projects:
            base_feature_class = project.db_entity_feature_class(DbEntityKey.BASE)
            base_features = base_feature_class.objects.all()
            for base_feature in base_features:
                base_feature.built_form = placetypes[randrange(0, len(placetypes)-1)]
                base_feature.save()
