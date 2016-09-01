
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

from optparse import make_option
import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.conf import settings
from django.db import connection, reset_queries

from footprint.celery import app
from footprint.client.configuration.fixture import ConfigEntitiesFixture
from footprint.main.lib.functions import merge, flat_map, unique, compact_kwargs, \
    list_or_none_if_empty
from footprint.main.models import AgricultureAttributeSet, Behavior, FeatureBehavior
from footprint.main.models.built_form.primary_component_percent import PrimaryComponentPercent
from footprint.main.models.built_form.placetype_component_percent import PlacetypeComponentPercent
from footprint.main.models.presentation.result.result import Result
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.models.built_form.built_form_set import BuiltFormSet
from footprint.main.models.presentation.medium import Medium
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.built_form.urban.building_attribute_set import BuildingAttributeSet
from footprint.main.models.analysis_module.analysis_module import AnalysisModule
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.config.global_config import GlobalConfig, global_config_singleton
from footprint.main.models.config.region import Region
from footprint.main.models.config.project import Project
from footprint.main.models.database.information_schema import InformationSchema, PGNamespace
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.geospatial.intersection import Intersection
from footprint.main.models.presentation.built_form_example import BuiltFormExample
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.geospatial.db_entity import DbEntity
from footprint.main.models.application_initialization import application_initialization, recalculate_project_bounds, \
    update_or_create_config_entities, minimum_initialization
from footprint.main.models.config.scenario import BaseScenario, FutureScenario, Scenario
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.client.configuration.utils import resolve_fixture
from footprint.main.publishing import config_entity_publishing
from footprint.main.publishing import db_entity_publishing
from footprint.main.publishing.analysis_module_publishing import update_or_create_analysis_modules, \
    on_config_entity_post_save_analysis_modules, on_config_entity_pre_delete_analysis_modules
from footprint.main.publishing.built_form_publishing import on_config_entity_post_save_built_form
from footprint.main.publishing.config_entity_initialization import scenarios_per_project
from footprint.main.publishing.crud_key import CrudKey
from footprint.main.publishing.data_import_publishing import on_config_entity_post_save_data_import, \
    on_config_entity_pre_delete_data_import, DeleteImportProcessor
from footprint.main.publishing.db_entity_publishing import update_or_create_db_entity_and_interest, \
    on_config_entity_post_save_db_entity, crud_db_entities
from footprint.main.publishing.policy_publishing import on_config_entity_post_save_policy
from footprint.main.publishing.result_publishing import on_config_entity_post_save_result
from footprint.main.publishing.tilestache_publishing import on_config_entity_post_save_tilestache
from footprint.main.publishing.user_publishing import on_config_entity_post_save_group, on_db_entity_post_save_user, \
    on_config_entity_post_save_user, on_config_entity_db_entities_post_save_user
from footprint.main.publishing.layer_publishing import on_config_entity_post_save_layer, \
    delete_layer_selections, create_layer_selections
from footprint.main.publishing.user_initialization import update_or_create_users
from footprint.main.utils.dynamic_subclassing import drop_tables_for_dynamic_classes
from footprint.main.utils.utils import resolve_model, map_property_path, full_module_path, resolve_module_attr, resolvable_module_attr_path
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator


logger = logging.getLogger(__name__)


