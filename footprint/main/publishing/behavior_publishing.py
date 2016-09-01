
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

from footprint.client.configuration import resolve_fixture
from footprint.main.lib.functions import map_to_dict
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.region import Region
from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.presentation.result.result import Result


logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

def on_config_entity_post_save_behevior(sender, **kwargs):
    """
        Sync a ConfigEntity's Behaviors
    """
    # TODO This is obviously not fully implemented
    raise Exception("Not implemented")
    config_entity = kwargs['instance']
    logger.info("Handler: on_config_entity_post_save_behvior. ConfigEntity: %s" % config_entity.name)
    update_or_create_behaviors(config_entity)

def update_or_create_behaviors(config_entity, **kwargs):
    """
        Creates Behaviors when saving a config_entity if they do not yet exist.
        :param config_entity
        :return:
    """

    # Just process Regions and GlobalConfig
    if not isinstance(config_entity, GlobalConfig, Region):
        return

    from footprint.client.configuration.fixture import BehaviorFixture

    client_behavior_fixture = resolve_fixture(
        "behavior",
        "behavior",
        BehaviorFixture,
        config_entity.schema(),
        config_entity=config_entity)

    # Create each ResultLibrary and store them as a dict keyed by their key
    result_library_lookup = map_to_dict(lambda result_library_config: [
        result_library_config.key,
        ResultLibrary.objects.update_or_create(
            key=result_library_config.key,
            config_entity=config_entity,
            scope=config_entity.schema(),
            defaults=dict(
                name=result_library_config.name.format(config_entity.name),
                description=result_library_config.description.format(config_entity.name)
            )
        )[0]],
        client_result.result_libraries())

    #for key, result_library in result_library_lookup.items():
    #    result_library.results.all().delete()

    # Create each configured Result
    for result_config in filter(lambda result:
                                    not db_entity_keys or
                                    result.result_db_entity_key in db_entity_keys or
                                    result.source_db_entity_key in db_entity_keys,
                                client_result.results()):

        logger.info("Result Publishing Result DbEntity Key: %s" % result_config.result_db_entity_key)
        # Create the db_entity and db_entity_interest for the result
        db_entity = result_config.update_or_create_db_entity(config_entity)
        # Make the db_entity the default selected one for its key
        previous = config_entity._no_post_save_publishing
        config_entity._no_post_save_publishing = True
        config_entity.save()
        config_entity._no_post_save_publishing = previous

        # Test the query
        db_entity.parse_query(config_entity)

        db_entity_interest = DbEntityInterest.objects.get(
            config_entity=config_entity,
            db_entity__key=result_config.result_db_entity_key
        )

        # Create a result for each result key given.
        result, created, updated = Result.objects.update_or_create(
            db_enitty_interest=db_entity_interest,
            defaults=dict(
                # Use the Result's custom Medium, keyed by the Result key
                medium=result_config.resolve_result_medium(),
                configuration=result_config.get_presentation_medium_configuration())
        )
        # If created, add the result to the matching result library
        if created:
            result_library_lookup[result_config.result_library_key].presentation_media.add(result)

    # Remove orphan results and their DbEntityInterests/DbEntities
    result_library_ids = map(lambda result_library: result_library.id, ResultLibrary.objects.filter(config_entity=config_entity))
    valid_result_keys = map(lambda result_config: result_config.result_db_entity_key, client_result.results())
    orphan_results = Result.objects.filter(presentation__id__in=result_library_ids).exclude(db_entity_key__in=valid_result_keys)
    DbEntityInterest.objects.filter(config_entity=config_entity, db_entity__key__in=map(lambda result: result.db_entity_key, orphan_results)).delete()
    orphan_results.delete()


def on_config_entity_pre_delete_result(sender, **kwargs):
    """
    """
    config_entity = kwargs['instance']
