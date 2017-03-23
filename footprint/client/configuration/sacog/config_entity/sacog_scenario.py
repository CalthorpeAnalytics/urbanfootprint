
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
from footprint.main.models import PhOutcomesSummary
from footprint.main.models.analysis.public_health_features.ph_variables_feature import PhVariablesFeature
from footprint.main.models.analysis.public_health_features.ph_grid_outcomes_feature import PhGridOutcomesFeature
from footprint.main.models.analysis.public_health_features.ph_block_group_outcomes_feature import \
    PhBlockGroupOutcomesFeature
from footprint.main.models.analysis.vmt_features.vmt_variables_feature import VmtVariablesFeature
from footprint.main.models.analysis.water_feature import WaterFeature
from footprint.main.models.analysis.energy_feature import EnergyFeature
from footprint.main.models.analysis.vmt_features.vmt_feature import VmtFeature
from footprint.main.models import AgricultureFeature
from footprint.main.models.base.canvas_feature import CanvasFeature
from footprint.main.models.analysis.core_increment_feature import CoreIncrementFeature
from footprint.main.models.category import Category
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.analysis.fiscal_feature import FiscalFeature
from footprint.main.models.geospatial.behavior import Behavior, BehaviorKey
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.client.configuration.fixture import ScenarioFixture, project_specific_project_fixtures
from footprint.main.lib.functions import merge

from footprint.main.models.config.scenario import FutureScenario, Scenario
from footprint.main.models.geospatial.intersection import GeographicIntersection, \
    AttributeIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.utils.model_utils import uf_model
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'


class SacogScenarioFixture(ScenarioFixture):

    def feature_class_lookup(self):
        # Get the client project fixture (or the default region if the former doesn't exist)
        project = merge(*map(
            lambda project_fixture: project_fixture.feature_class_lookup(),
            project_specific_project_fixtures(config_entity=self.config_entity)))
        return merge(
            project,
            FeatureClassCreator(self.config_entity).key_to_dynamic_model_class_lookup(self.default_db_entities())
        )

    def default_db_entities(self):
        """
            Scenarios define DbEntities specific to the Scenario. Creates a list a dictionary of configuration
            functionality. These are filtered based on whether the given scenario matches the scope in the
            configuration
        :return:
        """
        scenario = self.config_entity
        project = self.config_entity.parent_config_entity
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return super(SacogScenarioFixture, self).default_db_entities() + map(
            lambda db_entity_dict: update_or_create_db_entity(scenario, db_entity_dict['value']),
            FixtureList([
                dict(
                    class_scope=FutureScenario,
                    value=DbEntity(
                        key=DbEntityKey.INCREMENT,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=CoreIncrementFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            import_ids_only=True,
                            related_fields=dict(built_form=dict(
                                single=True,
                                related_class_name=uf_model('built_form.built_form.BuiltForm')
                            ))
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('scenario_increment'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.FUTURE_SCENARIO
                        )]
                    ),
                ),
                dict(
                    class_scope=FutureScenario,
                    value=DbEntity(
                        key=DbEntityKey.END_STATE,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=CanvasFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            related_fields=dict(built_form=dict(
                                single=True,
                                related_class_name=uf_model('built_form.built_form.BuiltForm')
                            ))
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('scenario_end_state'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.FUTURE_SCENARIO
                        )]
                    ),
                ),
                dict(
                    class_scope=FutureScenario,
                    value=DbEntity(
                        key=DbEntityKey.FUTURE_AGRICULTURE_CANVAS,
                        name='Scenario Agriculture End State',
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=AgricultureFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_AGRICULTURE_CANVAS,
                            import_ids_only=False,
                            related_fields=dict(built_form=dict(
                                single=True,
                                related_class_name=uf_model('built_form.built_form.BuiltForm'),
                                related_class_join_field_name='key',
                                source_class_join_field_name='built_form_key'
                            ))
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('agriculture_scenario'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.FUTURE_SCENARIO
                        )]
                    )
                ),
                dict(
                    class_scope=FutureScenario,
                    value=DbEntity(
                        key=DbEntityKey.FISCAL,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=FiscalFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            empty_table=True
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                ),

                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.VMT_VARIABLES,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=VmtVariablesFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            import_ids_only=True,
                            filter_query=dict(),
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.REFERENCE
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.VMT,
                        name='Vehicle Miles Traveled Output',
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=VmtFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            empty_table=True
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.ENERGY,
                        name='Energy Demand Output',
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=EnergyFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            empty_table=True
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.WATER,
                        name='Water Demand Output',
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=WaterFeature,
                            import_from_db_entity_key=DbEntityKey.BASE_CANVAS,
                            empty_table=True
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.PH_VARIABLES,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=PhVariablesFeature,
                            import_from_db_entity_key=DbEntityKey.GRID_150M,
                            import_ids_only=True,
                            filter_query=dict(),
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.REFERENCE
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.PH_GRID_OUTCOMES,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=PhGridOutcomesFeature,
                            import_from_db_entity_key=DbEntityKey.GRID_150M,
                            import_ids_only=True,
                            filter_query=dict(),
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.REFERENCE
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.PH_BLOCK_GROUP_OUTCOMES,
                        name='Public Health Output',
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=PhBlockGroupOutcomesFeature,
                            import_from_db_entity_key=DbEntityKey.GRID_150M,
                            import_ids_only=True,
                            filter_query=dict(),
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                ),
                dict(
                    class_scope=Scenario,
                    value=DbEntity(
                        key=DbEntityKey.PH_OUTCOMES_SUMMARY,
                        feature_class_configuration=FeatureClassConfiguration(
                            abstract_class=PhOutcomesSummary,
                            no_table_associations=True,
                            empty_table=True,
                        ),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('internal_analysis'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(
                            key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                            value=DbEntityCategoryKey.ANALYSIS_RESULTS
                        )]
                    )
                )
            ]).matching_scope(class_scope=self.config_entity and self.config_entity.__class__))
