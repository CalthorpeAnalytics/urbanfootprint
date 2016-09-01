
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

from footprint.main.initialization.policy.policy_importer import PolicyImporter

__author__ = 'calthorpe_analytics'

def initialize_policies(client='default'):

    policy_importer = PolicyImporter()
    policy_importer.load_residential_energy_baseline_csv(client)
    policy_importer.load_commercial_energy_baseline_csv(client)
    policy_importer.load_outdoor_water_baseline_csv(client)