def make_option_list():
    return (
        # The following allow you to turn off publishers that are part of the initialization
        make_option('--nolayer', action='store_true', default=False, help='Skips layer publisher'),
        make_option('--noimport', action='store_true', default=False, help='Skips data import publisher'),
        make_option('--noinitializer', action='store_true', default=False, help='Skips initializer publishers'),
        make_option('--notilestache', action='store_true', help='Skips tilestache publisher'),
        make_option('--nobuilt_form', action='store_true', help='Skips built_form publisher'),
        make_option('--noresult', action='store_true', help='Skips result publisher'),
        make_option('--nodb_entity', action='store_true', help='Skips db_entity publisher'),
        make_option('--noanalysis', action='store_true', help='Skips analysis publisher'),
        make_option('--nouser', action='store_true', help='Skips user stuff'),

        # If skip is not specified, the full application initialization will occur
        # Use skip with the options below to limit initialization
        make_option('--skip', action='store_true', default=False,
                    help='Skip initialization and data creation (for just doing resave)'),
        # Use this to skip config_entities and save all db_entities directly
        make_option('--save_db_entity_interests', action='store_true', default=False,
                    help="Saves the db_entities directly to run their publishers, instead of going through the "
                         "config_entities"),
        make_option('--minimum', action='store_true', default=False,
                    help="Runs minimum_installation instead of application_initialization for testing purposes"),
        make_option('--recreate', action='store_true', default=False,
                    help='Deletes model instances prior to anything else'),
        make_option('--reconfig_entity', action='store_true', default=False,
                    help='Resave all the config_entities to trigger signals'),
        make_option('--reimport', action='store_true', default=False,
                    help='Delete imported feature tables and reimport'),
        make_option('--recreate_rel', action='store_true', default=False,
                    help='Drop feature rel tables so that they can be repopulated'),
        make_option('--recalculate_bounds', action='store_true', default=False,
                    help='Recalculates the project bounds'),
        make_option('--rebehavior', action='store_true', default=False,
                    help='Delete behaviors and dependents. Run this with --initializer and --db_entity'),

        make_option('--initializer', action='store_true', default=False,
                    help='Rerun application initializers'),
        make_option('--tilestache', action='store_true', default=False,
                    help='Explicitly run tilestache publisher'),
        make_option('--reuser', action='store_true', default=False,
                    help='Explicitly delete and recreate users and their assets'),
        make_option('--result', action='store_true', default=False, help='Explicitly run result publisher'),
        make_option('--reresult', action='store_true', default=False,
                    help='Clear results and explicitly run result publisher'),
        make_option('--policy', action='store_true', default=False, help='Explicitly run policy publisher'),
        make_option('--import', action='store_true', default=False, help="Explicitly run data_import publisher"),
        make_option('--db_entity', action='store_true', default=False,
                    help='Rerun through default db_entities to pick up configuration changes'),
        make_option('--redb_entity', action='store_true', default=False,
                    help='Delete and rerun through default db_entities to pick up configuration changes'),

        make_option('--user', action='store_true', default=False,
                    help='Rerun the user_publisher to pick up configuration changes'),
        make_option('--db_entity_permissions', action='store_true', default=False,
                    help='Rerun the user_publisher, but only for DbEntity permissions'),
        make_option('--config_entity_permissions', action='store_true', default=False,
                    help='Rerun the user_publisher, but only for ConfigEntity permissions'),
        make_option('--built_form', action='store_true', default=False, help='Explicitly run built_form publisher'),
        make_option('--rebuilt_form', action='store_true', default=False,
                    help='Delete all built_form instances and then explicitly run built_form publisher'),
        make_option('--rebuilt_form_relations', action='store_true', default=False,
                    help='Delete all relations between built_forms and then rerun built_form publisher'),
        make_option('--layer', action='store_true', default=False, help='Explicitly run layer publisher'),
        make_option('--analysis', action='store_true', default=False, help='Explicitly run analysis publisher'),
        make_option('--run_analysis', action='store_true', default=False,
                    help='Explicitly run analysis publisher + run the modules too'),

        make_option('--reanalysis', action='store_true', default=False,
                    help='Explicitly run analysis publisher after deleting the analysis module tables'),
        make_option('--relayer', action='store_true', default=False,
                    help='Delete all layers and then explicitly run layer publisher'),
        make_option('--selections', action='store_true', help='Reset config_enitty selections', default=False),

        make_option('--test_clone_scenarios', action='store_true', help='Clone scenarios to simulate a UI clone',
                    default=False),
        make_option('--test_upload_layers', action='store_true', help='Upload layers to simulate a UI upload',
                    default=False),
        make_option('--test_layer_from_selection', action='store_true',
                    help='Tests creating a layer/db_entity from from a selection', default=False),
        make_option('--inspect', action='store_true',
                    help='Specify DbEntity key(s) with db_entity_keys to inspect feature class info about it/them'),
        make_option('--dump_behaviors', action='store_true',
                    help='Dump the Behaviors of each DbEntity of each ConfigEntity'),

        # Limit which config_entities are acted upon
        make_option('--config_entity_keys',
                    help='Comma separated config_entity key list to init to limit data import to given keys'),
        # Limit which db_entities are acted on, where applicable
        make_option('--db_entity_keys',
                    help='Comma separated db_entity key list to init to limit data import to given keys'),

        make_option('--recycle', action='store_true', default=False, help='Delete config_entities marked deleted'),
        make_option('--delete_clones', action='store_true', default=False,
                    help='Deletes cloned scenarios, db_entities, and layers'),
        make_option('--delete_scenario_clones', action='store_true', default=False,
                    help='Deletes cloned scenarios'),
        make_option('--delete_test_layers', action='store_true', default=False,
                    help='Deletes test layers'),
        make_option('--relayer_selection', action='store_true', help='Recreates all layer selections'),
        make_option('--class', help='Comma separated classes in the form FutureScenario, Project, etc'),
        make_option('--dump_config_entity_permissions', action='store_true', help='Dump all permissions for all config_entities, or for those limited by class and/or config_entity_keys')
    )

