
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

import datetime
from django.utils.timezone import utc

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.config.scenario import BaseScenario, FutureScenario
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.utils.utils import timestamp
from footprint.utils.websockets import send_message_to_client
from tilestache_uf.utils import invalidate_feature_cache

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


class AgricultureUpdaterTool(AnalysisTool):

    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
        abstract = False

    def test_agriculture_core(self, **kwargs):
        self.agriculture_analysis(**kwargs)

    ANALYSIS_FIELDS = ["gross_net_pct",
                        "built_form_key",
                        "built_form_id",
                        "density_pct",
                        "acres_gross",
                        "crop_yield",
                        "market_value",
                        "production_cost",
                        "water_consumption",
                        "labor_force",
                        "truck_trips"]

    def progress(self, proportion, **kwargs):
        send_message_to_client(
            kwargs['user'].id,
            dict(
                event='postSavePublisherProportionCompleted',
                job_id=str(kwargs['job'].hashid),
                config_entity_id=self.config_entity.id,
                ids=[kwargs['analysis_module'].id],
                class_name='AnalysisModule',
                key=kwargs['analysis_module'].key,
                proportion=proportion))

    def update_dependent_scenarios(self, base_features, scenario):
        if isinstance(scenario, BaseScenario):

            future_scenarios = FutureScenario.objects.filter(parent_config_entity=scenario.parent_config_entity_subclassed)
            logger.info("Updating dependent scenarios {0} of {1}".format(future_scenarios, scenario))
            for future_scenario in future_scenarios:

                agriculture_feature_class = future_scenario.db_entity_feature_class(DbEntityKey.FUTURE_AGRICULTURE)
                future_features = agriculture_feature_class.objects.filter(
                    id__in=base_features,
                    updater__isnull=True
                )
                logger.info("Updating {0} features of {1}".format(future_features.count(), future_scenario))

                updated_built_forms = []
                for feature in future_features.iterator():

                    base_feature = base_features.get(id=feature.id)
                    if base_feature.built_form_id != feature.built_form_id:
                        updated_built_forms.append(feature)
                    base_attributes = dict(
                        gross_net_pct=base_feature.gross_net_pct,
                        built_form_key=base_feature.built_form_key,
                        built_form_id=base_feature.built_form_id,
                        density_pct=base_feature.density_pct,
                        acres_gross=base_feature.acres_gross,
                        crop_yield=base_feature.crop_yield,
                        market_value=base_feature.market_value,
                        production_cost=base_feature.production_cost,
                        water_consumption=base_feature.water_consumption,
                        labor_force=base_feature.labor_force,
                        truck_trips=base_feature.truck_trips,
                    )

                    for attr, value in base_attributes.iteritems():
                        setattr(feature, attr, value)
                    feature.save(update_fields=self.ANALYSIS_FIELDS)

                layer = Layer.objects.filter(presentation__config_entity=agriculture_feature_class.config_entity,
                                             db_entity_interest__db_entity__key=agriculture_feature_class.db_entity_key)[0]

                if updated_built_forms:
                    for key in layer.keys:
                        # clear tilestache cache for updated dependencies
                        invalidate_feature_cache(key, updated_built_forms)

    def update(self, **kwargs):
        scenario = self.config_entity.subclassed
        logger.debug('{0}:Starting Agriculture Core Analysis for {1}'.format(timestamp(), self.config_entity))
        if isinstance(scenario, BaseScenario):
            agriculture_db_entity_key = DbEntityKey.BASE_AGRICULTURE_CANVAS
        elif isinstance(scenario, FutureScenario):
            agriculture_db_entity_key = DbEntityKey.FUTURE_AGRICULTURE_CANVAS
        else:
            raise Exception("Config Entity is not a Future or Base Scenario, cannot run AgricultureCore.")

        ids = kwargs.get('ids', None)
        agriculture_feature_class = self.config_entity.db_entity_feature_class(agriculture_db_entity_key)

        if ids:
            features = agriculture_feature_class.objects.filter(id__in=ids)
        else:
            features = agriculture_feature_class.objects.filter(built_form__isnull=False)

        feature_count = features.count()

        if not feature_count:
            logger.info("No features to process!")
            return

        logger.debug("Processing {0} features...".format(feature_count))
        iterator_start = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.progress(0.05, **kwargs)

        if feature_count <= 36:
            increment_portion = (.9 / feature_count) + .001
            equal_portion = 1
        else:
            increment_portion = .05
            equal_portion = int((feature_count - 1) / 18)
        i = 1
        for feature in features.iterator():
            if i % equal_portion == 0:
                self.progress(increment_portion, **kwargs)

            if not feature.built_form:
                feature.built_form_key = None
                feature.crop_yield = 0
                feature.market_value = 0
                feature.production_cost = 0
                feature.water_consumption = 0
                feature.labor_force = 0
                feature.truck_trips = 0
            else:
                applied_acres = feature.acres_gross * feature.density_pct * feature.dev_pct
                agriculture_attribute_set = feature.built_form.resolve_built_form(feature.built_form).agriculture_attribute_set
                feature.built_form_key = feature.built_form.key
                feature.crop_yield = agriculture_attribute_set.crop_yield * applied_acres
                feature.market_value = agriculture_attribute_set.unit_price * feature.crop_yield
                feature.production_cost = agriculture_attribute_set.cost * applied_acres
                feature.water_consumption = agriculture_attribute_set.water_consumption * applied_acres
                feature.labor_force = agriculture_attribute_set.labor_input * applied_acres
                feature.truck_trips = agriculture_attribute_set.truck_trips * applied_acres
            feature.save(update_fields=self.ANALYSIS_FIELDS)
            i += 1
        total_time = datetime.datetime.utcnow().replace(tzinfo=utc) - iterator_start

        logger.debug("Processed {0} features in {1}: {2} per feature".format(
            feature_count, total_time, total_time/feature_count
        ))
        self.progress(.9, **kwargs)
        logger.debug('{0}:Finished Agriculture Core Analysis for {1} '.format(timestamp(), self.config_entity))

        self.update_dependent_scenarios(features, scenario)

    #
    # def update_progress(self, number, total, start, **kwargs):
    #     if total < 20:
    #         parts = float(total)
    #     else:
    #         parts = 20
    #     chunk = float(total) / parts
    #     increment = 1 / parts
    #     if number % chunk < 1:
    #         progress_value = float(number) / float(total)
    #         octotherps = int(round(progress_value * parts))
    #         spaces = parts - octotherps
    #         bar = '#'*octotherps + ' '*spaces
    #         print '\r[{0}] {1}%'.format(bar, round(progress_value*100, 2)) + " | " + \
    #               self.estimated_time_remaining(progress_value, start) + " remaining"
    #     else:
    #         return
    #
    #
    # def estimated_time_remaining(self, progress, start):
    #     current_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     elapsed = current_time - start
    #     total_time = (elapsed * int(round((10/progress)))) / 10
    #     remaining_estimate = total_time - elapsed
    #     return str(remaining_estimate)
