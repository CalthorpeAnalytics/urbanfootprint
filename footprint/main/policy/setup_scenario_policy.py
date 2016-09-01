
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
import models
from footprint import main
from footprint.main.models.config.scenario import Scenario
from footprint.main.models.config.scenario import Scenario
from uf_tools import db_table_exists, executeSQL_now

__author__ = 'calthorpe_analytics'

@receiver(post_syncdb, sender=models)
@receiver(post_migrate, sender=models)
def on_post_syncdb(sender, **kwargs):
    pass

def on_scenario_post_save(sender, **kwargs):
    get_energy_water(kwargs['instance'])
    get_dev_acres(kwargs['instance'])
    setup_transit_policy(kwargs['instance'])

def on_scenario_pre_delete(sender, **kwargs):
    pass

def get_energy_water(scenario):
    from footprint.main.models.energy_water import EnergyWater
    try:
        e = EnergyWater.objects.get(scenario=scenario)
    except:
        e = EnergyWater.objects.create(scenario=scenario)
        e.save()
    return e

def get_dev_acres(scenario):
    from footprint.main.models.dev_acres import DevAcres
    try:
        d = DevAcres.objects.get(scenario=scenario)
    except:
        d = DevAcres.objects.create(scenario=scenario)
        d.save()
    return d


def setup_transit_policy(scenario):
    if scenario.year <= 2020:
        transit_year = 2020
    elif scenario.year <= 2035:
        transit_year = 2035
    else:
        transit_year = 2050
    transit_policy = {}
    transit_policy['transit_flavor'] = scenario.transit_scenario.lower() + "_" + str(transit_year)
    transit_policy['transit_areas'] = "transit_{0}_{1}_{2}".format(scenario.study_area.key.lower().replace(' ', ''),
        scenario.transit_scenario.lower(), str(transit_year))
    transit_policy['transit_table'] = scenario.working_schema + "." + scenario.transit_areas
    if not db_table_exists(scenario.transit_areas):
        print "running transit area sql..."
        hsr_radius = str(1609.344 * 2)
        standard_radius = str(1609.344)
        sql = rawSQL.select_and_buffer_study_area_stops.format(scenario.working_schema, scenario.transit_table,
            scenario.study_area.base_year_grid, str(scenario.year), scenario.transit_areas, str(hsr_radius), str(standard_radius),
            scenario.transit_flavor)
        executeSQL_now(scenario.study_area.inputs_outputs_db, [sql])
    return transit_policy

# Register Django Signals to respond to synd_db and Scenario persistence
post_syncdb.connect(on_post_syncdb, sender=main.models)
post_save.connect(on_scenario_post_save, sender=Scenario)
pre_delete.connect(on_scenario_pre_delete, sender=Scenario)
