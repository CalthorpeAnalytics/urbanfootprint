
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

from footprint.client.configuration.fixture import LandUseSymbologyFixture
from footprint.client.configuration.utils import resolve_fixture
from django.conf import settings
from footprint.main.publishing.model_layer_style_initialization import create_layer_style_for_related_field

__author__ = 'calthorpe_analytics'


def primary_base_layer_style(client_land_use_definition_class, visible=False):
    # Resolve the client's specific color lookup for the PrimaryParcelFeature land_use_definition
    client_symbology = resolve_fixture(
        "presentation", "land_use_symbology", LandUseSymbologyFixture, settings.CLIENT)

    if not client_symbology:
        return

    color_lookup = client_symbology.land_use_color_lookup()

    # Create a default LayerStyle dict. This context will style the foreign key attribute of the LandUseDefinition
    return create_layer_style_for_related_field(
        'land_use_definition__id',
        client_land_use_definition_class,
        color_lookup,
        'land_use',
        visible)
