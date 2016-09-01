
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
from footprint.main.publishing.data_export_publishing import export_scenario


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
        This command clears all layer_selections
    """
    option_list = BaseCommand.option_list + (
        make_option('--scenario', default='', help='String matching a key of or more Scenario to run'),
    )

    def handle(self, *args, **options):
        scenarios = FutureScenario.objects.filter(key__contains=options['scenario']) if options[
            'scenario'] else FutureScenario.objects.all()
        for scenario in scenarios:
            logger.info("Exporting scenario {0}".format(scenario.key))
            export_scenario(None, scenario.id)
