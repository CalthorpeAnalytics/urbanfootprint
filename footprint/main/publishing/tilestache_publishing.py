
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
import re
from django.db import reset_queries
from guardian.shortcuts import get_users_with_perms
from django.conf import settings
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.presentation.style_configuration import create_cartocss_template
from footprint.main.publishing.instance_bundle import InstanceBundle
from footprint.main.publishing.layer_initialization import LayerLibraryKey
from footprint.main.utils.utils import database_settings, get_property_path
from footprint.main.lib.functions import merge, unique, map_to_dict, map_property
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.main.utils.utils import connection_dict
from tilestache_uf.config import build_vector_layer_config, build_raster_layer_config, build_mml_json
from tilestache_uf.models import CACHES
from tilestache_uf.models import Layer as TSLayer
from tilestache_uf.models import Config
from tilestache_uf.utils import invalidate_feature_cache, carto_css, invalidate_cache


logger = logging.getLogger(__name__)


def resolve_layers(layer_libraries, **kwargs):
    """
        Resolve layers for the given config_entity and kwargs
        :param config_entity:
        :param kwargs specify an array of DbEntity keys in kwargs['db_entity_keys'] to restrict the
        layers to those matching the keys
    """
    logger.info("Searching for Layer in LayerLibraries: {0}".format(', '.join([l.key for l in layer_libraries])))

    filter_by = dict(layer_libraries__in=layer_libraries)
    if kwargs.get('db_entity_keys'):
        filter_by['db_entity_interest__db_entity__key__in'] = kwargs['db_entity_keys']

    layers = Layer.objects.filter(**filter_by)
    filtered_layers = [l for l in layers
                       if l.db_entity_interest.db_entity.feature_class_configuration
                       and l.db_entity_interest.db_entity.is_valid]

    logger.info("Found Layers to Invalidate: %s" % ', '.join([l.name for l in filtered_layers]))
    return filtered_layers


def on_config_entity_post_save_tilestache(sender, **kwargs):
    """
        Update/Create the tilestache data for the layers given DbEntityInterest
        :param: kwargs: Optional db_entity_keys to limit the layers to those of the given keys
    """
    config_entity = InstanceBundle.extract_single_instance(**kwargs)
    logger.info("Handler: on_config_entity_post_tilestache. ConfigEntity: %s" % config_entity.name)
    if not isinstance(config_entity, Scenario):
        return

    _on_post_save_tilestache(config_entity, **kwargs)

    reset_queries()

def on_db_entity_post_save_tilestache(sender, **kwargs):
    """
        Update/Create the tilestache data for a layer after a new db_entity is imported
    """
    db_entity_interest = InstanceBundle.extract_single_instance(**kwargs)
    config_entity = db_entity_interest.config_entity.subclassed
    db_entity = db_entity_interest.db_entity

    #return if the db_entity was not created from an user imported feature - tilestache will be handled elsewhere
    if not db_entity.feature_class_configuration.generated:
        return

    _on_post_save_tilestache(config_entity, db_entity_keys=[db_entity.key])

    reset_queries()

def on_layer_post_save_tilestache(sender, **kwargs):
    """
        Update/Create the tilestache data for the layer(s) of the given Layer
    """

    logger.info("Handler: on_layer_post_save_tilestache")

    layer = InstanceBundle.extract_single_instance(**kwargs)
    db_entity_interest = layer.db_entity_interest
    config_entity = db_entity_interest.config_entity.subclassed
    db_entity = db_entity_interest.db_entity

    _on_post_save_tilestache(config_entity, db_entity_keys=[db_entity.key])

    reset_queries()


def on_feature_post_save_tilestache(sender, **kwargs):
    """
        Update/Create the tilestache data for the layers of the given feature
    """

    features = kwargs['instance']
    config_entity = features[0].config_entity.subclassed
    db_entity_interest = config_entity.computed_db_entity_interests(db_entity__key=features[0].db_entity_key)[0]
    db_entity = db_entity_interest.db_entity
    logger.info("Handler: on_feature_post_save_tilestache for config_entity %s and db_entity %s" %\
                    (config_entity.name, db_entity.key))

    ids = map(lambda obj: obj.id, features)
    feature_class = config_entity.db_entity_feature_class(db_entity.key)
    queryset = feature_class.objects.filter(id__in=ids)
    # Find all scenarios under the config_entity, whatever it's scope
    # We need to refresh all LayerLibraries of those scenarios
    scenarios = config_entity.descendants_by_type(Scenario) if\
        not isinstance(config_entity, Scenario)\
        else [config_entity]
    if not scenarios:
        raise Exception("No scenarios found to invalidate for config_entity %s" % config_entity.full_name)

    logger.info("Handler: on_feature_post_save_tilestache. Invalidate layer of scenarios %s" % \
                (map(lambda scenario: scenario.id, scenarios)))
    layer_libraries = LayerLibrary.objects.filter(
        config_entity__id__in=map(lambda scenario: scenario.id, scenarios),
        key='layer_library__default'
    )
    for layer in resolve_layers(layer_libraries, db_entity_keys=[db_entity.key]):
        logger.info("Handler: on_feature_post_save_tilestache. Invalidate layer %s, queryset: %s" % (layer.medium_subclassed.style_attributes.all(), queryset))
        for attr in layer.medium_subclassed.style_attributes.all():
            #
            layer_key = "layer:{layer},attr_id:{attribute},type:raster".format(layer=layer.id, attribute=attr.id)
            invalidate_feature_cache(layer_key, queryset)


