
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

from django.db import transaction
import reversion

from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator


__author__ = 'calthorpe_analytics'

def get_sample_feature(config_entity_key, db_entity_key):
    config_entity = ConfigEntity.objects.get(key=config_entity_key).subclassed
    db_entity = config_entity.computed_db_entity(key=db_entity_key)
    feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
    feature = feature_class.objects.filter()[0]
    return feature

def perform_updates(revision_manager, feature, associations, attribute, users):
    """
    Updates the feature to each value in the associations, where the associations are the
    instances stored at the given attribute
    :param feature:
    :param associations:
    :param attribute:
    :param users: users will be used for each save, round-robin style
    :return:
    """
    for i, association in enumerate(associations):
        with transaction.commit_on_success(), reversion.create_revision():
            setattr(feature, attribute, association)
            feature.updater = users[i % len(users)]
            feature.comment = "Comment %s" % association.id
            feature.approval_status = 'approved'
            feature.save()
            reversion.set_user(feature.updater)
            reversion.set_comment(feature.comment)
        version_list = revision_manager.get_unique_for_object(feature)
        version_count = len(version_list)
        assert version_count >= i, "Feature should have at least %s version but has %s" % (i, version_count)
