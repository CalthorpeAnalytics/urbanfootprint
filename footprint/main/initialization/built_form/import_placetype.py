
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

from csvImporter.fields import CharField, FloatField
from csvImporter.model import CsvModel

class ImportedPlacetype(CsvModel):
    name = CharField(prepare=lambda x: x or '')
    clean_name = CharField(prepare=lambda x: x or '')
    color = CharField(prepare=lambda x: x or '')
    intersection_density = FloatField(prepare=lambda x: x or 0)

    class Meta:
        delimiter = ","
        has_header = True
