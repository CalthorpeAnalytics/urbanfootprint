
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
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from footprint.main.models.geospatial.feature import Feature
from footprint.main.models.config.scenario import FutureScenario, BaseScenario, Scenario
from footprint.main.publishing.analysis_module_publishing import on_feature_post_save_analysis_modules
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.publishing.tilestache_publishing import on_feature_post_save_tilestache
from footprint.main.utils.utils import resolvable_module_attr_path

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

# All initial signals. They can run without dependencies
# All signals that can run after features save
post_save_feature_initial = Signal(providing_args=[])

def dependent_signal_paths(signal_path):
    return []

signal_proportion_lookup = dict(
    # initial signal after save
    post_save_feature_initial=1
)

def post_save_feature_initial_publishers(cls):
    """
        AnalysisModule publishing updates DbEntity tables and then Tilestache runs to refresh any
        changes as a result of the Feature saves or Analysis
    """
    post_save_feature_initial.connect(on_feature_post_save_analysis_modules, cls, True, "analysis_module_on_feature_post_save")
    post_save_feature_initial.connect(on_feature_post_save_tilestache, cls, True, "tilestache_on_feature_post_save")

# Register receivers for all ConfigEntity classes.
# This is the config_entity of the Feature
for cls in [Scenario, BaseScenario, FutureScenario, Project, Region, GlobalConfig]:
    post_save_feature_initial_publishers(cls)


def on_feature_post_save(sender, **kwargs):
    """
        Called after one or more features save. This is called from the Feature post_save with kwargs
    """
    # todo invalidate the tiles at the current map zoom level FIRST, then do the other zoom levels
    features = kwargs['instance']
    user = get_user_model().objects.get(id=kwargs['user_id'])
    config_entity = features[0].config_entity.subclassed
    db_entity_key = features[0].db_entity_key
    logger.info("Handler: post_save_feature for config_entity {config_entity}, db_entity_key {db_entity_key}, and user {username}.".format(
        config_entity=config_entity,
        db_entity_key=db_entity_key,
        username=user.username
    ))

    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_feature_initial')

    return post_save_publishing(
        starting_signal_path,
        config_entity,
        user,
        instance=features,
        # This is a unique attribute to tell the client the DbEntity key of the Feature class
        class_key=db_entity_key,
        # The publisher client communication is only concerned with the base Feature class, not the dynamic subclasses
        instance_class=Feature,
        signal_proportion_lookup=signal_proportion_lookup,
        dependent_signal_paths=dependent_signal_paths,
        signal_prefix='post_save_feature'
    )
