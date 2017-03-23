
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

from django.conf import settings
from django.contrib.auth import get_user_model

from footprint.main.models import Scenario, Project
from footprint.main.models.category import Category
from footprint.main.models.config.db_entity_interest import DbEntity
from footprint.main.models.geospatial.behavior import BehaviorKey, Behavior
from footprint.main.models.geospatial.feature_behavior import FeatureBehavior
from footprint.main.models.geospatial.db_entity_configuration import update_or_create_db_entity
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.client.configuration.fixture import ProjectFixture, RegionFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.client.configuration.utils import resolve_fixture
from footprint.main.lib.functions import merge
from footprint.main.models.geospatial.intersection import GeographicIntersection
from footprint.main.models.keys.db_entity_category_key import DbEntityCategoryKey
from footprint.main.models.keys.permission_key import PermissionKey, DbEntityPermissionKey
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.utils.fixture_list import FixtureList


__author__ = 'calthorpe_analytics'


class DefaultProjectFixture(DefaultMixin, ProjectFixture):

    def feature_class_lookup(self):
        # Get the client region fixture (or the default region if the former doesn't exist)
        client_region = resolve_fixture("config_entity", "region", RegionFixture)
        region_class_lookup = client_region.feature_class_lookup()
        return merge(
            region_class_lookup,
            FeatureClassCreator(self.config_entity).key_to_dynamic_model_class_lookup(self.default_db_entities())
        )

    def default_db_entities(self, **kwargs):
        """
            Projects define DbEntities specific to the Project config_entity instance.
            Each DbEntity configured here should be persisted using update_or_clone_db_entity so that this code
            can be run many times without creating duplicates. The instances configured here are configurations--
            a persisted instance with an id will be returned for each. Similarly the FeatureClassConfiguration
            instances and FeatureBehavior instances configured will be updated or cloned.

            kwargs: overrides can be supplied to override certain values. The override behavior must be hand-crafted
            below
        :return: a dictionary of
        """
        return []

    def default_config_entity_groups(self, **kwargs):
        """
            Instructs Projects to create a UserGroup for managers and users of this region.
            The groups will be named config_entity.schema()__UserGroupKey.MANAGER and
            config_entity.schema()__UserGroupKey.USER

            Managers can do anything to the Project
            Users can do anything short of feature edit approval and should not be able to delete
             the Project (although the latter isn't codified in default_db_entity_permissions yet)
        :param kwargs:
        :return:
        """
        return [UserGroupKey.MANAGER, UserGroupKey.USER]

    def default_db_entity_permissions(self, **kwargs):
        """
            By default Managers and above can edit Project-owned DbEntities and approve Feature updates.
            Users can edit DbEntity features but cannot approve
            Everyone else can view them
        :param kwargs:
        :return:
        """
        return {
                UserGroupKey.MANAGER: DbEntityPermissionKey.ALL,  # includes APPROVAL permission
                UserGroupKey.USER: PermissionKey.ALL,  # excludes APPROVAL permission
                UserGroupKey.GUEST: PermissionKey.VIEW
        }

    def import_db_entity_configurations(self, **kwargs):
        project = self.config_entity

        # The Behavior keyspace
        behavior_key = BehaviorKey.Fab.ricate
        # Used to load Behaviors defined elsewhere
        get_behavior = lambda key: Behavior.objects.get(key=behavior_key(key))

        return map(
            lambda db_entity_dict: update_or_create_db_entity(project, db_entity_dict['value']),
            FixtureList([
                # This fixtures tests uploading a layer that came from UF by exporting to GDB
                # It verifies that we can handle an existing id column, which gets renamed to id_1
                # so that we can add a new primary key
                dict(
                    value=DbEntity(
                        name='RPLines0414',
                        key='rplines0414_1111',
                        url='file:///srv/calthorpe_media/test_uploads/dataset_57180_ed0d4399083743dbbc607a2d6a92c330.sql.zip',
                        creator=get_user_model().objects.get(username=UserGroupKey.SUPERADMIN),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('reference'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
                )),
                # This fixture tests a largish dataset
                dict(
                    value=DbEntity(
                        name='CPAD',
                        key='cpad_1454089444918',
                        url='file:///tmp/dataset_48424_45cbd88ea090485f93c72df2fd905701.sql.zip',
                        creator=get_user_model().objects.get(username=UserGroupKey.SUPERADMIN),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('reference'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
                )),
                # This fixture tests a small dataset
                dict(
                    value=DbEntity(
                        name='Lightrail',
                        key='lightrail_111111',
                        url='dataset_48708_d60bf2da001a44e8ab534dced4fb7478.sql.zip',
                        creator=get_user_model().objects.get(username=UserGroupKey.SUPERADMIN),
                        feature_behavior=FeatureBehavior(
                            behavior=get_behavior('reference'),
                            intersection=GeographicIntersection.polygon_to_polygon
                        ),
                        _categories=[Category(key=DbEntityCategoryKey.KEY_CLASSIFICATION, value=DbEntityCategoryKey.REFERENCE)]
                )),
            ]))


def project_key(name):

    if len(name) < 7:
        return name.lower().replace(' ', '_').replace(':', '')

    key_parts = []
    previous = None

    for l in name.lower():
        if l not in ['a', 'e', 'i', 'o', 'u', ' ', ':'] and previous != l:
            key_parts.append(l)
            previous = l

    return ''.join(key_parts)