class Command(BaseCommand):
    """
        This command initializes/syncs the footprint server with default and sample data. I'd like this to happen
        automatically in response to the post_syncdb event, but that event doesn't seem to fire
        (see management/__init__.py for the attempted wiring)
    """
    option_list = BaseCommand.option_list + make_option_list()

    def handle(self, *args, **options):

        AnalysisModule._no_post_save_task_run_global = True
        FootprintInit().run_footprint_init(*args, **options)


class FootprintInit(object):

    def run_footprint_init(self, *args, **options):

        if not settings.CELERY_ALWAYS_EAGER:
            raise Exception('This command must run with settings.CELERY_ALWAYS_EQUAL = True. '
                            'Add --settings=footprint.settings_init to the command line.')

        db_entity_keys = options.get('db_entity_keys').split(',') if options.get('db_entity_keys') else None
        # Replace so we can use options as kwargs
        options['db_entity_keys'] = db_entity_keys
        config_entity_keys = options.get('config_entity_keys').split(',') if options.get('config_entity_keys') else None
        # Replace so we can use options as kwargs
        options['config_entity_keys'] = config_entity_keys
        if not options.get('run_analysis'):
            AnalysisModule._no_post_save_task_run_global = True
        limit_to_classes = map(
            lambda cls: resolve_model('main.%s' % cls), (options.get('class').split(',') if options.get('class') else [])
        )
        options['limit_to_classes'] = limit_to_classes

        # Perforance testing
        if options.get('memory'):
            ConfigEntity.init_heapy()
            ConfigEntity.start_heapy_diagnosis()

        # Delete all ConfigEntity intances so they can be recreated.
        # This will cascade delete related models, but it doesn't delete
        # BuiltForms and other independent models
        if options.get('recreate'):
            for cls in filter_classes(limit_to_classes):
                cls.objects.all().delete()

        # Delete deleted config_entities
        if options.get('recycle'):
            for cls in filter_classes(limit_to_classes):
                cls.objects.filter(deleted=True).delete()
        if options.get('delete_clones') or options.get('delete_scenario_clones'):
            # Delete clones and uploads
            for cls in filter_classes(limit_to_classes):
                all_config_entities = cls.objects.all()
                for config_entity in all_config_entities:
                    if options.get('delete_clones'):
                        db_entities = map(
                            lambda db_entity_interest: db_entity_interest.db_entity,
                            DbEntityInterest.objects.filter(
                                    config_entity=config_entity,
                                    db_entity__origin_instance__isnull=False)
                        ) +\
                        filter(
                            lambda db_entity: db_entity.feature_class_configuration and \
                                              (isinstance(db_entity.feature_class_configuration, dict) or
                                               db_entity.feature_class_configuration.generated),
                            config_entity.computed_db_entities())

                        layers_to_remove = Layer.objects.filter(layer_libraries__config_entity__in=[config_entity], db_entity_interest__db_entity__key__in=map(lambda db_entity: db_entity.key, db_entities))
                        for layer in layers_to_remove:
                             # Drop the layer_selection classes
                            layer_selection_class = get_or_create_layer_selection_class_for_layer(layer)
                            drop_tables_for_dynamic_classes(
                                layer_selection_class,
                                layer_selection_class.features.field.rel.through
                            )
                        layers_to_remove.delete()

                        for layer in Layer.objects.all():
                            try:
                                layer.db_entity_interest.db_entity
                            except:
                                # orphan
                                try:
                                    # Drop the layer_selection classes
                                    layer_selection_class = get_or_create_layer_selection_class_for_layer(layer)
                                    drop_tables_for_dynamic_classes(
                                        layer_selection_class,
                                        layer_selection_class.features.field.rel.through
                                    )
                                    layer.delete()
                                except:
                                    pass
                        # DbEntities
                        for db_entity in db_entities:
                            feature_class = None
                            try:
                                feature_class = FeatureClassCreator(config_entity, db_entity).dynamic_model_class()
                            except Exception, e:
                                logger.warn("No feature class for db_entity %s could be created. Exception: %s" % (db_entity.name, e.message))
                            DeleteImportProcessor().drop_data(config_entity, db_entity)
                            db_entity.delete()

                if issubclass(cls, Scenario):
                    cloned_config_entities = cls.objects.filter(origin_instance__isnull=False)

                    # ConfigEntities and their schemas
                    if options.get('delete_clones') or options.get('delete_scenario_clones'):
                        for config_entity in cloned_config_entities:
                            PGNamespace.objects.drop_schema(config_entity.schema())
                            for db_entity in config_entity.owned_db_entities():
                                db_entity.delete()
                        cloned_config_entities.delete()

                if options.get('delete_clones') and False:
                    for built_form_set in BuiltFormSet.objects.all():
                        built_form_set.built_forms.remove(*built_form_set.built_forms.filter(origin_instance__isnull=False))
                    # BuiltForms
                    BuiltForm.objects.filter(origin_instance__isnull=False).delete()
                    # Orphaned BuiltForm assets (only an issue when corrupt saves have happened)
                    BuildingAttributeSet.objects.annotate(
                        num_buildings=Count('building'), num_buildingtypes=Count('buildingtype'), num_placetypes=Count('building')).filter(
                        num_buildings=0, num_buildingtypes=0, num_placetypes=0).delete()
                    Medium.objects.annotate(num_built_form_sets=Count('builtform')).filter(num_built_form_sets=0, key__startswith='built_form').delete()
                    BuiltFormExample.objects.annotate(num_built_form_sets=Count('builtform')).filter(num_built_form_sets=0).delete()

        if options.get('save_db_entity_interests'):
            # Save just existing db_entities--invoke dependent publishers
            for config_entity in filter_config_entities(**options):
                for db_entity_interest in config_entity.owned_db_entity_interests(**dict(db_entity__key__in=db_entity_keys) if db_entity_keys else {}):
                    db_entity_interest.save()

        else:
            # Default, run through everything, creating/updating config_entities and running
            # Dependent publishers that are not explictly disabled
            if not options.get('skip'):
                if options.get('nodb_entity'):
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_initial'),
                        on_config_entity_post_save_db_entity,
                        "db_entity_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('noimport'):
                    # Skip data importing
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_db_entities'),
                        on_config_entity_post_save_data_import,
                        "data_import_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('nolayer'):
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_db_entities'),
                        on_config_entity_post_save_layer,
                        "layer_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('noresult'):
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_db_entities'),
                        on_config_entity_post_save_result,
                        "result_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('notilestache'):
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_layers'),
                        on_config_entity_post_save_tilestache,
                        "tilestache_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('nobuilt_form'):
                    # Skip builtform presentation
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_initial'),
                        on_config_entity_post_save_built_form,
                        "built_form_publishing_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('noanalysis'):
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_imports'),
                        on_config_entity_post_save_analysis_modules,
                        "analysis_module_on_config_entity_post_save",
                        limit_to_classes)

                if options.get('nouser'):
                    # Skip user publishing
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_initial'),
                        on_config_entity_post_save_group,
                        "group_publishing_on_config_entity_post_save",
                        limit_to_classes)
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_initial'),
                        on_config_entity_post_save_user,
                        "user_publishing_on_config_entity_post_save",
                        limit_to_classes)
                    disable_signal_handler(
                        resolvable_module_attr_path(db_entity_publishing.__name__, 'post_save_db_entity_initial'),
                        on_db_entity_post_save_user,
                        "user_on_db_entity_post_save",
                        limit_to_classes)
                    disable_signal_handler(
                        resolvable_module_attr_path(config_entity_publishing.__name__, 'post_save_config_entity_db_entities'),
                        on_config_entity_db_entities_post_save_user,
                        "user_publishing_on_config_entity_db_entities_post_save",
                        limit_to_classes)


                # If skip is not specified, the full application initialization will occur
                # Use skip with the options below to limit initialization
                application_initialization(limit_to_classes=limit_to_classes) if\
                    not options.get('minimum_installation') else\
                    minimum_initialization(limit_to_class=limit_to_classes)

                # Update/Create the config_entities
                update_or_create_config_entities(limit_to_classes=limit_to_classes)
            else:
                # If skip is specified, use one or more of the following options
                # to run publishers directly for all or filtered config_entities
                if options.get('initializer'):

                    if options.get('rebehavior'):
                        # This will delete all the FeaturBehaviors too
                        for behavior in Behavior.objects.all():
                            template_feature_behavior = behavior.template_feature_behavior
                            behavior.template_feature_behavior = None
                            behavior.save()
                            if template_feature_behavior:
                                template_feature_behavior.delete()
                        FeatureBehavior.objects.all().delete()
                        for config_entity in ConfigEntity.objects.all():
                            config_entity.behavior = None

                        Behavior.objects.all().delete()
                        Intersection.objects.all().delete()

                    # Redo initializers. This is non-config_entity dependent stuff,
                    # like default style templates
                    application_initialization(
                        limit_to_classes=limit_to_classes,
                        no_post_save_publishing=True
                    )

                if options.get('user') or options.get('db_entity_permissions') or options.get('config_entity_permissions'):
                    if options.get('config_entity_permissions') or not options.get('db_entity_permissions'):
                        for config_entity in filter_config_entities(**options):
                            on_config_entity_post_save_group(None, instance=config_entity)
                        for config_entity in filter_config_entities(**options):
                            on_config_entity_post_save_user(None, instance=config_entity)
                    if not options.get('config_entity_permissions'):
                        for db_entity_interest in filter_db_entity_interests(**options):
                            on_db_entity_post_save_user(None, instance=db_entity_interest)

                if options.get('db_entity') or options.get('redb_entity'):
                    if options.get('redb_entity'):
                        DbEntityInterest.objects.all().delete()
                    # Pick up new stuff in the config_entity configurations, namely default db_entities
                    for config_entity in filter_config_entities(**options):
                        crud_db_entities(config_entity, CrudKey.SYNC, db_entity_keys)
                    missing_schemas = filter(lambda x: x.key != 'template_feature_behavior' and not x.schema, DbEntity.objects.all())
                    if len(missing_schemas) > 0:
                        raise Exception("No schemas for the following db_entities %s" % map_property_path(missing_schemas, 'key'))

                if options.get('built_form'):
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_built_form(None, instance=config_entity)
                if options.get('rebuilt_form'):
                    # This only works if their are no feature tables that reference the built forms
                    BuiltFormSet.objects.all().delete()
                    BuiltForm.objects.all().delete()
                    AgricultureAttributeSet.objects.all().delete()
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_built_form(None, instance=config_entity)
                if options.get('rebuilt_form_relations'):
                    # Redo the relationships between the built forms.
                    PrimaryComponentPercent.objects.all().delete()
                    PlacetypeComponentPercent.objects.all().delete()
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_built_form(None, instance=config_entity)

                if options.get('import'):
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_data_import(None, instance=config_entity, db_entity_keys=db_entity_keys)
                elif options.get('reimport'):
                    for config_entity in filter_config_entities(**options):
                        # Use the predelete to drop the tables
                        on_config_entity_pre_delete_data_import(None, instance=config_entity, db_entity_keys=db_entity_keys, drop_all=True)
                        # Reimport the db_entity tables for the specified config_entities/db_entity_keys
                        on_config_entity_post_save_data_import(None, instance=config_entity, db_entity_keys=db_entity_keys)
                elif options.get('recreate_rel'):
                    for config_entity in filter_config_entities(**options):
                        # Use the predelete to drop the tables
                        on_config_entity_pre_delete_data_import(None, instance=config_entity, db_entity_keys=db_entity_keys, drop_rel_only=True)
                        # Reimport the db_entity tables for the specified config_entities/db_entity_keys
                        on_config_entity_post_save_data_import(None, instance=config_entity, db_entity_keys=db_entity_keys)

                if options.get('analysis'):
                    for config_entity in filter_config_entities(**options):
                        update_or_create_analysis_modules(config_entity)

                if options.get('reanalysis'):
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_pre_delete_analysis_modules(None, instance=config_entity)
                        on_config_entity_post_save_analysis_modules(None, instance=config_entity)

                if options.get('layer') or options.get('relayer') or options.get('relayer_selection'):
                    for config_entity in filter_config_entities(**options):
                        if options.get('relayer'):
                            layers = Layer.objects.filter(**merge(dict(presentation__config_entity=config_entity),
                                                                  Intersection(db_entity_interest__db_entity__key__in=db_entity_keys) if db_entity_keys else {}))
                            for layer in layers:
                                # Remove layer_selection classes
                                layer_selection_class = get_or_create_layer_selection_class_for_layer(layer, config_entity, False)
                                if layer_selection_class:
                                    layer_selection_class.objects.all().delete()
                            # Delete the layers
                            layers.delete()
                            # Delete the LayerLibraries
                            LayerLibrary.objects.filter(
                                config_entity=config_entity
                            ).delete()
                        elif options.get('relayer_selection'):
                            # Redo just the layer selection tables
                            layers = filter_layers(**options)
                            logger.critical("Deleting layer selections for config_entity %s and layers %s" % (
                                config_entity.name, ', '.join(map(lambda layer: layer.db_entity_key, layers))
                            ))
                            delete_layer_selections(layers)
                            logger.critical("Creating layer selections for config_entity %s and layers %s" % (
                                config_entity.name, ', '.join(map(lambda layer: layer.db_entity_key, layers))
                            ))
                            create_layer_selections(layers)
                        else:
                            on_config_entity_post_save_layer(None, instance=config_entity, db_entity_keys=db_entity_keys)
                    for config_entity in filter_config_entities(**options):
                        if options.get('relayer'):
                            on_config_entity_post_save_layer(None, instance=config_entity, db_entity_keys=db_entity_keys)

                if options.get('reuser'):
                    # We don't actually recreate users since they are referenced by too many models
                    delete_layer_selections(limit_to_classes)
                    update_or_create_users()
                    create_layer_selections(limit_to_classes)

                if options.get('result') or options.get('reresult'):
                    if options.get('reresult'):
                        media = []
                        for result in Result.objects.all():
                            try:
                                result.db_entity_interest.db_entity.delete()
                                result.db_entity_interest.delete()
                                media.append(result.medium)
                            except:
                                pass
                        Result.objects.all().delete()
                        for medium in unique(media, idfun=lambda x: x.id):
                            medium.delete()
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_result(None, instance=config_entity)

                if options.get('policy'):
                    for config_entity in filter_config_entities(**options):
                        on_config_entity_post_save_policy(None, instance=config_entity)

                if options.get('tilestache'):
                    for config_entity in filter_config_entities(**merge(options, dict(limit_to_classes=[Scenario]) if not options.get('limit_to_classes') else dict())):
                        on_config_entity_post_save_tilestache(None,
                                                                                instance=config_entity,
                                                                                db_entity_keys=db_entity_keys)

        if options.get('recalculate_bounds'):
            recalculate_project_bounds()

        if options.get('dump_config_entity_permissions'):
            for config_entity in filter_config_entities(**options):
                logger.info("Dumping permissions for %s" % config_entity)
                logger.info(config_entity.pretty_print_instance_permissions())

        if options.get('reconfig_entity'):
            for config_entity in Region.objects.all():
                logger.info('Re-saving region {config_entity}'.format(config_entity=config_entity.name))
                config_entity.save()
            for config_entity in Project.objects.filter(**dict(key__in=config_entity_keys) if config_entity_keys else dict()):
                logger.info('Re-saving project {config_entity}'.format(config_entity=config_entity.name))
                config_entity.save()
            for config_entity in BaseScenario.objects.filter(**dict(key__in=config_entity_keys) if config_entity_keys else dict()):
                logger.info('Re-saving base scenario {config_entity}'.format(config_entity=config_entity.name))
                config_entity.save()
            for config_entity in FutureScenario.objects.filter(**dict(key__in=config_entity_keys) if config_entity_keys else dict()):
                logger.info('Re-saving future scenario {config_entity}'.format(config_entity=config_entity.name))
                config_entity.save()





        if options.get('delete_test_layers'):
            project = Scenario.objects.filter()[0]
            from footprint.client.configuration.fixture import ConfigEntityFixture
            client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(project)

            results = []
            for db_entity in client_fixture.import_db_entity_configurations():
                result = delete_upload_layer(db_entity, project)
                results.append(result)

        if options.get('test_upload_layers'):
            config_entity = Scenario.objects.filter()[0]
            # test_upload_layers(config_entity)
            test_upload_layers(config_entity.parent_config_entity_subclassed)

        if options.get('test_layer_from_selection'):
            config_entity = FutureScenario.objects.filter()[0]
            layer = Layer.objects.get(presentation__config_entity=config_entity, db_entity_key=DbEntityKey.BASE)
            # Create the db_entity_interest based on the upload configuration
            previous = DbEntityInterest._no_post_save_publishing
            DbEntityInterest._no_post_save_publishing = True
            db_entity_interest = update_or_create_db_entity_and_interest(config_entity, layer.db_entity)[0]
            DbEntityInterest._no_post_save_publishing = previous
            # Resave to trigger publishers
            # This will cause the data_import presentation to happen and other dependent publishers
            db_entity_interest.save()

        if options.get('test_clone_scenarios'):
            from footprint.client.configuration.fixture import ConfigEntityFixture
            create_scenario_clone(test_layer=True)

        if options.get('inspect'):
            for config_entity in filter_config_entities(**options):
                for db_entity_key in db_entity_keys:
                    db_entities = config_entity.computed_db_entities(key=db_entity_key)
                    if db_entities.count() == 1:
                        db_entity = db_entities[0]
                        feature_class_creator = FeatureClassCreator(config_entity, db_entity)
                        feature_class = feature_class_creator.dynamic_model_class()
                        logger.info("ConfigEntity: %s, DbEntity key: %s, Feature class: %s" % (config_entity.name, db_entity.name, feature_class.__name__))
                        feature_class_configuration = feature_class_creator.feature_class_configuration_from_introspection()
                        logger.info("Feature Class configuration from introspection: %s" % feature_class_configuration)

        if options.get('dump_behaviors'):
            for config_entity in filter_config_entities(**options):
                for db_entity in config_entity.computed_db_entities(**dict(key__in=db_entity_keys) if db_entity_keys else dict()):
                    logger.info("ConfigEntity: %s, DbEntity key: %s, Behaviors: %s" % (config_entity.name, db_entity.name, db_entity.feature_behavior.behavior.dump_behaviors()))
        call_command('collectstatic', interactive=False)


