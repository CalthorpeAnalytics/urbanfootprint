
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

from footprint.client.configuration.default.presentation.default_layer import built_form_based_layer_style
from footprint.client.configuration.fixture import LayerConfigurationFixture
from footprint.client.configuration.mixins.publishing.layer_primary_base import primary_base_layer_style
from footprint.client.configuration.sacog.config_entity.sacog_region import SacogDbEntityKey
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey, StyleTypeKey
from footprint.main.models.presentation.presentation_configuration import LayerConfiguration
from footprint.client.configuration.sacog.built_form.sacog_land_use_definition import SacogLandUseDefinition
from footprint.main.models.presentation.style_attribute import StyleValueContext, Style
from footprint.main.publishing.layer_initialization import LayerSort, LayerLibraryKey
from footprint.main.utils.fixture_list import FixtureList
from footprint.main.models.geospatial.db_entity_keys import DbEntityKey

__author__ = 'calthorpe_analytics'

class SacogLayerConfigurationFixture(LayerConfigurationFixture):

    def layer_libraries(self, class_scope=None):
        return self.parent_fixture.layer_libraries(
            FixtureList(self.layers()).matching_scope(class_scope=self.config_entity and self.config_entity.__class__))

    def layers(self, class_scope=None):

        return self.parent_fixture.layers() + FixtureList([
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.CENSUS_TRACTS,
                layer_style=dict(
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
                    ])
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.CENSUS_BLOCKGROUPS,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#CD5555',
                                    line_opacity=0.8,
                                    line_width=3
                                ))
                            ]
                        )
                    ])
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.CENSUS_BLOCK,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#E60000',
                                    line_opacity=0.8,
                                    line_width=3
                                ))
                            ]
                        )
                    ])
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.BASE_CANVAS,
                column_alias_lookup=dict(built_form__id='built_form_id'),
                layer_style=built_form_based_layer_style(),
                sort_priority=LayerSort.BASE
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.BASE_AGRICULTURE_CANVAS,
                column_alias_lookup=dict(built_form__id='built_form_id'),
                layer_style=built_form_based_layer_style(),
                sort_priority=LayerSort.BASE
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.ENERGY,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='annual_million_btus_per_unit',
                            style_type=StyleTypeKey.QUANTITATIVE,
                            style_value_contexts=[
                                StyleValueContext(value=0, symbol='=', style=Style(polygon_fill='#909090')),
                                StyleValueContext(value=0, symbol='>', style=Style(polygon_fill='#97D704')),
                                StyleValueContext(value=5, symbol='>', style=Style(polygon_fill='#B2D103')),
                                StyleValueContext(value=10, symbol='>', style=Style(polygon_fill='#CBCA03')),
                                StyleValueContext(value=15, symbol='>', style=Style(polygon_fill='#C5A703')),
                                StyleValueContext(value=20, symbol='>', style=Style(polygon_fill='#BF8603')),
                                StyleValueContext(value=30, symbol='>', style=Style(polygon_fill='#B96602')),
                                StyleValueContext(value=40, symbol='>', style=Style(polygon_fill='#B34802')),
                                StyleValueContext(value=55, symbol='>', style=Style(polygon_fill='#AD2C02')),
                                StyleValueContext(value=80, symbol='>', style=Style(polygon_fill='#A71102')),
                                StyleValueContext(value=120, symbol='>', style=Style(polygon_fill='#A1020B')),
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.WATER,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='annual_gallons_per_unit',
                            style_type=StyleTypeKey.QUANTITATIVE,
                            style_value_contexts=[
                                StyleValueContext(value=0, symbol='=', style=Style(polygon_fill='#909090')),
                                StyleValueContext(value=0, symbol='>', style=Style(polygon_fill='#B3D8FF')),
                                StyleValueContext(value=40, symbol='>', style=Style(polygon_fill='#9FC6F0')),
                                StyleValueContext(value=60, symbol='>', style=Style(polygon_fill='#8BB5E1')),
                                StyleValueContext(value=80, symbol='>', style=Style(polygon_fill='#77A4D2')),
                                StyleValueContext(value=120, symbol='>', style=Style(polygon_fill='#6392C3')),
                                StyleValueContext(value=160, symbol='>', style=Style(polygon_fill='#6392C3')),
                                StyleValueContext(value=200, symbol='>', style=Style(polygon_fill='#5081B5')),
                                StyleValueContext(value=250, symbol='>', style=Style(polygon_fill='#3C70A6')),
                                StyleValueContext(value=300, symbol='>', style=Style(polygon_fill='#285E97')),
                                StyleValueContext(value=350, symbol='>', style=Style(polygon_fill='#144D88')),
                                StyleValueContext(value=400, symbol='>', style=Style(polygon_fill='#013C7A')),
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.VMT,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='vmt_daily_per_hh',
                            style_type=StyleTypeKey.QUANTITATIVE,
                            style_value_contexts=[
                                StyleValueContext(value=0, symbol='=', style=Style(
                                    polygon_fill='#E8E8E8',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=0, symbol='>', style=Style(
                                    polygon_fill='#004d1a',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=20, symbol='>', style=Style(
                                    polygon_fill='#009933',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=30, symbol='>', style=Style(
                                    polygon_fill='#00CC33',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=40, symbol='>', style=Style(
                                    polygon_fill='#FFFF00',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=60, symbol='>', style=Style(
                                    polygon_fill='#FF9900',
                                    line_color='#909090',
                                    line_width=.3)),
                                StyleValueContext(value=80, symbol='>', style=Style(
                                    polygon_fill='#cc1500',
                                    line_color='#909090',
                                    line_width=.3))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.INCREMENT,
                column_alias_lookup=dict(built_form__id='built_form_id'),
                layer_style=built_form_based_layer_style(),
                sort_priority=LayerSort.FUTURE+1
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.END_STATE,
                visible=True,
                column_alias_lookup=dict(built_form__id='built_form_id'),
                layer_style=built_form_based_layer_style(),
                sort_priority=LayerSort.FUTURE+2
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.FUTURE_AGRICULTURE_CANVAS,
                visible=True,
                column_alias_lookup=dict(built_form__id='built_form_id'),
                layer_style=built_form_based_layer_style(),
                sort_priority=LayerSort.FUTURE+3
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.EXISTING_LAND_USE_PARCELS,
                visible=True,
                column_alias_lookup=dict(land_use_definition__id='land_use_definition_id'),
                built_form_set_key='sacog_land_use',
                layer_style=primary_base_layer_style(SacogLandUseDefinition)
            ),


            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.STREAM,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#00008B',
                                    polygon_opacity=0.75
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.VERNAL_POOL,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#008080',
                                    polygon_opacity=0.75
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.WETLAND,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#00688B',
                                    polygon_opacity=0.75
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.LIGHT_RAIL,
                layer_style=dict(
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
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.LIGHT_RAIL_STOPS,
                layer_style=dict(
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
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.LIGHT_RAIL_STOPS_ONE_MILE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#CC00FF',
                                    line_width=2
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.LIGHT_RAIL_STOPS_HALF_MILE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#CC00FF',
                                    line_width=2
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=SacogDbEntityKey.LIGHT_RAIL_STOPS_QUARTER_MILE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#CC00FF',
                                    line_width=2
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=DbEntityKey.PH_BLOCK_GROUP_OUTCOMES,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='adult_all_walk_minutes',
                            style_type=StyleTypeKey.QUANTITATIVE,
                            style_value_contexts=[
                                StyleValueContext(value=0, symbol='=', style=Style(
                                    polygon_fill='#E8E8E8',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=0, symbol='>', style=Style(
                                    polygon_fill='#C3523C',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=2, symbol='>', style=Style(
                                    polygon_fill='#B1782D',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=4, symbol='>', style=Style(
                                    polygon_fill='#9F9F1E',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=6, symbol='>', style=Style(
                                    polygon_fill='#8DC60F',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=8, symbol='>', style=Style(
                                    polygon_fill='#7BED00',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=15, symbol='>', style=Style(
                                    polygon_fill='#5FBC1E',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=20, symbol='>', style=Style(
                                    polygon_fill='#438C3D',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=25, symbol='>', style=Style(
                                    polygon_fill='#275C5B',
                                    polygon_opacity=0.3
                                )),
                                StyleValueContext(value=30, symbol='>', style=Style(
                                    polygon_fill='#0B2C7A',
                                    polygon_opacity=0.3
                                )),
                            ]
                        )
                    ]
                )
            )
        ])

    def import_layer_configurations(self, geometry_type):
        return self.parent_fixture.import_layer_configurations(geometry_type)
