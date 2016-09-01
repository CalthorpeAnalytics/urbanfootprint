
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
import time

from footprint.main.managers.geo_inheritance_manager import GeoInheritanceManager
from footprint.main.models.analysis_module.analysis_tool import AnalysisTool
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.utils.websockets import send_message_to_client

__author__ = 'calthorpe_analytics'


logger = logging.getLogger(__name__)

class FiscalUpdaterTool(AnalysisTool):

    objects = GeoInheritanceManager()

    class Meta(object):
        app_label = 'main'
        abstract = False

    def fiscal_progress(self, proportion, **kwargs):

        send_message_to_client(kwargs['user'].id, dict(
            event='postSavePublisherProportionCompleted',
            job_id=str(kwargs['job'].hashid),
            config_entity_id=self.config_entity.id,
            ids=[kwargs['analysis_module'].id],
            class_name='AnalysisModule',
            key=kwargs['analysis_module'].key,
            proportion=proportion)
        )
        logger.info("Progress {0}".format(proportion))


    def update(self, **kwargs):
        logger.info("Executing Fiscal using {0}".format(self.config_entity))

        self.run_fiscal_calculations(**kwargs)

        logger.info("Done executing Fiscal")
        logger.info("Executed Fiscal using {0}".format(self.config_entity))


    def run_fiscal_calculations(self, **kwargs):
        start_time = time.time()

        policy_assumptions = {}
        # TODO Use the first PolicySet--this needs to be done better
        policy_set = self.config_entity.computed_policy_sets()[0].policy_by_key('fiscal')

        #TODO: put a method in PolicySet that flattens the policies to a dict like this does
        for policy_set in policy_set.policies.all():
            policy_assumptions[policy_set.key] = {}
            for policy in policy_set.policies.all():
                for key, subpolicy in policy.values.items():
                     policy_assumptions[policy_set.key]["_".join([policy.key, key])] = subpolicy

        scenario_time_increment = float(self.config_entity.scenario.year - self.config_entity.scenario.project.base_year)
        fiscal_feature_class = self.config_entity.db_entity_feature_class(DbEntityKey.FISCAL, base_feature_class=True)
        net_increment_class = self.config_entity.db_entity_feature_class(DbEntityKey.INCREMENT)

        features = net_increment_class.objects.filter(land_development_category__isnull=False)

        fiscal_outputs = []

        self.fiscal_progress(0.3, **kwargs)

        for feature in features:

            new_feature = fiscal_feature_class(
                id=feature.id,
                wkb_geometry=feature.wkb_geometry
            )
            new_feature.residential_capital_costs = self.calculate_feature_fiscal_attributes(feature, policy_assumptions['capital_costs'])
            new_feature.residential_operations_maintenance_costs = self.calculate_feature_fiscal_attributes(
                    feature, policy_assumptions['operations_maintenance_costs'], multiplier=scenario_time_increment)
            new_feature.residential_revenue = self.calculate_feature_fiscal_attributes(feature, policy_assumptions['revenue'])
            fiscal_outputs.append(new_feature)

        self.fiscal_progress(0.5, **kwargs)

        fiscal_feature_class.objects.all().delete()
        fiscal_feature_class.objects.bulk_create(fiscal_outputs)

        self.fiscal_progress(0.2, **kwargs)

        print 'Finished: ' + str(time.time() - start_time)

        from footprint.main.publishing.config_entity_publishing import post_save_config_entity_analysis_module
        post_save_config_entity_analysis_module.send(
            sender=self.config_entity.__class__,
            config_entity=self.config_entity,
            analysis_module=kwargs['analysis_module']
        )


    def calculate_feature_fiscal_attributes(self, feature, policy_dict, multiplier=1.0):

        key = feature.land_development_category

        if key == 'compact':
            key = 'compact_refill' if feature.refill_flag else 'compact_greenfield'

        return  multiplier * sum([
                    float(feature.du_detsf_ll) * policy_dict[key + '_single_family_large_lot'],
                    float(feature.du_detsf_sl) * policy_dict[key + '_single_family_small_lot'],
                    float(feature.du_attsf) * policy_dict[key + '_single_family_attached'],
                    float(feature.du_mf) * policy_dict[key + '_multifamily']
        ])
