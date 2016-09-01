
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
import logging

from django.core.management.base import BaseCommand

from footprint.main.models.config.scenario import FutureScenario
from footprint.main.models.keys.keys import Keys


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
        This command clears all layer_selections
    """
    option_list = BaseCommand.option_list + (
        make_option('-r', '--resave', action='store_true', default=False,
                    help='Resave all the config_entities to trigger signals'),
        make_option('--scenario', default='', help='String matching a key of or more Scenario to run'),
    )

    def handle(self, *args, **options):
        scenarios = FutureScenario.objects.filter(key__contains=options['scenario']) if options[
            'scenario'] else FutureScenario.objects.all()
        for scenario in scenarios:
            future_scenario_feature_class = scenario.db_entity_feature_class(DbEntityKey.FUTURE_SCENARIO)
            for future_scenario_feature in future_scenario_feature_class.objects.exclude(built_form__isnull=True):
                future_scenario_feature.built_form = None
                future_scenario_feature.save()