def _on_post_save_tilestache(config_entity, **kwargs):
    """
        Update/Create of the tilestache data for layers of the config_entity
        :param: config_entity
        :param: kwargs: Optional db_entity_keys to limit the layers to those of the given keys
    """

    layer_libraries = LayerLibrary.objects.filter(
        scope=config_entity.schema(),
        config_entity=config_entity,
        key='layer_library__default'
    )
    layers = resolve_layers(layer_libraries, **kwargs)
    modify_config(config_entity, layers, **kwargs)


def modify_config(config_entity, layers, ignore_raster_layer=False, **kwargs):
    """
        Using the attributes of the given Layer objects, creates one or more TSLayer objects in the DB to be read by
         TileStache. Each layer instance is used to create a raster and selection (vector) layer for
         each configured attribute. These layers are keyed uniquely by the layer instance id, attribute, and layer type,
         so they will simply overwrite themselves in the config and accumulate.

    :param config_entity:
    :param layers:
    :return:
    """

    default_config = CACHES[getattr(settings, 'TILE_CACHE', "none")]
    Config.objects.get_or_create(name='default', defaults=dict(cache=default_config))
    for layer in layers:
        logger.info("Recreating cartocss & invalidating cache for layer {layer} of"
                    "DbEntity key {db_entity_key})".format(
                        layer=layer.full_name,
                        db_entity_key=layer.db_entity_key)
                    )
        subclassed_layer_style = layer.medium_subclassed

        if subclassed_layer_style:
            # Create a vector, raster, and vector selection layer for each attribute listed in the style attributes
            for style_attribute in subclassed_layer_style.style_attributes.all():
                style_attribute_id = style_attribute.id
                logger.info("Creating tilestache layers for layer %s, attribute %s" % (layer.full_name, style_attribute_id))

                tilestache_layers = create_layer_selection(config_entity, layer, style_attribute_id)

                if not ignore_raster_layer:
                    # generate the cartocss for each layer attribute that will be utilized by tilestach
                    cartocss = make_carto_css(layer, style_attribute)
                    tilestache_layers = [create_raster_layer(layer, style_attribute_id, cartocss)] + tilestache_layers

                for tilestache_layer in tilestache_layers:

                    tslayer, created = TSLayer.objects.get_or_create(
                        key=tilestache_layer.key,
                        defaults=dict(value=tilestache_layer.value)
                    )

                    updated = False
                    if not created:
                        if tslayer.value != tilestache_layer.value:
                            tslayer.value = tilestache_layer.value
                            tslayer.save()
                            updated = True

                    if created or updated or 'raster' in tslayer.key:
                        logger.info("invalidating tilestache layers for layer %s, attribute_id %s, tsLayerKey %s" %
                                    (layer.full_name, style_attribute_id, tilestache_layer.key))
                        invalidate_cache(tslayer.key)


def on_config_entity_pre_delete_tilestache(sender, **kwargs):
    # todo delete layers when we delete config entities
    pass


def create_vector_layer(config_entity, layer, attribute):
    # If the db_entity doesn't have an explicit query create a query from the table and schema that joins
    # in the geography column.
    db_entity = layer.db_entity_interest.db_entity
    query = create_query(attribute, config_entity, layer)
    connection = connection_dict(layer.config_entity.db)

    vector_layer = build_vector_layer_config(merge(connection,
                dict(query=query, column="wkb_geometry",)), client_id_property=db_entity._meta.pk.name)

    return TSLayer(key="layer_{0}_{1}_vector".format(layer.id, attribute), value=vector_layer)


def create_raster_layer(layer, attribute_id, cartocss):
    raster_layer = build_raster_layer_config(cartocss)

    layer_key = "layer:{layer},attr_id:{attribute},type:{type}".format(layer=layer.id, attribute=attribute_id, type='raster')
    logger.info("Creating layer %s" % layer_key)

    return TSLayer(key=layer_key, value=raster_layer)


