
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

from footprint.client import SacogLandUseDefinition
from footprint.client.configuration.sacog.config_entity.sacog_region import SacogDbEntityKey
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.geospatial.feature_version import feature_revision_manager
from footprint.main.tests.test_api.api_test import ApiTest
from footprint.main.tests.test_models.version_testing import get_sample_feature, perform_updates


__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class TestFeatureRevisionApi(ApiTest):

    def test_feature_revision_api(self):
        """
            Make sure that the API can return all the versions of a feature
        :return:
        """
        feature = get_sample_feature('irthorn_base_condition', SacogDbEntityKey.EXISTING_LAND_USE_PARCELS)
        user = User.objects.get(username=UserGroupKey.SUPERADMIN)
        runs = 2
        land_use_definitions = SacogLandUseDefinition.objects.all()[0:runs]
        # Update the feature [runs] times
        perform_updates(feature_revision_manager, feature, land_use_definitions, 'land_use_definition', [user])
        # Fetch the feature revisions from the API
        resource_name = 'feature_revision'
        # We currently use the user's LayerSelection along with the feature id to fetch the revision history
        # Alternatively the resource could be configured accept a config_entity id, db_entity id, and feature id
        # Or we could use a combination of these ids to define a unique_id like we do with layer_selection
        feature_class = feature.__class__
        config_entity = feature_class.config_entity
        db_entity_key = feature_class.db_entity_key
        layer = Layer.objects.get(db_entity_key=db_entity_key, presentation__config_entity=config_entity)

        response = self.get(resource_name, user=user, query_params=dict(layer__id=layer.id, id=feature.id))
        api_feature_versions = self.deserialize(response)['objects']

        for i, land_use_definition in enumerate(land_use_definitions):
            # Make sure that we have the expected comment and land_use_definition id for each version
            reverse_i = runs - 1 - i
            feature_version = feature_revision_manager.get_unique_for_object(feature)[reverse_i]
            # These should be in the same order--newest to oldest
            api_feature_version = api_feature_versions[reverse_i]

            assert_equals(
                api_feature_version['revision']['comment'],
                feature_version.revision.comment,
                "Expected api feature version %s comment to have comment %s but it has comment %s" %\
                    (feature_version.revision.id, feature_version.revision.comment, api_feature_version['revision']['comment']))
            expected_association_id = int(land_use_definition.id)
            actual_association_id = api_feature_version['object_version'].land_use_definition
            assert_equals(actual_association_id,
                          expected_association_id,
                          "Expected association for version %s comment to have id %s, but alas it has id %s" % (feature_version.revision.id, expected_association_id, actual_association_id))
