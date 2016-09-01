
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


# List the following imports because they have Django signal receivers that need to fire
from footprint.main.publishing import layer_initialization, layer_publishing, \
    analysis_module_publishing, result_initialization, result_publishing, data_import_publishing, \
    built_form_publishing, tilestache_publishing, db_entity_publishing, user_publishing, config_entity_publishing
