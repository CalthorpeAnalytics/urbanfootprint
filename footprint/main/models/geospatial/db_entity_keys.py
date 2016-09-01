
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

from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'


class DbEntityKey(Keys):
    """
        A Key class to key DbEntity instances
    """
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            # No prefix since these are so fundamental and are used to create table names,
            # so we don't want them any longer than needed to clearly describe the db_entity
            return ''
    # Preconfigured keys
    # Some of these have the word feature in order to match the generated data tables
    # They should all be normalized to remove 'feature'
    BASE_CANVAS = 'base_canvas'
    BASE_PARCEL_CANVAS = 'base_parcel_canvas'
    REGION_PRIMARY_GEOGRAPHY = 'region_primary_geography'
    REGION_BASE_CANVAS = 'region_base_canvas'
    CPAD_HOLDINGS = 'cpad_holdings'
    REGION_CPAD_HOLDINGS = 'region_cpad_holdings'
    CENSUS_TRACTS = 'census_tracts'
    CENSUS_BLOCKGROUPS = 'census_blockgroups'
    CENSUS_BLOCK = 'census_blocks'
    CENSUS_RATES = 'census_rates'
    REGION_CENSUS_RATES = 'region_census_rates'
    BASE_AGRICULTURE_CANVAS = 'base_agriculture_canvas'
    REGION_BASE_AGRICULTURE_CANVAS = 'region_base_agriculture_canvas'
    CLIMATE_ZONES = 'climate_zones'
    REGION_CLIMATE_ZONES = 'region_climate_zones'
    INCREMENT = 'scenario_increment'
    END_STATE = 'scenario_end_state'
    FUTURE_AGRICULTURE_CANVAS = 'future_agriculture_canvas'
    GRID_150M = 'grid_150m'
    REGION_GRID_150M = 'region_grid_150m'
    STREET_CENTER_LINES = 'street_center_lines'
    BASE_TRANSIT_STOPS = 'base_transit_stops'
    REGION_BASE_TRANSIT_STOPS = 'region_base_transit_stops'
    FUTURE_TRANSIT_STOPS = 'future_transit_stops'
    REGION_FUTURE_TRANSIT_STOPS = 'region_future_transit_stops'
    FISCAL = 'fiscal'
    VMT = 'vehicle_miles_traveled'
    VMT_FUTURE_TRIP_LENGTHS = 'vmt_future_trip_lengths'
    VMT_BASE_TRIP_LENGTHS = 'vmt_base_trip_lengths'
    REGION_VMT_FUTURE_TRIP_LENGTHS = 'region_vmt_future_trip_lengths'
    REGION_VMT_BASE_TRIP_LENGTHS = 'region_vmt_base_trip_lengths'

    VMT_VARIABLES = 'vmt_variables'

    PH_VARIABLES = 'ph_variables'
    PH_GRID_OUTCOMES = 'ph_grid_outcomes'
    PH_OUTCOMES_SUMMARY = 'ph_outcomes_summary'
    PH_BLOCK_GROUP_OUTCOMES = 'ph_block_group_outcomes'

    ENERGY = 'energy'
    WATER = 'water'