def create_scenario_clone(test_layer=False):
    scenario = FutureScenario.objects.filter(origin_instance__isnull=True)[0]
    if test_layer:
        cloned_layers = test_upload_layers(scenario)
    config_entities_fixture = resolve_fixture("config_entity", "config_entities", ConfigEntitiesFixture)
    import_scenario_configurations = config_entities_fixture.import_scenarios(scenario)

    for new_scenario_configuration in import_scenario_configurations:
        # Wipe out data and instance if it already exists
        matches = scenario.__class__.objects.filter(key=new_scenario_configuration['key'])
        if matches:
            on_config_entity_pre_delete_data_import(
                None, instance=matches[0])
            matches.delete()

    # Save the scenario to simulate cloning
    # Cloning happens because future_scenario is the clone's origin_instance
    scenarios = scenarios_per_project(scenario.project, import_scenario_configurations)
    for s in scenarios:
        print s, s.__dict__

    return scenarios


def sort_config_entities(config_entities):
    """
        Sort by Hierarchy
    :param config_entities:
    :return:
    """
    sort_priority = {GlobalConfig: 1, Region: 2, Project: 3, BaseScenario: 4, FutureScenario: 5}
    return sorted(map(
        lambda config_entity: resolve_scenario(config_entity) if isinstance(config_entity, Scenario) else config_entity,
        config_entities
    ), key=lambda config_entity: sort_priority[config_entity.__class__])


