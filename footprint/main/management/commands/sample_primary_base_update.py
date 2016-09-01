
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

from django.core.management.base import BaseCommand

from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.application_initialization import application_initialization, update_or_create_config_entities
from footprint.main.models.keys.keys import Keys
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.main.publishing.user_initialization import update_or_create_users
from footprint.main.publishing.config_entity_initialization import update_or_create_scenarios


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--skip', action='store_true',  default=False, help='Skip initialization and data creation (for just doing resave)'),
    )

    def handle(self, *args, **options):
        if not options['skip']:
            application_initialization()
            update_or_create_config_entities()

        user = update_or_create_users()['user']
        scenarios = update_or_create_scenarios()
        for scenario in scenarios:
            layer_library = scenario.presentation_set.filter(key=Keys.LAYER_LIBRARY_DEFAULT)[0]
            presentation_medium = layer_library.presentationmedium_set.get(db_entity_key=Keys.DB_ABSTRACT_PRIMARY_PARCEL_SOURCE)
            layer = Layer.objects.get(id=presentation_medium.id) # Cast
            layer_selection_class = get_or_create_layer_selection_class_for_layer(layer, scenario)
            layer_selection = layer_selection_class.objects.get(user=user, layer=layer)
            layer_selection.save()
