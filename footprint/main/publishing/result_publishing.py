
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

# from memory_profiler import profile
import logging
from django.contrib.auth import get_user_model
from django.db import reset_queries
from inflection import titleize

from footprint.main.models.config.scenario import BaseScenario
from footprint.main.lib.functions import map_to_dict, one_or_none
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.keys.user_group_key import UserGroupKey
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.presentation.result.result import Result
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.result_initialization import ResultLibraryKey

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'


def on_config_entity_post_save_result(sender, **kwargs):
    """
        Sync a ConfigEntity's ResultPage presentation
        :param kwargs: 'db_entity_keys' Optional list to limit which DbEntities are processed
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)

    logger.info("Handler: on_config_entity_post_save_result for %s" % config_entity.full_name)
    update_or_create_result_libraries(config_entity)


def on_db_entity_post_save_result(sender, **kwargs):
    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    if db_entity_interest.db_entity.source_db_entity_key:
        # No import to do for Result DbEntities (The only thing that could change is the query, which is evaluated
        # in real-time and requires no post-save processing)
        return
    # db_entity_interest = kwargs['instance']
    config_entity = db_entity_interest.config_entity
    db_entity = db_entity_interest.db_entity
    logger.info("Handler: on_db_entity_post_save_result. DbEntity: %s" % db_entity.full_name)
    update_or_create_result_libraries(config_entity, db_entity_keys=[db_entity.key])

    reset_queries()


def update_or_create_result_libraries(config_entity, **kwargs):
    """
        Creates a ResultLibrary and its Result instances upon saving a config_entity if they do not yet exist.
        :param config_entity
        :param kwargs: 'db_entity_keys' Optional list to limit the Results processed. Any result whose
            result_db_entity_key or source_db_entity_key is in db_entity_keys will pass through.
        :return:
    """

    # Force adoption. This is primarily so scenarios get the result_library from their parent project.
    for presentation in config_entity.presentation_set.all():
        presentation_class = type(presentation)
        presentation_subclass = presentation_class.objects.get_subclass(id=presentation.id)
        if presentation_subclass.presentation_media_alias:
            presentation_subclass._adopt_from_donor(presentation_subclass.presentation_media_alias)
    db_entity_keys = kwargs.get(
        'db_entity_keys',
        map(lambda db_entity: db_entity.key, config_entity.owned_db_entities())
    )

    from footprint.client.configuration.fixture import ResultConfigurationFixture
    from footprint.client.configuration.utils import resolve_fixture

    client_result = resolve_fixture(
        "presentation",
        "result",
        ResultConfigurationFixture,
        config_entity.schema(),
        config_entity=config_entity)

    client_result.update_or_create_media(config_entity, db_entity_keys=kwargs.get('db_entity_keys'))

    # Create each ResultLibrary and store them as a dict keyed by their key
    result_library_lookup = map_to_dict(lambda result_library_config: [
        result_library_config.key,
        ResultLibrary.objects.update_or_create(
            key=result_library_config.key,
            config_entity=config_entity,
            scope=config_entity.schema(),
            defaults=dict(
                name=result_library_config.name.format(titleize(config_entity.key)),
                description=result_library_config.description.format(config_entity.name)
            )
        )[0]],
        client_result.result_libraries())

    # Create each configured Result
    for result_config in filter(
            lambda result:
                result.result_db_entity_key in db_entity_keys or
                result.source_db_entity_key in db_entity_keys,
            client_result.results()):

        logger.info("Result Publishing Result DbEntity Key: %s from Source DbEntity Key %s" %
                    (result_config.result_db_entity_key, result_config.source_db_entity_key))
        # Make the db_entity the default selected one for its key
        previous = config_entity._no_post_save_publishing
        config_entity._no_post_save_publishing = True
        config_entity.save()
        config_entity._no_post_save_publishing = previous

        # Get the Results DbEntity if it already exists
        existing_db_entity_interest = one_or_none(DbEntityInterest.objects.filter(
            config_entity=config_entity,
            db_entity__key=result_config.result_db_entity_key
        ))
        existing_result = one_or_none(Result.objects.filter(db_entity_interest=existing_db_entity_interest))
        # Create the db_entity and db_entity_interest for the result if it doesn't exist
        db_entity_interest = result_config.update_or_create_db_entity_interest(config_entity, existing_result and existing_result.db_entity_interest)
        db_entity = db_entity_interest.db_entity
        # Test the query. This will raise an error if the query was configured wrong
        db_entity.parse_query(config_entity)

        dummy_user = get_user_model().objects.get(username=UserGroupKey.SUPERADMIN)

        # Create a result for each result key given.
        result, created, updated = Result.objects.update_or_create(
            db_entity_interest=db_entity_interest,
            name=result_config.name,
            defaults=dict(
                # Use the Result's custom Medium, keyed by the Result key
                medium=result_config.resolve_result_medium(),
                configuration=result_config.get_presentation_medium_configuration(),
                creator=dummy_user,
                updater=dummy_user)
        )

        # If created, add the result to the matching result libraries, always including the Default Library
        # Use the related_collection_adoption to make sure donor results are adopted prior
        # to adding the result if they haven't yet been
        if created:
            for library_key in [ResultLibraryKey.DEFAULT] + result_config.library_keys:
                result_library_lookup[library_key]._add('presentation_media', result)


def on_config_entity_pre_delete_result(sender, **kwargs):
    """
    """
    config_entity = kwargs['instance']