def resolve_scenario(scenario):
    for scenario_type in ['basescenario', 'futurescenario']:
        if hasattr(scenario, scenario_type):
            return getattr(scenario, scenario_type)
    return scenario


def config_entity_classes():
    return [BaseScenario, FutureScenario] + Scenario.lineage()


def filter_classes(limit_to_classes):
    classes = [GlobalConfig, Region, Project, BaseScenario, FutureScenario]
    if len(limit_to_classes)==0:
        return classes
    return filter(lambda cls: cls in limit_to_classes, classes)


def test_upload_layers(config_entity):
    # Tests layer upload, creating and then deleting the instances
    from footprint.client.configuration.fixture import ConfigEntityFixture
    client_fixture = ConfigEntityFixture.resolve_config_entity_fixture(config_entity)

    results = []

    # Delete anything that already exists matching the DbEntity
    for db_entity in client_fixture.import_db_entity_configurations():
        delete_upload_layer(db_entity, config_entity)

    for db_entity in client_fixture.import_db_entity_configurations():
        result = test_upload_layer(db_entity, config_entity)
        results.append(result)

    # Delete what we did
    for db_entity in client_fixture.import_db_entity_configurations():
        delete_upload_layer(db_entity, config_entity)

    return results


def delete_upload_layer(config_db_entity, config_entity):
    """
        Delete previoust test DbEntity/Layers
    :param config_db_entity:
    :param config_entity:
    :return:
    """
    DbEntityInterest._no_post_save_publishing = True
    update_or_create_db_entity_and_interest(config_entity, config_db_entity)[0]
    DbEntityInterest._no_post_save_publishing = False
    # Wipe out the previous import data since we're just testing
    on_config_entity_pre_delete_data_import(
        None, instance=config_entity, db_entity_keys=[config_db_entity.key]
    )

    Layer.objects.filter(db_entity_interest__db_entity__key=config_db_entity.key).delete()
    config_entity.db_entities.filter(key=config_db_entity.key).delete()


