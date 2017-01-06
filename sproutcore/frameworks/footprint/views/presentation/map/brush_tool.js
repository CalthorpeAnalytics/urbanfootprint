/*
 * UrbanFootprint v1.5
 * Copyright (C) 2017 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */


/***
 * Represents a tool used for painting/selection
 * @type {*}
 */
Footprint.PaintTool = SC.Object.extend({

    mapView: null,
    brush:null,
    /***
     * The selector string to access the svg element holding the tool's path data()
     */
    selector:null,

    selectionFeatureGroup:null,
    drawnPolygonCoordinates:null,
    geometry:null
});

/***
 * Extends PaintTool to add actions based on the d3.svg.brush interface
 * @type {*}
 */
Footprint.BrushTool = Footprint.PaintTool.extend({
    /***
     * Overload init to set up the brush events
     * Brush start clears the activeLayerSelection
     */
    init:function() {
        sc_super();
        Footprint.statechart.sendAction('doCancelLayerSelectionUpdate');
        L.drawLocal.draw.handlers.rectangle.tooltip.start = 'Click and drag to draw selection rectangle';
        L.drawLocal.draw.handlers.polygon.tooltip.start = 'Click to start drawing selection polygon';
        L.drawLocal.draw.handlers.marker.tooltip.start = 'Click a polygon to select it';
        L.drawLocal.draw.handlers.marker.tooltip.info = 'Click a selected feature identify it';
    },


    getLastDrawnPolygonCoordinates: function(event) {
        var newLayer = event.layer;
        var newGeoJsonObj = newLayer.toGeoJSON();
        var coordsShape = newGeoJsonObj.geometry.coordinates;

        return (coordsShape.length == 2) ? this.pointToTinySquare(coordsShape[0],coordsShape[1]) : coordsShape;
    },

    getAddToSelectionKeyPressed: function() {
        var eventCtrlPressed = L.DomEvent._getEvent().ctrlKey ? true : false;
        var eventMetaPressed = L.DomEvent._getEvent().metaKey ? true : false;
        var platformOS = String(navigator.platform);
        var addToSelKeyPressed;
        if (platformOS.substring(0, 3) == 'Mac') {
            addToSelKeyPressed = eventMetaPressed;
        } else {
            addToSelKeyPressed = eventCtrlPressed;
        }

        return addToSelKeyPressed;
    },


    didEndShape: function() {
        var self = this;
        //console.log("in BrushTool.didEndShape, L.DomEvent._getEvent().ctrlKey = " + String(L.DomEvent._getEvent().ctrlKey));

        return function(event) {
            // self.set('geometry', self.getEventBounds(event));
            self.set('addToSelectionKeyPressed', self.getAddToSelectionKeyPressed());
            self.set('drawnPolygonCoordinates', self.getLastDrawnPolygonCoordinates(event));
            // TODO this could also be additive or a continuation of the previous polygon
            SC.run(function () {
                Footprint.statechart.sendAction('doEndShape', event);
            });
        };
    },
    selectionFeatureGroup:null,
    drawnPolygonCoordinates:null,
    addToSelectionKeyPressed:null,
    geometry: null,

    /***
     * takes in lat/lon and returns a very small square polygon based on arbitrary offset
     */
    pointToTinySquare: function(lat,lon) {
        var offset = 0.0000005, tinySquareCoords = [], coodsArray = [];
        coodsArray.push([lat-offset,lon-offset]);   //,[lat+offset,lon-offset],[lat-offset,lon+offset],[lat+offset,lon+offset],[lat-offset,lon-offset]);
        coodsArray.push([lat+offset,lon-offset]);
        coodsArray.push([lat+offset,lon+offset]);
        coodsArray.push([lat-offset,lon+offset]);
        coodsArray.push([lat-offset,lon-offset]);
        tinySquareCoords.push(coodsArray);
        return tinySquareCoords;
    },

    getEventBounds: function(event) {
        //console.log('in BrushTool.getEventBounds');
        var newLayer = event.layer;
        var eventType = L.DomEvent._getEvent().ctrlKey ? 'add' : 'replace';

        var coordsMultiPolygon=[],featgrpGeoJsonObj,coordsShape,coordsPolygon;

        // http://stackoverflow.com/questions/24018630/how-to-save-a-completed-polygon-points-leaflet-draw-to-mysql-table

        if (eventType == 'add'){
            this.selectionFeatureGroup.addLayer(newLayer);
            // layer is already in the featuregroup so just iterate through it
            this.selectionFeatureGroup.eachLayer(function (layer) {
                featgrpGeoJsonObj = layer.toGeoJSON();
                coordsShape = featgrpGeoJsonObj.geometry.coordinates;

                if (coordsShape.length == 2) {
                    coordsPolygon = [];
                    var offset = 0.0000005, coodsArray = [];
                    var lat = coordsShape[0], lon = coordsShape[1];
                    coodsArray.push([lat-offset,lon-offset]);   //,[lat+offset,lon-offset],[lat-offset,lon+offset],[lat+offset,lon+offset],[lat-offset,lon-offset]);
                    coodsArray.push([lat+offset,lon-offset]);
                    coodsArray.push([lat+offset,lon+offset]);
                    coodsArray.push([lat-offset,lon+offset]);
                    coodsArray.push([lat-offset,lon-offset]);
                    coordsPolygon.push(coodsArray);
                } else {
                    coordsPolygon = coordsShape;
                }
                coordsMultiPolygon.push(coordsPolygon);
                //var geom_gjstr = JSON.stringify(shape_geom);
                //output_text =  output_text + "<br>&nbsp;<br>" + geom_gjstr;
            });
        } else if (eventType == 'replace') {

            // blow all feature group layers away and add the newest layer from event
            this.selectionFeatureGroup.clearLayers();
            this.selectionFeatureGroup.addLayer(newLayer);
            var newGeoJsonObj = newLayer.toGeoJSON();
            coordsShape = newGeoJsonObj.geometry.coordinates;
            coordsPolygon = (coordsShape.length == 2) ? this.pointToTinySquare(coordsShape[0],coordsShape[1]) : coordsShape;
            coordsMultiPolygon.push(coordsPolygon);

            /*
            // iterate through featuregroup and clear all but only the newest
            this.selectionFeatureGroup.eachLayer(function (layer) {
            if (layer == newLayer) {
            // return this as the new multipoly
            featgrpGeoJsonObj = layer.toGeoJSON();
            coordsShape = featgrpGeoJsonObj.geometry.coordinates;
            coordsPolygon = (coordsShape.length == 2) ? this.pointToTinySquare(coordsShape[0],coordsShape[1]) : coordsShape;
            coordsMultiPolygon.push(coordsPolygon);

            } else {
            //this.selectionFeatureGroup.clearLayers();
            this.selectionFeatureGroup.removeLayer(layer);
            //this.selectionFeatureGroup.addLayer(layer);
            }

            });
            */

        }

        return {
            type: 'MultiPolygon',
            coordinates: coordsMultiPolygon
        };

    },

    isValidGeometry: function() {
        var geometry = this.geometry();
        return geometry && geometry.length >= 3;
    }
});