def create_query(attribute, config_entity, layer):

    db_entity = layer.db_entity_interest.db_entity
    feature_class = config_entity.db_entity_feature_class(db_entity.key)
    # Create a query that selects the wkb_geometry and the attribute we need
    # There's nothing to prevent styling multiple attributes in the future
    try:
        query = str(feature_class.objects.values(*unique(['wkb_geometry', attribute])).query)
    except Exception, e:
        raise Exception("Error creating the query for db_entity %s. Original exception: %s" % (db_entity.key, e.message))
    column_alias = get_property_path(layer.configuration, 'column_alias_lookup.{0}'.format(attribute))

    # This would be better done by values() supporting aliases:
    # https://code.djangoproject.com/attachment/ticket/16735/column_alias.diff

    # There is a patch available at https://code.djangoproject.com/attachment/ticket/16735/column_alias.diff
    # that could be applied instead of this:
    # Replace the select column with the colum as alias.
    # Only 1 replacement is done to avoid mutilating a join with the same column

    updated_query = query.replace(
        '{column_alias}"'.format(column_alias=column_alias), '{column_alias}" as {attribute}'.format(
            column_alias=column_alias, attribute=attribute), 1) if column_alias else query
    return updated_query


def create_layer_selection(config_entity, layer, attribute_id):
    db_entity = layer.db_entity_interest.db_entity
    connection = connection_dict(layer.config_entity.db)

    tilestache_layers = []

    users = set(get_users_with_perms(config_entity)) | set(get_users_with_perms(layer.db_entity_interest.db_entity))

    # Make sure layer_selection instances exist for the users
    from footprint.main.publishing.layer_publishing import update_or_create_layer_selections_for_layer
    update_or_create_layer_selections_for_layer(layer, users=users)

    logger.info("Get/Create layer_selection for config_entity %s, layer %s, users %s" %\
                (config_entity.key, layer.db_entity_key, ','.join(map(lambda user: user.username, users))))
    # Each layer has a dynamic class representing its SelectedFeature table
    get_or_create_layer_selection_class_for_layer(layer)
    if not users:
        return tilestache_layers

    config_entity.db_entity_feature_class(key=layer.db_entity_key)
    layer_selection_class = get_or_create_layer_selection_class_for_layer(layer, config_entity)
    # Take the first user to create a template query
    user = list(users)[0]
    # Each LayerSelection instance is per user
    layer_selection = layer_selection_class.objects.get_or_create(user=user)[0]
    # Extract the query from the QuerySet
    query = re.sub(
        r'"layer_selection_id" = \d+',
        r'"layer_selection_id" = {user_id}',
        str(layer_selection.selected_features.values('wkb_geometry', 'id').query))
    logger.info("Creating tilestache layer_selection for layer %s, user %s, query: %s" % (layer.full_name, user.username, query))
    user_id_lookup = map_to_dict(lambda layer_selection: [layer_selection.user.id, layer_selection.id], layer_selection_class.objects.all())

    # Embed the id in the Geojson for each feature.
    # Nothing else is needed, since all other attributes can be looked up based on the id
    id_field = map(lambda field: field.name + '_id', layer_selection.feature_class._meta.parents.values())[0]

    vector_selection_layer = build_vector_layer_config(
        parameters=merge(connection, dict(query=query, column="wkb_geometry", user_id_lookup=user_id_lookup)),
        provider_id_property=id_field,
        client_id_property=db_entity._meta.pk.name
    )

    layer_key = "layer:{layer},attr_id:{attribute},type:{type}".format(layer=layer.id, attribute=attribute_id, type='selection')
    logger.info("Creating layer %s" % layer_key)
    tilestache_layers.append(TSLayer(key=layer_key, value=vector_selection_layer))
    return tilestache_layers


def style_id(layer, style_attribute):
    layer_library = layer.owning_presentation
    return 'style__{0}__{1}__{2}__{3}'.format(layer_library.config_entity_subclassed.id, layer_library.id, layer.db_entity_key, style_attribute.id)


def render_attribute_styles(layer, style_attribute):
    """
        uses the style attribute to generate cartocss styling for a specific attribute on a layer. The results are
        placed in the layer.rendered_medium in the form
        dict(attribute1:dict('css':rendered_css, 'cartocss': rendered_carto_css)). The carto_css is actually a file
        path since this is required by tilestache (TODO that it can't be a string)
    :param layer:
    :return:
    """
    # Create this dict if it doesn't yet exist
    layer.rendered_medium = layer.rendered_medium or {}
    layer.rendered_medium[style_attribute.id] = {}
    # This makes the mml and xml, and just returns the xml path
    layer.rendered_medium[style_attribute.id]['cartocss'] = make_carto_css(layer, style_attribute)

    previous = layer._no_post_save_publishing
    layer._no_post_save_publishing = True
    layer.save()
    layer._no_post_save_publishing = previous

    return layer


