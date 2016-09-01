
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
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal

from footprint.main.models.category import Category
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.project import Project
from footprint.main.models.config.region import Region
from footprint.main.models.config.scenario import FutureScenario, BaseScenario
from footprint.main.models.user.footprint_group import GroupKey
from footprint.main.publishing import analysis_module_publishing
from footprint.main.publishing import built_form_publishing
from footprint.main.publishing import data_import_publishing
from footprint.main.publishing import db_entity_publishing
from footprint.main.publishing import layer_publishing
from footprint.main.publishing import policy_publishing
from footprint.main.publishing import result_publishing
from footprint.main.publishing import tilestache_publishing
from footprint.main.publishing import user_publishing
from footprint.main.publishing.crud_key import CrudKey
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.publishing import post_save_publishing
from footprint.main.utils.subclasses import receiver_subclasses
from footprint.main.utils.utils import resolvable_module_attr_path

logger = logging.getLogger(__name__)

# Signal for all initial publishers. They can run without dependencies
post_save_config_entity_initial = Signal(providing_args=[])
# Signal for all publishers after built_forms are processed
post_save_config_entity_built_forms = Signal(providing_args=[])
# Signal for all publishers that can run after db_entities are processed
post_save_config_entity_db_entities = Signal(providing_args=[])
# Signal for all publishers that can run after layers are processed
post_save_config_entity_layers = Signal(providing_args=[])
# Signal for all publishers that can run after data importing
post_save_config_entity_imports = Signal(providing_args=[])
# Signal for all publishers that should run after analytic modules run
post_save_config_entity_analysis_module = Signal(providing_args=[])

def post_save_config_entity_initial_publishers(cls):
    """
        DbEntity presentation, Analysis Module presentation, and BuiltForm presentation can happen in parallel as soon
        as a config_entity is saved
    """
    post_save_config_entity_initial.connect(user_publishing.on_config_entity_post_save_group, cls, True, "group_publishing_on_config_entity_post_save")
    post_save_config_entity_initial.connect(user_publishing.on_config_entity_post_save_user, cls, True, "user_publishing_on_config_entity_post_save")

    post_save_config_entity_initial.connect(built_form_publishing.on_config_entity_post_save_built_form, cls, True, "built_form_publishing_on_config_entity_post_save")

    post_save_config_entity_initial.connect(policy_publishing.on_config_entity_post_save_policy, cls, True, "policy_publishing_on_config_entity_post_save")


def post_save_config_entity_built_form_publishers(cls):
    """
        DBEntity presentation can happen after built_forms
    """
    post_save_config_entity_built_forms.connect(db_entity_publishing.on_config_entity_post_save_db_entity, cls, True, "db_entity_on_config_entity_post_save")


def post_save_config_entity_db_entities_publishers(cls):
    """
        User permissions,  Data Import presentation, Layer presentation, and Result presentation can happen after DbEntity presentation
    """
    post_save_config_entity_db_entities.connect(user_publishing.on_config_entity_db_entities_post_save_user, cls, True, "user_publishing_on_config_entity_db_entities_post_save")

    post_save_config_entity_db_entities.connect(data_import_publishing.on_config_entity_post_save_data_import, cls, True, "data_import_on_config_entity_post_save")

    post_save_config_entity_db_entities.connect(layer_publishing.on_config_entity_post_save_layer, cls, True, "layer_on_config_entity_post_save")

def post_save_config_entity_import_publishers(cls):
    """
        Result and AnalysisModule presentation can run after Data Import presentation
    """
    post_save_config_entity_imports.connect(result_publishing.on_config_entity_post_save_result, cls, True, "result_on_config_entity_post_save")
    post_save_config_entity_imports.connect(analysis_module_publishing.on_config_entity_post_save_analysis_modules, cls, True, "analysis_module_on_config_entity_post_save")


def post_save_config_entity_layers_publishers(cls):
    """
        Tilestache presentation can run after the Layer publisher
    """
    post_save_config_entity_layers.connect(tilestache_publishing.on_config_entity_post_save_tilestache, cls, True, "tilestache_on_config_entity_post_save")

def post_save_config_entity_analytic_runs_publishers(cls):
    """
        Tilestache runs after Updater tools run.
        Tilestache also runs here after analytic runs to clear the cache
        TODO this should be refined.
    """
    post_save_config_entity_analysis_module.connect(tilestache_publishing.on_post_analytic_run_tilestache, cls, True, "tilestache_on_post_analytic_run")

# Register receivers for only the lineage classes of Scenario subclasses
for cls in [FutureScenario, BaseScenario, Project, Region, GlobalConfig]:
    post_save_config_entity_initial_publishers(cls)
    post_save_config_entity_built_form_publishers(cls)
    post_save_config_entity_db_entities_publishers(cls)
    post_save_config_entity_import_publishers(cls)
    post_save_config_entity_layers_publishers(cls)
    post_save_config_entity_analytic_runs_publishers(cls)

