
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

from footprint.client.configuration.fixture import LayerConfigurationFixture
from footprint.client.configuration.mixins.publishing.layer_primary_base import primary_base_layer_style
from footprint.client.configuration.scag_dm.built_form.scag_dm_land_use_definition import ScagDmLandUseDefinition
from footprint.client.configuration.scag_dm.config_entity.scag_dm_config_entities import ScagDmDbEntityKey
from footprint.main.models.geospatial.geometry_type_keys import GeometryTypeKey, StyleTypeKey
from footprint.main.models.presentation.presentation_configuration import LayerConfiguration
from footprint.main.models.presentation.style_attribute import StyleValueContext, Style
from footprint.main.publishing.layer_initialization import LayerLibraryKey
from footprint.main.utils.fixture_list import FixtureList

__author__ = 'calthorpe_analytics'


class ScagDmLayerConfigurationFixtures(LayerConfigurationFixture):

    def layer_libraries(self, class_scope=None):
        return self.parent_fixture.layer_libraries(
            FixtureList(self.layers())
        )

    def layers(self, class_scope=None):
        # Combine parent fixture layers with the layers matching the given ConfigEntity scope
        return self.parent_fixture.layers() + FixtureList([
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                name='Existing Land Use Parcels 2012',
                db_entity_key=ScagDmDbEntityKey.EXISTING_LAND_USE_PARCELS_2012,
                column_alias_lookup=dict(land_use_definition__id='land_use_definition_id'),
                built_form_set_key='scag_land_uses',
                layer_style=primary_base_layer_style(ScagDmLandUseDefinition, True)
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                name='Existing Land Use Parcels 2016',
                db_entity_key=ScagDmDbEntityKey.EXISTING_LAND_USE_PARCELS_2016,
                visible=True,
                column_alias_lookup=dict(land_use_definition__id='land_use_definition_id'),
                built_form_set_key='scag_land_uses',
                layer_style=primary_base_layer_style(ScagDmLandUseDefinition, True)
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.GENERAL_PLAN_PARCELS,
                column_alias_lookup=dict(land_use_definition__id='land_use_definition_id'),
                built_form_set_key='scag_land_uses',
                layer_style=primary_base_layer_style(ScagDmLandUseDefinition)
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.ENTITLEMENT_PARCELS_2016,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='is_modified',
                            opacity=0.5,
                            style_type=StyleTypeKey.CATEGORICAL,
                            style_value_contexts=[
                                StyleValueContext(value='true', symbol='=', style=Style(
                                    polygon_fill='#FF530D',
                                    line_color='#66a0b2',
                                    line_width=1,
                                    polygon_opacity=0.4
                                )),
                                StyleValueContext(value='false', symbol='=', style=Style(
                                    polygon_fill='#2AE824',
                                    line_color='#66a0b2',
                                    line_width=1,
                                    polygon_opacity=0.4
                                ))
                        ])
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.SCENARIO_PLANNING_ZONES,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#E60000',
                                    line_width=3
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.SPHERE_OF_INFLUENCE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#FFCC00',
                                    line_width=5,
                                    line_opacity=0.8
                                ))
                            ]
                        )
                    ])
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.TIER2_TAZ,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#00CC99',
                                    line_width=4
                                ))
                            ]
                        )
                    ])
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.HABITAT_CONSERVATION_AREA,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            opacity=0.5,
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#009966',
                                    line_color='#006644',
                                    line_width=1,
                                    polygon_opacity=0.4
                                )
                            )
                        ])
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.ENDANGERED_SPECIES,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#009929',
                                    line_opacity=1,
                                    line_width=3
                                ))
                            ]
                        )
                    ])
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.COUNTY_BOUNDARY,
                layer_style=dict(
                    geometry_type = GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#FFFFCC',
                                    line_opacity=1,
                                    line_width=6
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                name='Transit Priority Areas 2012',
                db_entity_key=ScagDmDbEntityKey.TRANSIT_PRIORITY_AREAS,
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
                    ])
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                name='Major Transit Stops 2012',
                db_entity_key=ScagDmDbEntityKey.MAJOR_TRANSIT_STOPS,
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
                name='High Quality Transit Areas 2012',
                db_entity_key=ScagDmDbEntityKey.HIGH_QUALITY_TRANSIT_AREAS,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#CC00FF',
                                    polygon_opacity=0.15,
                                    line_color='#CC00FF',
                                    line_width=4,
                                    line_opacity=0.5
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                name='High Quality Transit Corridors',
                db_entity_key=ScagDmDbEntityKey.HIGH_QUALITY_TRANSIT_CORRIDORS,
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
                db_entity_key=ScagDmDbEntityKey.CENSUS_TRACTS,
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
                db_entity_key=ScagDmDbEntityKey.SUB_REGION,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#FFCC00',
                                    line_width=6,
                                    line_opacity=0.8
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.CITY_BOUNDARY,
                visible=True,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    line_color='#000000',
                                    line_opacity=1,
                                    line_width=3
                                ))
                            ]
                        )
                    ]
                )
            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.SEA_LEVEL_RISE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            style_type=StyleTypeKey.SINGLE,
                            style_value_contexts=[
                                StyleValueContext(value=None, symbol=None, style=Style(
                                    polygon_fill='#00007f',
                                    line_color='#808080',
                                    polygon_opacity=0.1
                                ))
                            ]
                        )
                    ]
                )

            ),
            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.BIKE_LANE,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.LINESTRING,
                    style_attributes=[
                        dict(
                            attribute='status',
                            style_type=StyleTypeKey.CATEGORICAL,
                            style_value_contexts=[
                                StyleValueContext(value='Existing', symbol='=', style=Style(
                                    line_color='#00cc88',
                                    line_width=4
                                )),

                                StyleValueContext(value='Proposed', symbol='=', style=Style(
                                    line_color='#ff9a00',
                                    line_width=4
                                ))
                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.FLOOD_ZONES,
                layer_style=dict(

                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='fld_zone',
                            style_type=StyleTypeKey.CATEGORICAL,
                            style_value_contexts=[
                                StyleValueContext(value='100 Year Flood Hazard', symbol='=', style=Style(
                                    polygon_fill='#885ead',
                                    line_color='#d3d3d3',
                                    line_width=1,
                                    line_opacity=0.8,
                                    polygon_opacity=0.4,
                                )),
                                StyleValueContext(value='500 Year Flood Hazard', symbol='=', style=Style(
                                    polygon_fill='#7cb0df',
                                    line_color='#d3d3d3',
                                    line_width=1,
                                    line_opacity=0.8,
                                    polygon_opacity=0.4,
                                ))
                            ]
                        )
                    ])
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.CPAD_HOLDINGS,
                layer_style=dict(
                    global_opacity=0.6,
                    geometry_type=GeometryTypeKey.POLYGON,
                    style_attributes=[
                        dict(
                            attribute='layer_scag',
                            style_type=StyleTypeKey.CATEGORICAL,
                            style_value_contexts=[
                                StyleValueContext(value='California Department of Fish and Wildlife', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#1A2E14',
                                )),

                                StyleValueContext(
                                    value='California Department of Parks and Recreation',
                                    symbol='=',
                                    style=Style(
                                        line_color='#594',
                                        line_width=1,
                                        polygon_fill='#00c5ff',
                                    )
                                ),

                                StyleValueContext(value="City", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#ff73df',
                                )),

                                StyleValueContext(value="County", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#a900e6',
                                )),

                                StyleValueContext(value="National Park Service", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#c89445',
                                )),

                                StyleValueContext(value="Non Governmental Organization", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#a87000',
                                )),

                                StyleValueContext(value="Other Federal", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#aaaa66',
                                )),

                                StyleValueContext(value="Other State", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#6699cd',
                                )),

                                StyleValueContext(value="Private", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#559944',
                                )),

                                StyleValueContext(value="Special District", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#ffbee8',
                                )),

                                StyleValueContext(value="US Bureau of Land Management", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#ffd37f',
                                )),

                                StyleValueContext(value="US Fish and Wildlife Service", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#aaff00',
                                )),

                                StyleValueContext(value="US Forest Service", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#7af5ca',
                                )),

                                StyleValueContext(value="US Military/Defense", symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#686868',
                                ))

                            ]
                        )
                    ]
                )
            ),

            LayerConfiguration(
                library_keys=[LayerLibraryKey.APPLICATION],
                db_entity_key=ScagDmDbEntityKey.FARMLAND,
                layer_style=dict(
                    geometry_type=GeometryTypeKey.POLYGON,
                    global_opacity=0.6,
                    style_attributes=[
                        dict(
                            attribute='type_scag',
                            style_type=StyleTypeKey.CATEGORICAL,
                            style_value_contexts=[
                                StyleValueContext(value='P', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#8DB359',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='S', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#BED984',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='U', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#E2F7B0',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='G', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#E3DBC5',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='L', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#F9FCDE',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='LP', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#FCF6F2',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='X', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#EBECED',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='CI', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#B37B59',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='nv', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#dbc49a',
                                    polygon_opacity=0.4
                                )),
                                StyleValueContext(value='V', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#D3D2D4',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='R', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#F2CED3',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='sAC', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#F5D489',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='D', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#F29DAA',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='W', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#96D0D6',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='I', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#ACC7A5',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='N', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#F0F0C2',
                                    polygon_opacity=0.4
                                )),

                                StyleValueContext(value='Z', symbol='=', style=Style(
                                    line_color='#594',
                                    line_width=1,
                                    polygon_fill='#ffffff',
                                    polygon_opacity=0.4
                                )),
                            ]
                        )
                    ]
                )
            )
        ])

    def import_layer_configurations(self, geometry_type):
        return self.parent_fixture.import_layer_configurations(geometry_type)
