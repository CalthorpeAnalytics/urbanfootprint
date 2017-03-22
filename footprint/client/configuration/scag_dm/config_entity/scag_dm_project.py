
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

from footprint.client.configuration.scag_dm.base.existing_land_use_parcel import ExistingLandUseParcel
from footprint.client.configuration.scag_dm.base.city_boundary import CityBoundary
from footprint.client.configuration.fixture import ProjectFixture
from footprint.client.configuration.scag_dm.config_entity.scag_dm_config_entities import ScagDmDbEntityKey
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.category import Category
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.geospatial.feature_class_configuration import FeatureClassConfiguration
from footprint.main.models.geospatial.intersection import GeographicIntersection, AttributeIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey

__author__ = 'calthorpe_analytics'


class ScagDmProjectFixture(ProjectFixture):

    def default_db_entities(self, **kwargs):
        """
        Project specific SACOG additional db_entities
        :param default_dict:
        :return:
        """

        project = self.config_entity
        # The DbEntity keyspace. These keys have no prefix
        Key = ScagDmDbEntityKey
        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate

        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return super(ScagDmProjectFixture, self).default_db_entities() + [

        update_or_create_db_entity(project, DbEntity(
                name='SCAG Existing Land Use Parcels 2012',
                key=Key.EXISTING_LAND_USE_PARCELS_2012,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=ExistingLandUseParcel,
                    import_from_db_entity_key=Key.REGION_EXISTING_LAND_USE_PARCELS,
                    filter_query=dict(city=project.name),
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
            )
        ),

        update_or_create_db_entity(project, DbEntity(
                key=Key.CITY_BOUNDARY,
                feature_class_configuration=FeatureClassConfiguration(
                    abstract_class=CityBoundary,
                    import_from_db_entity_key=Key.REGION_CITY_BOUNDARY,
                    filter_query=dict(city=project.name),
                    use_for_bounds=True
                  ),
                feature_behavior=FeatureBehavior(
                    behavior=get_behavior('reference'),
                    intersection=GeographicIntersection.polygon_to_centroid
                ),
                _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
            )
        )
        ]
