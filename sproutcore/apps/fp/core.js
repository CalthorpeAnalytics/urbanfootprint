/*
 * UrbanFootprint v1.5
 * Copyright (C) 2016 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */

sc_require('resources/leaflet/leaflet-src.js');
sc_require('resources/leaflet/compass/dist/leaflet.compass.js');
sc_require('resources/leaflet/draw/src/Leaflet.draw.js');
sc_require('resources/leaflet/draw/src/Toolbar.js');
sc_require('resources/leaflet/draw/src/Tooltip.js');
sc_require('resources/leaflet/draw/src/ext/GeometryUtil.js');
sc_require('resources/leaflet/draw/src/ext/LatLngUtil.js');
sc_require('resources/leaflet/draw/src/ext/LineUtil.Intersect.js');
sc_require('resources/leaflet/draw/src/ext/Polygon.Intersect.js');
sc_require('resources/leaflet/draw/src/ext/Polyline.Intersect.js');
sc_require('resources/leaflet/draw/src/draw/DrawToolbar.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Feature.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.SimpleShape.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Polyline.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Circle.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Marker.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Polygon.js');
sc_require('resources/leaflet/draw/src/draw/handler/Draw.Rectangle.js');
sc_require('resources/leaflet/draw/src/edit/EditToolbar.js');
sc_require('resources/leaflet/draw/src/edit/handler/EditToolbar.Edit.js');
sc_require('resources/leaflet/draw/src/edit/handler/EditToolbar.Delete.js');
sc_require('resources/leaflet/draw/src/Control.Draw.js');
sc_require('resources/leaflet/draw/src/edit/handler/Edit.Poly.js');
sc_require('resources/leaflet/draw/src/edit/handler/Edit.SimpleShape.js');
sc_require('resources/leaflet/draw/src/edit/handler/Edit.Circle.js');
sc_require('resources/leaflet/draw/src/edit/handler/Edit.Rectangle.js');
sc_require('resources/leaflet/draw/src/edit/handler/Edit.Marker.js');
// Leaflet doesn't set its imagePath correctly in compiled sproutcore mode. So set it manually here
// (using compass.png just as a dependable file since sc_static wants a file name)
L.Icon.Default.imagePath = sc_static('leaflet/images/compass.png');
L.Icon.Default.imagePath = L.Icon.Default.imagePath.slice(0, L.Icon.Default.imagePath.lastIndexOf('/compass.png'));
sc_require('resources/leaflet/TileLayer.GeoJSON_uf.js');
//sc_require('resources/leaflet/TileLayer.GeoJSON_extensions.js');

//sc_require('resources/leaflet/Google.js');
//sc_require('resources/leaflet/l.control.geosearch.js');
sc_require('resources/leaflet/easy-button.js');

// For map_controller's exportMapToImage button function
sc_require('resources/leaflet/leaflet-image/leaflet-image.js');
sc_require('resources/leaflet/leaflet-image/queue.js');

sc_require('footprint/controllers/developer_mode_controller');

//SC.LOG_OBSERVERS = YES;

Footprint.STATIC = sc_static('images/loading.png').replace('images/loading.png','%@');

SC.NestedStore.reopen({ lockOnRead: NO });
