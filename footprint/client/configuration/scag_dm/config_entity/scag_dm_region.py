
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

from footprint.client.configuration.scag_dm.base.scenario_planning_zones import ScenarioPlanningZones
from footprint.client.configuration.scag_dm.base.county_boundary import CountyBoundary
from footprint.client.configuration.scag_dm.base.cpad_holdings import CpadHoldings
from footprint.client.configuration.scag_dm.base.endangered_species import EndangeredSpecies
from footprint.client.configuration.scag_dm.base.existing_land_use_parcel import ExistingLandUseParcel
from footprint.client.configuration.scag_dm.base.farmland import Farmland
from footprint.client.configuration.scag_dm.base.flood_zones import FloodZones
from footprint.client.configuration.scag_dm.base.general_plan_parcels import GeneralPlanParcels
from footprint.client.configuration.scag_dm.base.entitlement_parcels import EntitlementParcels
from footprint.client.configuration.scag_dm.base.habitat_conservation_areas import HabitatConservationAreas
from footprint.client.configuration.scag_dm.base.high_quality_transit_areas import HighQualityTransitAreas
from footprint.client.configuration.scag_dm.base.high_quality_transit_corridors import HighQualityTransitCorridors
from footprint.client.configuration.scag_dm.base.major_transit_stops import MajorTransitStops
from footprint.client.configuration.scag_dm.base.sphere_of_influence import SphereOfInfluence
from footprint.client.configuration.scag_dm.base.sub_region import SubRegion
from footprint.client.configuration.scag_dm.base.tier2_taz import Tier2Taz
from footprint.client.configuration.scag_dm.base.transit_priority_areas import TransitPriorityAreas
from footprint.client.configuration.scag_dm.base.city_boundary import CityBoundary
from footprint.client.configuration.scag_dm.base.bike_lane import BikeLane
from footprint.client.configuration.scag_dm.base.sea_level_rise import SeaLevelRise
from footprint.client.configuration.scag_dm.config_entity.scag_dm_config_entities import ScagDmDbEntityKey
from footprint.client.configuration.scag_dm.base.census_tracts import CensusTracts
from footprint.main.models import GlobalConfig
from footprint.main.models.category import Category
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.client.configuration.fixture import RegionFixture
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.geospatial.intersection import GeographicIntersection, \
    AttributeIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.models.tag import Tag
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'



class ScagDmRegionFixture(RegionFixture):

    def default_remote_db_entities(self):
        """
            Add the any background imagery. This function is called from default_db_entities so it doesn't
            need to call the parent_fixture's method
        """
        return self.parent_config_entity_fixture.default_remote_db_entities()

    def default_db_entities(self):
        """
            Region specific db_entity_setups
        :param default_dict:
        :return:
        """

        config_entity = self.config_entity
        parent_region_fixture = self.parent_fixture
        default_db_entities = parent_region_fixture.default_db_entities()
        # The DbEntity keyspace. These keys have no prefix
        Key = ScagDmDbEntityKey
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        if isinstance(self.config_entity.parent_config_entity_subclassed, GlobalConfig):
            # Block the client-level region. We just want real regions
            return []

        return default_db_entities + FixtureList([

            update_or_create_db_entity(config_entity, DbEntity(
                name='2016 SCAG Existing Land Use Parcels',
                key=Key.REGION_EXISTING_LAND_USE_PARCELS,
                    feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=ExistingLandUseParcel,
                    primary_geography=True,
                    primary_key='source_id',
                    primary_key_type='int',
                    fields=dict(),
                    related_fields=dict(land_use_definition=dict(
                        single=True,
                        related_class_name='footprint.client.configuration.scag_dm.built_form.scag_dm_land_use_definition.ScagDmLandUseDefinition',
                        related_class_join_field_name='land_use',
                        source_class_join_field_name='scag_lu')
                    )
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference')
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.FLOOD_ZONES,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=FloodZones
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.ENDANGERED_SPECIES,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=EndangeredSpecies
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.CPAD_HOLDINGS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CpadHoldings
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.HABITAT_CONSERVATION_AREA,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=HabitatConservationAreas
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.COUNTY_BOUNDARY,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CountyBoundary
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                name='High Quality Transit Areas 2012',
                key=Key.HIGH_QUALITY_TRANSIT_AREAS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=HighQualityTransitAreas
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                name='High Quality Transit Corridors 2012',
                key=Key.HIGH_QUALITY_TRANSIT_CORRIDORS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=HighQualityTransitCorridors
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                name='Major Transit Stops 2012',
                key=Key.MAJOR_TRANSIT_STOPS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=MajorTransitStops
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                name='Transit Priority Areas 2012',
                key=Key.TRANSIT_PRIORITY_AREAS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=TransitPriorityAreas
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.FARMLAND,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=Farmland,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_GENERAL_PLAN_PARCELS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=GeneralPlanParcels,
                    primary_key='source_id',
                    primary_key_type='int',
                    fields=dict(),
                    related_fields=dict(land_use_definition=dict(
                        single=True,
                        related_class_name='footprint.client.configuration.scag_dm.built_form.scag_dm_land_use_definition.ScagDmLandUseDefinition',
                        # Use this for the resource type, since we don't want a client-specific resource URL
                        # TODO not wired up yet
                        resource_model_class_name='footprint.main.models.built_form.ClientLandUseDefinition',
                        related_class_join_field_name='land_use',
                        source_class_join_field_name='scag_gp_code')
                    )
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=AttributeIntersection()
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_ENTITLEMENT_PARCELS_2016,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=EntitlementParcels,
                    primary_key='source_id',
                    primary_key_type='int',
                    fields=dict()
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=AttributeIntersection()
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_SCENARIO_PLANNING_ZONES,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=ScenarioPlanningZones,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_SPHERE_OF_INFLUENCE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SphereOfInfluence,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_TIER2_TAZ,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=Tier2Taz,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.CENSUS_TRACTS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CensusTracts,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.SUB_REGION,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SubRegion,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.REGION_CITY_BOUNDARY,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CityBoundary,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.BIKE_LANE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=BikeLane,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.SEA_LEVEL_RISE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SeaLevelRise,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            ))
        ])
