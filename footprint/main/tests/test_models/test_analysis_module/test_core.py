
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

from datetime import datetime
import random
from time import sleep

from nose import with_setup

from footprint.main.models.application_initialization import application_initialization, \
    update_or_create_config_entities
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.keys.keys import Keys
from footprint.main.publishing.config_entity_initialization import update_or_create_scenarios
from footprint.main.tests.test_models.test_config_entity.test_config_entity import TestConfigEntity

__author__ = 'calthorpe_analytics'


class TestCore(TestConfigEntity):
    def setup(self):
        super(TestCore, self).__init__()
        application_initialization()
        update_or_create_config_entities()

    def teardown(self):
        super(TestCore, self).__init__()

    @with_setup(setup, teardown)
    def test_scenario_core(self):
        """
            Tests scenario creation
        :return:
        """
        scenarios = update_or_create_scenarios()
        scenario = scenarios[0]
        scenario_built_form_feature_manager = scenario.db_entity_feature_class('scenario_built_form_layer').objects
        built_form_set = scenario.computed_built_forms()[0]
        built_form_ids = map(lambda built_form: built_form.id, built_form_set.built_form_definitions.all())

        length = scenario_built_form_feature_manager.count()
        assert (length > 0)
        # Dirty up the features
        for scenario_built_form_feature_manager in scenario_built_form_feature_manager.all():
            scenario_built_form_feature_manager.built_form_id = random.choice(built_form_ids)
        scenario_built_form_feature_manager.save()

        core = ScenarioBuilder.objects.get(config_entity=scenario)
        timestamp = datetime.now()
        core.start(ids=map(lambda obj: obj.id, scenario_built_form_feature_manager.all()))
        sleep(3)

        # Make sure we have values for all the analysis table classes
        for db_entity_key in [Keys.DB_ABSTRACT_GROSS_INCREMENT_FEATURE, DbEntityKey.INCREMENT,
                              DbEntityKey.END_STATE]:
            db_entity = scenario.db_entity_by_key(db_entity_key)
            FeatureClass = scenario.db_entity_feature_class(db_entity_key)
            # Assert that the correct number of rows exist
            assert (FeatureClass.objects.count() == length)
            # Assert that all rows were updated
            assert (len(FeatureClass.objects.filter(updated__gte=timestamp)) == length,
                    "For table {0}.{1}, not all rows were updated by the core, rather {2} out of {3}".format(
                        scenario.schema(),
                        db_entity.table,
                        len(FeatureClass.objects.filter(updated__gte=timestamp)),
                        length))