def dependent_signal_paths(signal_path):
    """
        Gives the hierarchy of publisher signal calling order based on the given signal
        Signals are given as strings instead of paths for serialization ease
        param: signal_path. The signal path for which the dependent signals are returned
        return: An array of signal_paths or an empty array
    """

    if signal_path == resolvable_module_attr_path(__name__, 'post_save_config_entity_initial'):
        # BuiltForm dependent publishers can run after initial
        return [resolvable_module_attr_path(__name__, 'post_save_config_entity_built_forms')]
    elif signal_path == resolvable_module_attr_path(__name__, 'post_save_config_entity_built_forms'):
        # DbEntity dependent publishers can run after the built_form publishers
        return [resolvable_module_attr_path(__name__, 'post_save_config_entity_db_entities')]
    elif signal_path == resolvable_module_attr_path(__name__, 'post_save_config_entity_db_entities'):
        # Layer and DataImport dependent publishers are run after DbEntity dependent publishers
        return [resolvable_module_attr_path(__name__, 'post_save_config_entity_layers'),
                resolvable_module_attr_path(__name__, 'post_save_config_entity_imports')]
    return []

# Very wild guess about config_entity saving proportional times to send to the client
# These represent the parsed signal names sent to the client after the dependencies of
# the signal finish running
signal_proportion_lookup = dict(
    # Initial signals complete
    post_save_config_entity_initial=.20,
    # built_form dependants run after initial
    post_save_config_entity_built_forms=.20,
    # These run after built_forms
    post_save_config_entity_db_entities=.20,
    # layers and dataImports run in parallel after records
    post_save_config_entity_layers=.20,
    post_save_config_entity_imports=.20
)

@receiver_subclasses(pre_save, ConfigEntity, "config_entity_pre_save")
def on_config_entity_pre_save(sender, **kwargs):
    """
        A presave event handler. Currently this just defaults the bounds of the instance to those of its parent
    :param sender:
    :param kwargs:
    :return:
    """
    instance = InstanceBundle.extract_single_instance(**kwargs)
    if instance._no_post_save_publishing:
        return
    if not instance.pk:
        # Inherit the parent's bounds if none are defined
        if not instance.bounds:
            instance.bounds = instance.parent_config_entity.bounds

@receiver_subclasses(post_save, ConfigEntity, "config_entity_post_save")
def on_config_entity_post_save(sender, **kwargs):
    """
        Create the ConfigEntity's database schema on initial save.
        Post save starts a chain of asynchronous publishers that run according to a dependency tree.
        First publishers that are wired to the post_save_config_entity_initial signal
        run, followed by publishers dependent on signals that are dependent of
        post_save_config_entity_initial (see dependent_signal_paths)
        :param sender:
        :param kwargs:
            instance - the ConfigEntity
            created - True if the instance was just created
            sync - True if the instance should be synced to the configuration
        :return:
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    if transaction.is_managed():
        transaction.commit()
    crud_type = CrudKey.resolve_crud(**kwargs)

    # Send a message to publishers to configure after creation or update of the config_entity
    # This is executed through a Celery task so that it can run asynchronously
    if config_entity._no_post_save_publishing:
        return
    if config_entity.deleted:
        # Also do nothing if the config_entity is deleted. At some point this should do some
        # processings, such as rekeying the scenario so it doesn't conflict with new scenario keys
        return

    for child_config_entity in config_entity.children():
        # Do any needed syncing of config_entity_children
        # This currently does nothing
        child_config_entity.parent_config_entity_saved()


    if CrudKey.CLONE == crud_type:
        config_entity.add_categories(*config_entity.origin_instance.categories.all())
    elif CrudKey.CREATE == crud_type:
        # Unless preconfigured, set the basic category based on type
        if config_entity.categories.count() == 0:
            category = Category.objects.update_or_create(
                key='category',
                value='Future' if isinstance(config_entity, FutureScenario) else 'Base')[0]
            config_entity.add_categories(category)

    # TODO The default user here should be the admin, and in fact all config_entity instances
    # should simply have to have a creator
    user = config_entity.creator if config_entity.creator else get_user_model().objects.get(username=GroupKey.SUPERADMIN)
    starting_signal_path = resolvable_module_attr_path(__name__, 'post_save_config_entity_initial')

    logger.info("Handler: post_save_config_entity for config_entity {config_entity} and user {username}".format(
        config_entity=config_entity,
        username=user.username))

    return post_save_publishing(
        starting_signal_path,
        config_entity,
        user,
        instance=config_entity,
        signal_proportion_lookup=signal_proportion_lookup,
        dependent_signal_paths=dependent_signal_paths,
        signal_prefix='post_save_config_entity',
        crud_type=crud_type)
