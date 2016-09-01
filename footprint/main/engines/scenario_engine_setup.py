
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

from django.db.models.signals import post_syncdb, post_save, pre_delete
from django.dispatch import receiver
from south.signals import post_migrate
from django.conf import settings

from footprint.main.policy.setup_scenario_policy import get_dev_acres
import models
from footprint.main.lib.functions import merge
from footprint import main
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.keys.keys import Keys
from footprint.uf_tools import db_table_exists


__author__ = 'calthorpe_analytics'

@receiver(post_syncdb, sender=models)
@receiver(post_migrate, sender=models)
def on_post_syncdb(sender, **kwargs):
    pass

def on_scenario_post_save(sender, **kwargs):
    check_basic_increments(kwargs['instance'])

def on_scenario_pre_delete(sender, **kwargs):
    pass

def check_basic_increments(scenario):
    from footprint.main.sql_unformatted import rawSQL
    if not db_table_exists("basic_increments_{0}".format(scenario.id)):
        from footprint.uf_tools import executeSQL_now
        executeSQL_now(scenario.projects.inputs_outputs_db, [rawSQL.make_increment_headers.format(scenario.working_schema, scenario.id)])

# Register Django Signals to respond to synd_db and Scenario persistence
post_syncdb.connect(on_post_syncdb, sender=main.models)
post_save.connect(on_scenario_post_save, sender=Scenario)
pre_delete.connect(on_scenario_pre_delete, sender=Scenario)

# TODO not sure what this was for
def get_project_options(project):
    return {'base_year_grid'    : project.resolve_db_entity(DbEntityKey.BASE),
            'base_year'         : project.base_year,
            'vmt_geography_type': 'taz',
            'vmt_geographies'   : project.resolve_db_entity(Keys.DB_ENTITY_VMT_GEOGRAPHIES),
            'vmt_trip_table'    : project.resolve_db_entity(Keys.DB_ENTITY_VMT_TRIPS),
            'ref_table_schema'  : project.schema(),
            'srid'              : project.srid,
            'study_area'        : project.name,
            'key'               : project.key,
            'working_schema'    : project.schema()
    }

