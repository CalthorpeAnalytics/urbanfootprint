
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

__author__ = 'calthorpe_analytics'

# Import all client models that have static tables so that we have a single migration path
from footprint.client.configuration.fixture import InitFixture
from footprint.client.configuration.utils import resolve_fixture, resolve_client_module
from django.conf import settings

# Load all client modules into the system, even though we only will configure one CLIENT
# This forces South to create all client specific table definitions
for client in settings.ALL_CLIENTS:
    client_init = resolve_fixture(None, "init", InitFixture, client)
    #client_init.import_database()
    for module_tuple in client_init.model_class_modules():
        # Load the module so that Django and South find the classes
        resolve_client_module(module_tuple[0], module_tuple[1], client)
