
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

from footprint.client.configuration.sacog.config_entity.sacog_region import SacogDbEntityKey
from footprint.client.configuration.sacog.base.elk_grove_land_use_parcel import ElkGroveLandUseParcel
from footprint.main.models import AgricultureFeature
from footprint.main.models.base.transit_stop_feature import TransitStopFeature
from footprint.main.models.analysis.vmt_features.vmt_trip_lengths_feature import VmtTripLengthsFeature
from footprint.main.models.analysis.climate_zone_feature import ClimateZoneFeature
from footprint.main.models.analysis.public_health_features.ph_grid_feature import PhGridFeature
from footprint.main.models.base.census_rates_feature import CensusRatesFeature
from footprint.main.models.base.canvas_feature import CanvasFeature
from footprint.main.models.category import Category
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.client.configuration.fixture import ProjectFixture
from footprint.client.configuration.sacog.base.sacog_existing_land_use_parcel_feature import \
    SacogExistingLandUseParcelFeature
from footprint.main.lib.functions import merge
from footprint.main.models.geospatial.intersection import Intersection, JoinTypeKey, GeographicIntersection, \
    AttributeIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.utils.model_utils import uf_model
from footprint.main.utils.utils import get_property_path

__author__ = 'calthorpe_analytics'


class SacogProjectFixture(ProjectFixture):
    def feature_class_lookup(self):
        """
            Adds mappings of custom Feature classes
        :return:
        """
        parent_fixture = self.parent_fixture
        feature_class_lookup = parent_fixture.feature_class_lookup()
        return merge(
            feature_class_lookup,
            FeatureClassCreator(self.config_entity).key_to_dynamic_model_class_lookup(self.default_db_entities())
        )

    def default_db_entities(self, **kwargs):
        """
        Project specific SACOG additional db_entities
        :param default_dict:
        :return:
        """
        project = self.config_entity
        # The DbEntity keyspace. These keys have no prefix
        Key = SacogDbEntityKey

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return super(SacogProjectFixture, self).default_db_entities() + [
            update_or_create_db_entity(project, DbEntity(
                key=DbEntityKey.BASE_CANVAS,
                # Override. If a name override is supplied, put it in. Otherwise leave null to derive it from the key
                name='UF Urban Base Canvas',
                # name=get_property_path(kwargs, 'overrides.%s.name' % Key.BASE),
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CanvasFeature,
                    # The Base Feature is normally considered a primary_geography unless overridden
                    primary_geography=get_property_path(kwargs, 'overrides.%s.primary_geography' % Key.BASE_CANVAS) or True,
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

            update_or_create_db_entity(project, DbEntity(
                key=Key.EXISTING_LAND_USE_PARCELS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=SacogExistingLandUseParcelFeature,
                    primary_key='geography_id',
                    primary_key_type='int',
                    fields=dict(),
                    related_fields=dict(land_use_definition=dict(
                        single=True,
                        related_class_name='footprint.client.configuration.sacog.built_form.sacog_land_use_definition.SacogLandUseDefinition',
                        resource_model_class_name='footprint.main.models.built_form.ClientLandUseDefinition',
                        related_class_join_field_name='land_use',
                        source_class_join_field_name='land_use')
                    )
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=AttributeIntersection(from_attribute='id', to_attribute='id')
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(project, DbEntity(
                key=DbEntityKey.BASE_AGRICULTURE_CANVAS,
                name='UF Agriculture Base Canvas (RUCS)',
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=AgricultureFeature,
                    primary_key='geography_id',
                    primary_key_type='varchar',
                    # Create a built_form ForeignKey to a single BuiltForm,
                    # by initially joining our 'built_form_key' attribute to its 'key' attribute
                    related_fields=dict(built_form=dict(
                        single=True,
                        related_class_name='footprint.main.models.built_form.built_form.BuiltForm',
                        related_class_join_field_name='key',
                        source_class_join_field_name='built_form_key')
                    )
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('base_agriculture'),
                    intersection=AttributeIntersection(join_type='attribute')
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(project, DbEntity(
                key=Key.ELK_GROVE_LAND_USE_PARCELS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=ElkGroveLandUseParcel
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.centroid_to_polygon
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(project, DbEntity(
                key=Key.CENSUS_RATES,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CensusRatesFeature
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

            update_or_create_db_entity(project, DbEntity(
                key=Key.GRID_150M,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=PhGridFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(project, DbEntity(
                key=DbEntityKey.CLIMATE_ZONES,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=ClimateZoneFeature,
                    related_fields=dict(
                        evapotranspiration_zone=dict(
                            single=True,
                            related_class_name=uf_model('policy.water.evapotranspiration_baseline.EvapotranspirationBaseline'),
                            related_class_join_field_name='zone',
                            source_class_join_field_name='evapotranspiration_zone_id'),

                        forecasting_climate_zone=dict(
                            single=True,
                            related_class_name=uf_model('policy.energy.commercial_energy_baseline.CommercialEnergyBaseline'),
                            related_class_join_field_name='zone',
                            source_class_join_field_name='forecasting_climate_zone_id'),

                        title_24_zone=dict(
                            single=True,
                            related_class_name=uf_model('policy.energy.residential_energy_baseline.ResidentialEnergyBaseline'),
                            related_class_join_field_name='zone',
                            source_class_join_field_name='title_24_zone_id')
                    )
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(project, DbEntity(
                key=DbEntityKey.VMT_FUTURE_TRIP_LENGTHS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=VmtTripLengthsFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),

            update_or_create_db_entity(project, DbEntity(
                key=DbEntityKey.VMT_BASE_TRIP_LENGTHS,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=VmtTripLengthsFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(project, DbEntity(
                key=Key.BASE_TRANSIT_STOPS,
                name='GTFS Transit Stops: 2014',
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=TransitStopFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
            update_or_create_db_entity(project, DbEntity(
                key=Key.FUTURE_TRANSIT_STOPS,
                name='GTFS and Future Transit Stops: 2040',
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=TransitStopFeature
                ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('internal_analysis'),
                    intersection=GeographicIntersection.polygon_to_polygon
                ),
                _categories=[Category(
                    key=DbEntityCategoryKey.KEY_CLASSIFICATION,
                    value=DbEntityCategoryKey.REFERENCE
                )]
            )),
        ]