def get_engine_options(scenario):

    db = scenario.db

    conn_string = 'dbname=' + db['NAME'] + ' host=' + db['HOST'] + ' user=' + db['USER'] + ' password=' + db['PASSWORD']

    scenario_settings = {
        # scenario profile
        'use_hhsize_factor'         : False,
        'pop_control'               : None,
        'base_year_grid'            : scenario.resolve_db_entity(DbEntityKey.BASE),
        'developable_acres_grid'    : scenario.resolve_db_entity(Keys.DB_ABSTRACT_DEVELOPABLE),
        'horiz_developable_grid'    : scenario.resolve_db_entity(Keys.DB_ABSTRACT_HORIZON_DEVELOPABLE),
        'horiz_year_pt_grid'        : scenario.resolve_db_entity(DbEntityKey.FUTURE_SCENARIO),
        'canvas_schema'             : settings.CANVAS_SCHEMA,
        'loaded_parcels'            : scenario.resolve_db_entity(Keys.DB_ABSTRACT_LOADED_PARCELS),
        'parcel_portions'           : scenario.resolve_db_entity(Keys.DB_ENTITY_PARCEL_PORTIONS),
        'working_schema'            : scenario.schema(),
        'core_output'               : scenario.resolve_db_entity(Keys.DB_CORE_OUTPUT),
        'scenario_name'             : scenario.name,
        'scenario_year'             : scenario.year,
        'scenario_region'           : scenario.project.key,
        'placetypes'                : scenario.resolve_db_entity(Keys.DB_PLACETYPES),
        'unique_name'               : scenario.key(),
        'scenario_id'               : str(scenario.id),
        'ref_table_schema'          : scenario.schema(),
        'census_block_table'        : scenario.resolve_db_entity(Keys.DB_ENTITY_CENSUS_BLOCKS),
        'census_blkgrp_table'       : scenario.resolve_db_entity(Keys.DB_ENTITY_CENSUS_BLOCK_GROUPS)
        }

    all_options = scenario_settings

    d = get_dev_acres(scenario)
    devacres_settings = {
        # developable acres configuration
        'Urban_Res_DetSF_SL'        : d.urban_residential_detached_single_family_small_lot,
        'Urban_Res_DetSF_LL'        : d.urban_residential_detached_single_family_large_lot,
        'Urban_Res_Mf'              : d.urban_residential_multi_family,
        'Urban_Emp_Off'             : d.urban_employment_office,
        'Urban_Emp_Ret'             : d.urban_employment_retail,
        'Urban_Emp_Ind'             : d.urban_employment_industrial,
        'Urban_Emp_Ag'              : d.urban_employment_agriculture,
        'Urban_Emp_Mixed'           : d.urban_employment_mixed,
        'Urban_Mixed_w_Off'         : d.urban_mixed_use_with_office,
        'Urban_Mixed_no_Off'        : d.urban_mixed_use_without_office,
        'Urban_No_Use'              : d.urban_no_use,
        'gf'                        : d.greenfield,
        # new fields added in v2
        'Urban_Emp_Ret_Off'         : d.greenfield,
        'Urban_Emp_Ind_Ret'         : d.greenfield,
        'Urban_Emp_Ind_Off'         : d.greenfield,
        'Urban_Mixed_Ag'            : d.greenfield,
        }
    all_options = merge(all_options, devacres_settings)

    try:
        from footprint.main.models.energy_water import EnergyWater
        e = scenario.get_energy_water()
        #            e = EnergyWater.objectself.get(scenario=self)
        YearsBasetoHoriz = scenario.year - 2010
        energywater_settings = {
            #POLICY SETTINGS--------------------------------------------------------------------
            #Residential Energy (Electricity & Gas)-----Enter as PERCENTS!!!--------------------
            'ResEnrgyNewConst'          : e.ResEnrgyNewConst,    #New construction - Percentage reduction from baseline rates by a horizon year.
            'ResEnrgyRetro'             : e.ResEnrgyRetro,   #Retrofits - Year-upon-year percentage reduction.
            'ResEnrgyReplcmt'           : e.ResEnrgyReplcmt,    #Replacement - Reset of some percentage of existing units to new standards.
            #Commercial Energy (Electricity & Gas) ---------------------------------------------
            'ComEnrgyNewConst'          : e.ComEnrgyNewConst,     #New construction - Percentage reduction from baseline rates by a horizon year.
            'ComEnrgyRetro'	            : e.ComEnrgyRetro,    #Retrofits - Year-upon-year - percentage reduction.
            'ComEnrgyReplcmt'           : e.ComEnrgyReplcmt,     #Replacement - Reset of some percentage of existing units to new standards.
            #Residential Water (Indoor & Outdoor) ----------------------------------------------
            'ResWatrNewConst'           : e.ResWatrNewConst,  #New construction
            'ResWatrRetro'	            : e.ResWatrRetro,    #Retrofits
            'ResWatrReplcmt'            : e.ResEnrgyReplcmt,    #Replacement
            #Commercial & Industrial Water (Indoor & Outdoor) ----------------------------------
            'ComIndWatrNewConst'        : e.ComIndWatrNewConst,    #New construction
            'ComIndWatrRetro'           : e.ComIndWatrRetro,  #Retrofits
            'ComIndWatrReplcmt'         : e.ComIndWatrReplcmt,   #Replacement
            #Additional Parameters -------------------------------------------------------------
            'YearsBasetoHoriz'          : YearsBasetoHoriz,
            'Water_GPCD_SF'             : e.Water_GPCD_SF,           #Indoor per-capita single family gallons per day
            'Water_GPCD_MF'             : e.Water_GPCD_MF,            #Indoor per-capita multifamily gallons per day:
            'Water_GPED_Retail'         : e.Water_GPED_Retail,       #Indoor per-employee gallons per day, Retail
            'Water_GPED_Office'         : e.Water_GPED_Office,       #Indoor per-employee gallons per day, Office
            'Water_GPED_Industrial'     : e.Water_GPED_Industrial,   #Indoor per-employee gallons per day, Industrial
            'Water_GPED_School'         : e.Water_GPED_School,        #Indoor per-employee gallons per day, School
            #Industrial energy intensity: Annual Energy use per Employee
            'ann_ind_elec_peremp'       : e.ann_ind_elec_peremp,         #kwh
            'ann_ind_gas_peremp'        : e.ann_ind_gas_peremp,             #thm
        }
        all_options = merge(all_options, energywater_settings)
    except Exception, E:
        pass

    conn_string = {'conn_string' : conn_string,}

    all_options = merge(all_options, conn_string)

    return all_options
