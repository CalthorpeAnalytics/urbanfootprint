
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

import logging
from footprint.client.configuration.fixture import LayerConfigurationFixture
from footprint.client.configuration.default.default_mixin import DefaultMixin
from footprint.main.lib.functions import first
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey, StyleTypeKey
from footprint.main.models.presentation.style_attribute import StyleValueContext, Style
from footprint.main.publishing.layer_initialization import LayerLibraryKey, LayerSort
from footprint.main.models.presentation.style_configuration import update_or_create_layer_style
from footprint.main.publishing.model_layer_style_initialization import create_layer_style_for_parent_model
from footprint.main.models.built_form.built_form import BuiltForm
from footprint.main.models.presentation.presentation_configuration import LayerConfiguration, PresentationConfiguration, ConfigurationData
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.utils.model_utils import model_dict

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class DefaultLayerConfigurationFixtures(DefaultMixin, LayerConfigurationFixture):
    def layer_libraries(self, layers=None):
        """
            Returns a PresentationConfiguration for each LayerLibrary scoped to self.config_entity.
            The instance will be saved to the LayerLibrary as a foreign key, so it is persisted at that time.
            Each instance contains LayerConfiguration instances that match it's config_entity class scope

            Layers are always in the Default LayerLibraries starting at the scope of their DbEntity's ConfigEntity
            and all the way down to the lowest scope, which should be the UserProfile.
            second LayerLibrary, Application, contains a subset of those Layers based on a user's choice of what
            should be visible in the application. A user can determine the inclusion in this subset LayerLibrary based
            on their permission level. For instance, a user with Project edit permission could decide that a Layer
            is excluded from the Project's Application LayerLibrary. This would exclude it from all Scenario and
            UserProfile level Application LayerLibraries below the Project. A User with Scenario edit permission
            could then choose to include the Layer at the Scenario or UserProfile level to bring the Layer into
            the LayerLibrary at one of those levels. Preconfigured layers use a configuration flag to determine
            whether or not the Layer should be put in the Application LayerLibrary at it's ConfigEntity scope
            (and thus adopted by child LayerLibraries)
        """
        return [
            PresentationConfiguration(
                scope=self.config_entity.schema(),
                key=LayerLibraryKey.DEFAULT,
                name='{0} Default Layer Library',  # format with config_entity key
                description='The default layer library for {0}',  # format with config_entity name
                data=ConfigurationData(
                    # This LayerLibrary always includes all Layers
                    presentation_media_configurations=layers or self.layers()
                )
            ),
            PresentationConfiguration(
                scope=self.config_entity.schema(),
                key=LayerLibraryKey.APPLICATION,
                name='{0} Application Layer Library',  # format with config_entity key
                description='The application layer library for {0}',  # format with config_entity name
                data=ConfigurationData(
                    # This LayerLibrary only includes layers that are configured to be in this library
                    # Uploaded/Created layer inclusion will be decided upon by the user at the time of creation
                    presentation_media_configurations=filter(
                        lambda layer_configuration: LayerLibraryKey.APPLICATION in layer_configuration.library_keys,
                        layers or self.layers()
                    )
                )
            )
        ]

    def background_layers(self):
        """
            Background layers are simple references to their corresponding db_entities.
        :return:
        """
        return map(
            lambda db_entity: LayerConfiguration(
                # ApplicationLibrary inclusion. This only includes mapbox as a test. It should include all
                library_keys=[LayerLibraryKey.APPLICATION] if 'mapbox' in db_entity.key else [],
                db_entity_key=db_entity.key,
                visible=db_entity.key=='mapbox_mapbox_streets',
                sort_priority=LayerSort.BACKGROUND
            ),
            # Background DbEntities must already exist at this point
            self.config_entity.computed_db_entities(no_feature_class_configuration=True))

    def layers(self):
        """
            Returns LayerConfigurations
        :return:
        """
        return FixtureList(self.background_layers()) + (
            self.parent_fixture.layers() if self.ancestor_config_entity else []
        )

    def import_layer_configurations(self, geometry_type):
        """
            Generic LayerConfigurations for db_entity layers imported into the system.
            :param geometry_type: GeometryTypeKey to use to determine the layer_style
        """
        return FixtureList([
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                # Use Feature for the template key so we match the default Feature
                # style files
                is_template_layer_configuration=True,
                # This is meant to be replaced by the imported db_entity_key
                # It serves to uniquely identify the LayerConfiguration
                # so that it can be overridden by client configurations
                db_entity_key='__to_be_replaced__',
                layer_style=self.IMPORT_LAYER_STYLES[geometry_type]
            ),
        ])

    # A lookup of default layer style based on geometry_type
    IMPORT_LAYER_STYLES = {
        GeometryTypeKey.POLYGON: dict(
            geometry_type=GeometryTypeKey.POLYGON,
            style_attributes=[
                dict(
                    style_type=StyleTypeKey.SINGLE,
                    style_value_contexts=[
                        StyleValueContext(value=None, symbol=None, style=Style(
                            line_color='#990000',
                            line_opacity=0.8,
                            line_width=3
                        ))
                    ]
                )
            ]
        ),
        GeometryTypeKey.POINT: dict(
            geometry_type=GeometryTypeKey.POINT,
            style_attributes=[
                dict(
                    style_type=StyleTypeKey.SINGLE,
                    style_value_contexts=[
                        StyleValueContext(value=None, symbol=None, style=Style(
                            marker_fill='#000080',
                            marker_width=10,
                            marker_line_color='white',
                            marker_line_width=1
                        ))
                    ]
                )
            ]
        ),
        GeometryTypeKey.LINESTRING: dict(
            geometry_type=GeometryTypeKey.LINESTRING,
            style_attributes=[
                dict(
                    style_type=StyleTypeKey.SINGLE,
                    style_value_contexts=[
                        StyleValueContext(value=None, symbol=None, style=Style(
                            line_color='#660066',
                            line_width=6
                        ))
                    ]
                )
            ]
        )
    }



    def update_or_create_layer_style(self, config_entity, layer_configuration, layer):
        """
            Updates or creates the LayerStyle for the Layer described by the given layer_configuration
        :param config_entity:
        :param layer_configuration:
        :return: The updated or created LayerStyle
        """
        try:
            # DbEntities with no backing feature_class_configuration, such as background layers, need not have styles
            no_feature_class_configuration = \
                not layer_configuration.is_template_layer_configuration \
                and config_entity.computed_db_entities(key=layer_configuration.db_entity_key)[0].no_feature_class_configuration
        except IndexError:
            raise Exception('No DbEntity with key {key} found for {config_entity}. The following DbEntities do exist {db_entity_keys}'.format(
                key=layer_configuration.db_entity_key,
                config_entity=config_entity.full_name,
            db_entity_keys=', '.join(map(lambda db_entity: db_entity.key, config_entity.computed_db_entities()))))

        if not no_feature_class_configuration:
            logger.debug(
                "Updating/Creating layer style for layer layer %s" % str(layer.id))

            layer_style = update_or_create_layer_style(
                layer_configuration.layer_style,
                layer_configuration.db_entity_key,
                layer.medium_subclassed)

            if layer:
                layer.medium = layer_style
                layer.active_style_key = layer_style.style_attributes.all()[0].key if layer.active_style_key is None else layer.active_style_key
                layer.visible_attributes = layer_style.defined_attributes
                layer.save()

            logger.debug("Updated/Created style template for layer of db_entity_key %s with template id key %s" %
                         (layer_configuration.db_entity_key, layer_style.key))
            return layer_style
        else:
            return None



def built_form_based_layer_style():
    """
        Create the LayerStyle based on the built_form_id attribute
        This layer_style lists all the available built_forms and creates
        a StyleValueContext for each built_form's LayerStyle StyleValueContext.
        A BuiltForm will typically just have one StyleValueContext defined to match
        its id value
    :return:
    """

    def built_form_style_value_context_resolver(built_form):
        style_attribute = built_form.medium_subclassed and built_form.medium_subclassed.style_attributes.get(attribute='id')
        if not style_attribute:
            return None
        # A BuiltForm must have 1 and only 1 StyleValueContext matching its id
        return style_attribute.style_value_contexts[0]

    layer_style = create_layer_style_for_parent_model(
        BuiltForm,
        built_form_style_value_context_resolver,
        'built_form'
    )
    return layer_style
