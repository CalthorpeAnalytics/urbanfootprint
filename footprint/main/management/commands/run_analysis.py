
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

import logging
import uuid
from optparse import make_option
from random import randrange

import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import utc

from footprint.main.models.analysis_module.agriculture_module.agriculture_updater_tool import AgricultureUpdaterTool
from footprint.main.models.analysis_module.analysis_module import AnalysisModuleKey, AnalysisModule
from footprint.main.models.analysis_module.energy_module.energy_updater_tool import EnergyUpdaterTool
from footprint.main.models.analysis_module.public_health_module.public_health_updater_tool import \
    PublicHealthUpdaterTool
from footprint.main.models.analysis_module.vmt_module.vmt_updater_tool import VmtUpdaterTool
from footprint.main.models.analysis_module.water_module.water_updater_tool import WaterUpdaterTool
from footprint.main.models.built_form.agriculture.crop_type import CropType
from footprint.main.models.config.scenario import FutureScenario, Scenario, BaseScenario
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.utils.async_job import Job

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
        This command initializes/syncs the footprint server with default and sample data. I'd like this to happen automatically in response to the post_syncdb event, but that event doesn't seem to fire (see management/__init__.py for the attempted wiring)
    """
    option_list = BaseCommand.option_list + (
        make_option('-r', '--resave', action='store_true', default=False,
                    help='Resave all the config_entities to trigger signals'),
        make_option('-s', '--skip', action='store_true', default=False,
                    help='Skip initialization and data creation (for just doing resave)'),
        make_option('--core', action='store_true', default=False, help='Run core'),
        make_option('--fiscal', action='store_true', default=False, help='Run fiscal'),
        make_option('--vmt', action='store_true', default=False, help='Run VMT'),
        make_option('--energy', action='store_true', default=False, help='Run Energy'),
        make_option('--water', action='store_true', default=False, help='Run Water'),
        make_option('--rucs', action='store_true', default=False, help='Run AG'),

        make_option('--public_health', action='store_true', default=False, help='Run Public Health'),
        make_option('--aggregate_geom', default="", help='Specify custom geometry for result aggregation'),

        make_option('--constraint', action='store_true', default=False, help='Run Environmental Constraints'),
        make_option('--test', action='store_true', default=False, help='setup test data before running'),
        make_option('--all', action='store_true', default=False, help='runs all analysis modules'),
        make_option('--postprocess_only', action='store_true', default=False, help='do not recreate vmt tables'),
        make_option('--scenario', default=False, help='String matching a key of or more Scenario to run'),
        make_option('--base', action='store_true', default=False, help='Run only base scenario'),
        make_option('--future', action='store_true', default=False, help='Run only future scenarios'),

    )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.filter()[0]
        # if not options['skip']:
        #     application_initialization()
        #     update_or_create_config_entities()
        if options['scenario']:
            scenarios = Scenario.objects.filter(key=options['scenario'])
        # elif options['base']:
        #     scenarios = BaseScenario.objects.all()
        # elif options['future']:
        else:
            scenarios = Scenario.objects.all()
        print "Running analysis modules on: {scenarios}".format(scenarios="\n".join([scenario.name for scenario in scenarios]))

        kwargs = dict(user=user)

        for scenario in scenarios:

            if options['core'] or options['all']:

                from footprint.main.models.built_form.placetype import Placetype
                end_state_feature_class = scenario.db_entity_feature_class(
                    DbEntityKey.END_STATE)
                future_scenario_features = end_state_feature_class.objects.all()
                built_forms = Placetype.objects.all()
                for scenario_built_form_feature in future_scenario_features.filter()[:100]:
                    scenario_built_form_feature.built_form = built_forms[randrange(0, len(built_forms) - 1)]
                    scenario_built_form_feature.dirty = True
                    scenario_built_form_feature.save()

                end_state_feature_class.post_save(user.id, end_state_feature_class.objects.all())

            if (options['fiscal'] or options['all']) and isinstance(scenario, FutureScenario):
                job = Job(user=user, hashid=uuid.uuid4(), type="Fiscal")
                job.save()
                kwargs = dict(
                    user=user,
                    job=job,
                    analysis_module=AnalysisModule.objects.get(
                        config_entity=scenario,
                        key=AnalysisModuleKey.FISCAL)
                )
                AnalysisModule.objects.get(config_entity=scenario, key=AnalysisModuleKey.FISCAL).update(**kwargs)

        if options['constraint'] or options['all']:
            # initialize(one_scenario)
            pass

        for scenario in scenarios:
            if options['energy'] or options['all']:
                job = Job(user=user, hashid=uuid.uuid4(), type="Energy")
                job.save()
                analysis_module = EnergyUpdaterTool.objects.get(config_entity=scenario)
                kwargs.update(dict(
                    job=job,
                    analysis_module=analysis_module
                ))
                analysis_module.update(**kwargs)

            if options['water'] or options['all']:
                job = Job(user=user, hashid=uuid.uuid4(), type="Water")
                job.save()
                analysis_module = WaterUpdaterTool.objects.get(config_entity=scenario)
                kwargs.update(dict(
                    job=job,
                    analysis_module=analysis_module
                ))
                analysis_module.update(**kwargs)

            if options['public_health'] or options['all']:
                job = Job(user=user, hashid=uuid.uuid4(), type="Public Health")
                job.save()
                analysis_module = PublicHealthUpdaterTool.objects.get(config_entity=scenario)
                if options['aggregate_geom']:
                    print options['aggregate_geom']
                    aggregate_geom = options['aggregate_geom'].split('.')
                    if len(aggregate_geom) == 1:
                        aggregate_geom.insert(0, 'public')
                else:
                    aggregate_geom = None

                kwargs.update(dict(
                    job=job,
                    analysis_module=analysis_module,
                    postprocess_only=options['postprocess_only'],
                    aggregate_geom=aggregate_geom
                ))

                analysis_module.update(**kwargs)

            if options['vmt'] or options['all']:
                job = Job(user=user, hashid=uuid.uuid4(), type="VMT")
                job.save()
                analysis_module = VmtUpdaterTool.objects.get(config_entity=scenario)
                kwargs.update(dict(
                    job=job,
                    analysis_module=analysis_module,
                    postprocess_only=options['postprocess_only']
                ))

                analysis_module.update(**kwargs)

            if options['rucs'] or options['all']:
                job = Job(user=user, hashid=uuid.uuid4(), type="Agriculture")
                job.save()
                kwargs = dict(
                    user=user,
                    job=job,
                    analysis_module=AnalysisModule.objects.get(
                        config_entity=scenario,
                        key=AnalysisModuleKey.AGRICULTURE)
                )
                if isinstance(scenario.subclassed, BaseScenario):
                    ag_scenario_feature_class = scenario.db_entity_feature_class(
                        DbEntityKey.BASE_AGRICULTURE)
                else:
                    ag_scenario_feature_class = scenario.db_entity_feature_class(
                        DbEntityKey.FUTURE_AGRICULTURE)

                if options['test']:
                    if ag_scenario_feature_class.objects.count() > 1000:
                        ag_features = ag_scenario_feature_class.objects.all()[:1000]
                    else:
                        ag_features = ag_scenario_feature_class.objects.all()
                    for f in ag_features:
                        f.dirty_flag = True
                        f.built_form = CropType.objects.all()[randrange(0, CropType.objects.count())]
                        f.save()

                else:
                    ag_scenario_feature_class.objects.all().update(updated=datetime.datetime.utcnow().replace(tzinfo=utc))

                AgricultureUpdaterTool.objects.get(config_entity=scenario).test_agriculture_core(**kwargs)
