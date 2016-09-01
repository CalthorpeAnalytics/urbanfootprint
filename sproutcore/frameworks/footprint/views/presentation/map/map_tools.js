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


Footprint.MapTools = SC.Object.extend({

    /***
     * A reference to the mapView that these tools interact with
     */
    mapView: null,
    polygonDrawLayer: null,
    rectangleDrawLayer: null,
    pointDrawLayer: null,

    selectionFeatureGroup: null,
    drawControl: null,
    brushTool: null,
    polygonBrush: null,

    init: function () {
        this.set('brushTool', Footprint.BrushTool.create({
            mapView: this.get('mapView'),
            selectionFeatureGroup: this.get('selectionFeatureGroup'),
            mapTools: this
        }));
    },

    //    /***
    //     * Point brush
    //     */
    //    pointbrush:null,
    //    /***
    //     * A d3 polygon selection bush
    //     */
    circlebrush:function() {
        return this.get('brushTool');
    }.property().cacheable(),
    pointbrush:function() {
        return this.get('brushTool');
    }.property().cacheable(),
    polybrush:function() {
        return this.get('brushTool');
    }.property().cacheable(),
    rectanglebrush:function() {
        return this.get('brushTool');
    }.property().cacheable()
});
