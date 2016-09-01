#
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
#
JSON_DIR=$UF/footprint/initialization/fixtures/client/default/built_form/json_fixtures

./manage.py dumpdata calthorpe.footprint.buildingusepercent --indent 2 > $JSON_DIR/building_uses_and_attributes.json
sed -i -e "1,3d" $JSON_DIR/building_uses_and_attributes.json

./manage.py dumpdata calthorpe.footprint.placetypecomponentpercent --indent 2 > $JSON_DIR/placetype_components.json
sed -i -e "1,3d" $JSON_DIR/placetype_components.json

./manage.py dumpdata calthorpe.footprint.infrastructuretype --indent 2 > $JSON_DIR/infrastructuretypes.json
sed -i -e "1,3d" $JSON_DIR/infrastructuretypes.json

./manage.py dumpdata calthorpe.footprint.buildingpercent --indent 2 > $JSON_DIR/building_percents.json
sed -i -e "1,3d" $JSON_DIR/building_percents.json

./manage.py dumpdata calthorpe.footprint.sacogplacetype --indent 2 > $JSON_DIR/sacog_placetype.json
sed -i -e "1,3d" $JSON_DIR/sacog_placetype.json
