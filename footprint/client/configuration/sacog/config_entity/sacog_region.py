
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

from footprint.client.configuration.sacog.base.sacog_wetland_feature import SacogWetlandFeature
from footprint.client.configuration.sacog.base.sacog_stream_feature import SacogStreamFeature
from footprint.client.configuration.sacog.base.sacog_vernal_pool_feature import SacogVernalPoolFeature
from footprint.client.configuration.sacog.base.sacog_light_rail_stops_half_mile_feature import \
    SacogLightRailStopsHalfMileFeature
from footprint.client.configuration.sacog.base.sacog_light_rail_stops_feature import SacogLightRailStopsFeature
from footprint.client.configuration.sacog.base.sacog_light_rail_stops_one_mile_feature import \
    SacogLightRailStopsOneMileFeature
from footprint.client.configuration.sacog.base.sacog_light_rail_stops_quarter_mile_feature import \
    SacogLightRailStopsQuarterMileFeature
from footprint.client.configuration.sacog.base.sacog_light_rail_feature import SacogLightRailFeature
from footprint.main.models import PhGridFeature

from footprint.main.models.base.census_tract import CensusTract

from footprint.main.models.base.canvas_feature import CanvasFeature
from footprint.main.models.base.census_block import CensusBlock
from footprint.main.models.base.census_blockgroup import CensusBlockgroup

from footprint.main.models.category import Category
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.client.configuration.fixture import RegionFixture
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.geospatial.intersection import Intersection, GeographicIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.models.geospatial.intersection import Intersection
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.utils.model_utils import uf_model
from footprint.main.utils.utils import get_property_path

__author__ = 'calthorpe_analytics'


class SacogDbEntityKey(DbEntityKey):
    EXISTING_LAND_USE_PARCELS = 'existing_land_use_parcels'
    ELK_GROVE_LAND_USE_PARCELS = 'elk_grove_land_use_parcels'
    REGION_EXISTING_LAND_USE_PARCELS = 'region_existing_land_use_parcels'
    STREAM = 'streams'
    VERNAL_POOL = 'vernal_pools'
    WETLAND = 'wetlands'
    HARDWOOD = 'hardwoods'
    LIGHT_RAIL = 'light_rail'
    LIGHT_RAIL_STOPS = 'light_rail_stops'
    LIGHT_RAIL_STOPS_ONE_MILE = 'light_rail_stops_one_mile'
    LIGHT_RAIL_STOPS_HALF_MILE = 'light_rail_stops_half_mile'
    LIGHT_RAIL_STOPS_QUARTER_MILE = 'light_rail_stops_quarter_mile'
    COMMUNITY_TYPES = 'community_types'



class SacogRegionFixture(RegionFixture):

    def default_remote_db_entities(self):
        """
            Add the SACOG background. This function is called from default_db_entities so it doesn't
            need to call the parent_fixture's method
        """
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return [
            DbEntity(
                key='sacog_background',
                url="http://services.sacog.org/arcgis/rest/services/Imagery_DigitalGlobe_2012WGS/MapServer/tile/{Z}/{Y}/{X}",
                no_feature_class_configuration=True,
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('remote_imagery')
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.BASEMAPS)]
            )
        ]

    def default_db_entities(self, **kwargs):
        """
        Region specific SACOG db_entity_setups
        :param default_dict:
        :return:
        """

        config_entity = self.config_entity
        parent_region_fixture = self.parent_fixture
        default_db_entities = parent_region_fixture.default_db_entities()
        Key = SacogDbEntityKey

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        if self.config_entity.key=='sacog':
            # Block the client-level region. We just want real regions
            return []

        remote_db_entity_setups = FixtureList(map(
            lambda db_entity: update_or_create_db_entity(config_entity, db_entity), self.default_remote_db_entities()))

        # TODO: Disabled the 'sacog_background' 'remote db entity' b/c it is throwing errors (2016-07-06)
        # return default_db_entities + remote_db_entity_setups + FixtureList([
        return default_db_entities + FixtureList([

            update_or_create_db_entity(config_entity, DbEntity(
                key=DbEntityKey.REGION_PRIMARY_GEOGRAPHY,
                # Override. If a name override is supplied, put it in. Otherwise leave null to derive it from the key
                name='Urban Base Canvas (UF)',
                # name=get_property_path(kwargs, 'overrides.%s.name' % Key.BASE),
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CanvasFeature,
                    # The Base Feature is normally considered a primary_geography unless overridden
                    primary_geography=True,
                    primary_key='geography_id',
                    primary_key_type='int',
                    # The Base Feature is normally associated to a subclass of Geography unless overridden
                    geography_class_name=get_property_path(kwargs, 'overrides.%s.geography_class_name' % Key.BASE_CANVAS) or
                                         'footprint.main.models.geographies.parcel.Parcel',
                    # Create a built_form ForeignKey to a single BuiltForm,
                    # by initially joining our 'built_form_key' attribute to its 'key' attribute
                    related_fields=dict(built_form=dict(
                        single=True,
                        related_class_name=uf_model('built_form.built_form.BuiltForm'),
                        source_class_join_field_name='built_form_key',
                        related_class_join_field_name='key',
                    ))
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('base_feature'),
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.CENSUS_TRACTS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CensusTract
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.CENSUS_BLOCKGROUPS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CensusBlockgroup
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.CENSUS_BLOCK,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CensusBlock
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.LIGHT_RAIL,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogLightRailFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.LIGHT_RAIL_STOPS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogLightRailStopsFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.LIGHT_RAIL_STOPS_ONE_MILE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogLightRailStopsOneMileFeature,
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.LIGHT_RAIL_STOPS_HALF_MILE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogLightRailStopsHalfMileFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )),

            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.LIGHT_RAIL_STOPS_QUARTER_MILE,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogLightRailStopsQuarterMileFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.VERNAL_POOL,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogVernalPoolFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('environmental_constraint')
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.WETLAND,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogWetlandFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('environmental_constraint')
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(config_entity, DbEntity(
                key=Key.STREAM,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogStreamFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('environmental_constraint')
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
        ])
