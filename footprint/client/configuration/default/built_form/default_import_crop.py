
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

from csvImporter.fields import CharField, FloatField, IntegerField
from csvImporter.model import CsvModel


class ImportCrop(CsvModel):
    id = IntegerField(prepare=lambda x: x or 0)
    name = CharField(prepare=lambda x: x or '')

    crop_yield = FloatField(prepare=lambda x: x or 0)
    unit_price = FloatField(prepare=lambda x: x or 0)
    cost = FloatField(prepare=lambda x: x or 0)
    water_consumption = FloatField(prepare=lambda x: x or 0)
    labor_input = FloatField(prepare=lambda x: x or 0)
    truck_trips = FloatField(prepare=lambda x: x or 0)

    seed_cost = FloatField(prepare=lambda x: x or 0)
    chemical_cost = FloatField(prepare=lambda x: x or 0)
    fertilizer_cost = FloatField(prepare=lambda x: x or 0)
    custom_cost = FloatField(prepare=lambda x: x or 0)
    contract_cost = FloatField(prepare=lambda x: x or 0)
    irrigation_cost = FloatField(prepare=lambda x: x or 0)
    labor_cost = FloatField(prepare=lambda x: x or 0)
    equipment_cost = FloatField(prepare=lambda x: x or 0)
    fuel_cost = FloatField(prepare=lambda x: x or 0)
    other_cost = FloatField(prepare=lambda x: x or 0)
    feed_cost = FloatField(prepare=lambda x: x or 0)
    pasture_cost = FloatField(prepare=lambda x: x or 0)
    land_rent_cost = FloatField(prepare=lambda x: x or 0)
    other_cash_costs = FloatField(prepare=lambda x: x or 0)
    # We don't store this. We calculate it from everything above on the front-end
    total_cash_costs = FloatField(prepare=lambda x: x or 0)
    establishment_cost = FloatField(prepare=lambda x: x or 0)
    land_cost = FloatField(prepare=lambda x: x or 0)
    other_noncash_costs = FloatField(prepare=lambda x: x or 0)
    # We don't store this. We calculate it from everything above on the front-end
    total_noncash_costs = FloatField(prepare=lambda x: x or 0)

    class Meta:
        delimiter = ","
        has_header = True

class ImportCropType(CsvModel):
    id = IntegerField(prepare=lambda x: x or 0)
    name = CharField(prepare=lambda x: x or '')
    alfalfa = FloatField(prepare=lambda x: x or 0)
    almonds = FloatField(prepare=lambda x: x or 0)
    apples = FloatField(prepare=lambda x: x or 0)
    apricots = FloatField(prepare=lambda x: x or 0)
    asparagus = FloatField(prepare=lambda x: x or 0)
    beans = FloatField(prepare=lambda x: x or 0)
    blueberries = FloatField(prepare=lambda x: x or 0)
    corn = FloatField(prepare=lambda x: x or 0)
    grapes = FloatField(prepare=lambda x: x or 0)
    mandarins = FloatField(prepare=lambda x: x or 0)
    nursery = FloatField(prepare=lambda x: x or 0)
    olives = FloatField(prepare=lambda x: x or 0)
    other_citrus = FloatField(prepare=lambda x: x or 0)
    other_fruits_and_nuts = FloatField(prepare=lambda x: x or 0)
    other_stone_fruits = FloatField(prepare=lambda x: x or 0)
    pasture = FloatField(prepare=lambda x: x or 0)
    peaches = FloatField(prepare=lambda x: x or 0)
    pears = FloatField(prepare=lambda x: x or 0)
    prunes = FloatField(prepare=lambda x: x or 0)
    rice = FloatField(prepare=lambda x: x or 0)
    safflower = FloatField(prepare=lambda x: x or 0)
    strawberry = FloatField(prepare=lambda x: x or 0)
    sunflower = FloatField(prepare=lambda x: x or 0)
    timber = FloatField(prepare=lambda x: x or 0)
    tomatoes = FloatField(prepare=lambda x: x or 0)
    vegetables = FloatField(prepare=lambda x: x or 0)
    walnuts = FloatField(prepare=lambda x: x or 0)
    wheat = FloatField(prepare=lambda x: x or 0)
