
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

from django.contrib.auth.models import User
from nose.tools import assert_equals
from django.utils import unittest

from footprint.client import SacogLandUseDefinition
from footprint.main.models.geospatial.feature_version import feature_revision_manager
from footprint.main.tests.test_models.version_testing import get_sample_feature, perform_updates


logger = logging.getLogger(__name__)
__author__ = 'calthorpe_analytics'

class TestFeatureVersioning(unittest.TestCase):

    def test_feature_versioning__updating(self):
        feature = get_sample_feature('irthorn_base_condition', DemoDbEntityKey.EXISTING_LAND_USE_PARCELS)
        user = User.objects.get(username=UserGroupKey.SUPERADMIN)
        runs = 2
        land_use_definitions = SacogLandUseDefinition.objects.all()[0:runs]
        perform_updates(feature_revision_manager, feature, land_use_definitions, 'land_use_definition', [user])
        for i, land_use_definition in enumerate(land_use_definitions):
            # Make sure that we have the expected comment and land_use_definition id for each version
            feature_version = feature_revision_manager.get_unique_for_object(feature)[runs-1-i]
            expected_comment = "Comment %s" % land_use_definition.id
            assert_equals(feature_version.revision.comment,
                          expected_comment,
                          "Expected feature version %s comment to have comment %s" % (feature_version.revision.id, expected_comment))
            expected_association_id = int(land_use_definition.id)
            actual_association_id = feature_version.field_dict['land_use_definition']
            assert_equals(actual_association_id,
                          expected_association_id,
                          "Expected association for version %s comment to have id %s, but alas it has id %s" % (feature_version.revision.id, expected_association_id, actual_association_id))

    def test_feature_versioning__reverting(self):
        feature = get_sample_feature('irthorn_base_condition', DemoDbEntityKey.EXISTING_LAND_USE_PARCELS)
        user = User.objects.get(username=UserGroupKey.SUPERADMIN)
        runs = 2
        land_use_definitions = SacogLandUseDefinition.objects.all()[0:runs]
        logger.info(map(lambda x: x.id, land_use_definitions))
        perform_updates(feature_revision_manager, feature, land_use_definitions, 'land_use_definition', [user])
        for i, land_use_definition in enumerate(land_use_definitions):
            # Revert to each version from newest to oldest and validate the object state
            feature_version = feature_revision_manager.get_unique_for_object(feature)[runs-1-i]  # newest is always first
            feature_version.revision.revert()
            reverted_feature = feature.__class__.objects.get(id=feature.id)
            expected_association_id = int(land_use_definition.id)
            actual_association_id = reverted_feature.land_use_definition.id
            logger.info('%s-%s' %(expected_association_id, actual_association_id))
            assert_equals(actual_association_id,
                          expected_association_id,
                          "Expected association for version %s comment to have id %s, but alas it has id %s" % (feature_version.revision.id, expected_association_id, actual_association_id))