# ConfigEntities should not change for the lifetime of footprint_init
_CACHED_CONFIG_ENTITIES = []
def filter_config_entities(**options):
    """
        Filter by 'limit_to_classes' ConfigEntity subclasses and by config_etnity_keys options
    :param options:
    :return:
    """

    global _CACHED_CONFIG_ENTITIES
    if not _CACHED_CONFIG_ENTITIES:
        old_debug = settings.DEBUG
        settings.DEBUG = True
        reset_queries()

        _cached_config_entities = ConfigEntity.objects.filter(deleted=False)

        # This assertion makes sure we aren't overly aggressive in
        # loading the initial ConfigEntity list. In a pinch, comment
        # this out.
        # TODO: Move this to a test.
        total_entities = len(_cached_config_entities)
        assert len(connection.queries) < total_entities*13, (
            "Got %d queries for %d config_entities " % (len(connection.queries), len(_cached_config_entities)))
        settings.DEBUG = old_debug

    # Make sure we only select ConfigEntities related to the current client
    client_region = Region.objects.get(key=settings.CLIENT)
    eligible_ids = map(lambda config_entity: config_entity.id,
                       [global_config_singleton(), client_region] + list(client_region.descendants()))
    config_entities = _cached_config_entities.filter(
        id__in=eligible_ids,
        **compact_kwargs(key__in=options.get('config_entity_keys'))
    )
    # config_entities = ConfigEntity.objects.filter(deleted=False).filter(
    #     **compact_kwargs(key__in=options.get('config_entity_keys')))
    result = sort_config_entities(
        filter(
            lambda config_entity: not options.get('limit_to_classes') or isinstance(config_entity, tuple(options.get('limit_to_classes'))),
            map(lambda config_entity: config_entity.subclassed, config_entities)
        )
    )

    return result