def make_carto_css(layer, style_attribute):
    """
    Renders a mapnik XML file based on the properties of the layer and, optionally,
    style attributes. This process first writes an MML file to the filesystem. It then invokes the node.js
    carto command to create a carto xml file

    :param layer:
    :param attribute:
    :return:
    """
    mml = make_mml(layer, style_attribute)
    xml_filepath = carto_css(mml, style_id(layer, style_attribute))
    return xml_filepath


def make_mml(layer, style_attribute):
    """
    Generates mml string from a layer and a style
    :param layer: Layer object
    :param attribute: the attribute of the layer object that is getting styled

    :return:
    """
    attribute = style_attribute.attribute if style_attribute.attribute is not None else 'wkb_geometry'
    carto_css_style = cartocss_data(layer, style_attribute)
    db = database_settings(layer.config_entity.db)
    query = create_query(attribute, layer.config_entity, layer)
    db_entity = layer.db_entity_interest.db_entity
    # Get the base version of the feature class that holds wkb_geometry
    feature_class = layer.config_entity.db_entity_feature_class(db_entity.key, base_feature_class=True)

    return build_mml_json(db,
                          query=query,
                          geom_table=feature_class._meta.db_table,
                          layer_id=layer.id,
                          name=style_id(layer, style_attribute),
                          cls=db_entity.key,
                          style=carto_css_style)


def cartocss_data(layer, style_attribute):
    """
    :param layer: the layer to be styled
    :param attribute: The attribute whose cartocss is needed
    :return  dict with an id in the form {layer.name}.mss and data key valued by the rendered template
    """
    logger.debug("Handler: Generating Cartocss for %s. Style Attribute: %s" % (layer.medium_subclassed, style_attribute))

    # We might have 'css' parallel to cartocss in the future
    cartocss = create_cartocss_template(layer.medium_subclassed, style_attribute)
    return {
        'id': '{0}.mss'.format(style_id(layer, style_attribute)),
        'data': cartocss
    }


def on_post_analytic_run_tilestache(sender, **kwargs):
    """
        Responds to analytic module runs
        kwargs: module is the string name of the module (TODO covert to instance)
            config_entity is the config_entity that ran
    :return:
    """

    module = kwargs['analysis_module'].key
    config_entity = kwargs['config_entity']

    logger.info("Handler: on_post_analytic_run_tilestache. ConfigEntity: %s. Module %s" % (config_entity.name, module))
    # Find the Default LayerLibrary so that we can invalidate all Layers or those matching our specified
    # DbEntity keys
    layer_library = LayerLibrary.objects.get(config_entity=config_entity, key=LayerLibraryKey.DEFAULT)
    dependent_db_entity_keys = []

    # todo is this redundantly clearing the cache for these layers?
    if module == 'core':
        dependent_db_entity_keys = [DbEntityKey.INCREMENT]

    if module == 'vmt':
        dependent_db_entity_keys = [DbEntityKey.VMT]

    if module == 'agriculture':
        # we clear the cache when we paint, not after running the analysis

        # if isinstance(config_entity.subclassed, FutureScenario):
        #     dependent_db_entity_keys = [DbEntityKey.FUTURE_AGRICULTURE]
        # elif isinstance(config_entity.subclassed, BaseScenario):
        #     dependent_db_entity_keys = [DbEntityKey.BASE_AGRICULTURE]
        dependent_db_entity_keys = []

    if not dependent_db_entity_keys:
        return

    layers = layer_library.layers.filter(db_entity_interest__db_entity__key__in=dependent_db_entity_keys)

    # Invalidate these layers
    for layer in layers:
        # generate relevant layer keys and invalidate caches
        layer.invalidate()

def on_post_save_built_form_tilestache(sender, **kwargs):
    """
    A signal handler to invalidate relevant layers of the tilestache cache after a BuiltForm instances is created or updated.
    """

    # Find all DbEntities that reference built_form.
    # TODO these should inspect the feature class in the future for the built_form attribute or similar
    built_forms = kwargs['instance']
    logger.info("Processing TileStache updates for built forms: {0}".format(
        ', '.join(map_property(built_forms, 'name'))
    ))

    # if we are just editing the attributes of primary components (which are never visualized) skip the time consuming
    # layer invalidation and tilestache recreation.
    built_form_class_name = built_forms[0].__class__.__name__
    if built_form_class_name in ['Building', 'Crop', 'PrimaryComponent']:
        return

    if built_form_class_name in ['CropType', 'LandscapeType']:
        built_form_dependent_db_entity_keys = [DbEntityKey.FUTURE_AGRICULTURE, DbEntityKey.BASE_AGRICULTURE]
    else:
        built_form_dependent_db_entity_keys = [DbEntityKey.END_STATE, DbEntityKey.BASE_CANVAS]

    for layer_library in LayerLibrary.objects.filter(deleted=False):
        _on_post_save_tilestache(layer_library.config_entity, db_entity_keys=built_form_dependent_db_entity_keys)