def filter_db_entity_interests(**options):
    """
        Filter db_entities by config_entity_keys and db_entity_keys options
    :param options:
    :return:
    """
    return DbEntityInterest.objects.filter(**compact_kwargs(
        config_entity__key__in=options.get('config_entity_keys'),
        db_entity__key__in=options.get('db_entity_keys')
    ))

def filter_layers(**options):
    """
        Filter layers by config_entity_keys and db_entity_keys options
    :param options:
    :return:
    """
    return Layer.objects.filter(**compact_kwargs(
        presentation__config_entity__key__in=options.get('config_entity_keys'),
        db_entity_interest__db_entity__key__in=options.get('db_entity_keys')
    ))

def disable_signal_handler(signal_ref_path, handler, uid, limit_to_classes):
    for cls in filter_classes(limit_to_classes):
        resolve_module_attr(signal_ref_path).disconnect(handler, cls, True, uid)

    disable_signal_handler_for_celery.apply_async(
        args=(signal_ref_path, full_module_path(handler), uid, map(lambda cls: full_module_path(cls), limit_to_classes)),
        soft_time_limit=3600,
        time_limit=3600,
        countdown=1
    )

def test_upload_layer(config_db_entity, config_entity):

    db_entity_interest = update_or_create_db_entity_and_interest(config_entity, config_db_entity)[0]

    logger.info("Getting the layer")
    layer = Layer.objects.get(presentation__config_entity=config_entity, db_entity_interest=db_entity_interest)
    logger.info("Returning the layer %sw with id %s" % (layer.name, layer.id))

    return layer

@app.task
def disable_signal_handler_for_celery(signal_ref_path, handler_path, uid, limit_to_classes_paths):
    for cls in filter_classes(limit_to_classes_paths):
        resolve_module_attr(signal_ref_path).disconnect(resolve_module_attr(handler_path), resolve_module_attr(cls), True, uid)
