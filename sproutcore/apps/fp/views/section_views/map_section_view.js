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

sc_require('views/presentation/map/map_layer_group');
sc_require('views/presentation/map/map_controls');
sc_require('views/presentation/map/map_painting');
sc_require('views/presentation/map/map_styling');
sc_require('views/presentation/map/map_tools');
sc_require('views/section_views/tool_section_view');
sc_require('controllers/map_controller');
sc_require('controllers/map_tools_controller');

/***
 * The map. Contains a Leaflet map and all of the associated controls
 */
Footprint.MapSectionView = SC.View.extend(SC.ActionSupport, SC.ContentDisplay, {

    classNames: 'footprint-map-section-view'.w(),
    childViews: ['mapView', 'mapOverlayView', 'mapToolsView', 'overlayView'],
    icon: sc_static('footprint:images/zoom_to_extent.png'),

    /***
     * The Footprint.ConfigEntity or other mappable instance according to which the map is configured
     * TODO why not call this scenario?
     */
    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),

    contentDisplayProperties: ['content'],

    /***
     * All Footprint.Layer instances of the Footprint.ConfigEntity
     */
    layers: null,
    layersBinding: SC.Binding.oneWay('Footprint.scenarioLayerLibraryApplicationController.layers'),

    init: function () {
        sc_super();

        // We set the mapTools here since they depend on the view for the map and to send actions to the view
        Footprint.mapToolsController.set('content', Footprint.MapTools.create({
            mapView: this,
            selectionFeatureGroup: new L.FeatureGroup()
        }));
    },

    /***
     * Creates the Leaflet map instance attached to the this.mapNode div element
    */
    createMap: function() {
        var map = L.map(this.get('mapNode'), {
            minZoom:Footprint.mapController.get('mapZoomRange')[0],
            maxZoom:Footprint.mapController.get('mapZoomRange')[1]
        });
        var latLngBounds = L.latLngBounds(Footprint.mapController.get('projectExtent'));
        map.fitBounds(latLngBounds);

        var compass_options = {position: 'bottomright'};
        var compass = new L.Control.Compass(compass_options);
        map.addControl(compass);
        L.control.scale().addTo(map);

        var drawColor = {shapeOptions: {
            color: '#383838',
            weight: 10
        }};
        var drawOptions = {
            draw: {
                polyline: false, // Turns off this drawing tool
                polygon: drawColor,
                circle: drawColor,
                rectangle: drawColor,
                marker: false // Turns off this drawing tool
            }
        };

        map.on('move', function() {
            Footprint.mapController.refreshMapLayerZoomVisibility();
        });

        map.on('click', function(e) {
            // need to remove popup visibility in case some other action is occurring
            // e.g. clicking to draw another selection polygon
            Footprint.featurePopupTableController.get('featureTablePopupPane').doClose();
        });


        // add draw controls
        var mapTools = Footprint.mapToolsController.get('content');
        polygon_options = {
            showArea: false,
            repeatMode: true,
            shapeOptions: {
                stroke: true,
                color: 'blue',
                weight: 2,
                opacity: 0.5,
                fill: true,
                fillColor: null, //same as color by default
                fillOpacity: 0.2,
                clickable: true
            }
        };

        var myIcon = L.divIcon({
            className: 'leaflet-div-icon-uf-sel',
            html: '+'
        });


        point_options = {
            repeatMode: true,
            icon: myIcon
        };

        mapTools.set('polygonDrawLayer', new L.Draw.Polygon(map, polygon_options));
        mapTools.set('rectangleDrawLayer', new L.Draw.Rectangle(map, polygon_options));
        mapTools.set('pointDrawLayer', new L.Draw.Marker(map, point_options));

        map.on('draw:created', mapTools.get('brushTool').didEndShape());

        // Center to the project bounds
        Footprint.mapController.set('content', map);
        Footprint.mapController.set('compass', compass);

        Footprint.featurePopupTableController.set('featureTablePopupPane', Footprint.FeatureTablePopupPane.create({isModal: NO}));
    },

    overlayView: Footprint.OverlayView.extend({
        contentBinding:SC.Binding.oneWay('Footprint.layersAndDependenciesController.content'),
        statusBinding:SC.Binding.oneWay('Footprint.layersAndDependenciesController.status')
    }),

    mapToolsView: Footprint.ToolSectionView.extend({
        classNames: ['footprint-tool-section-view', 'footprint-top-overlay-section'],
        layout: {top: 0, height: 25}
    }),

    mapView: SC.View.extend({
        classNames: 'footprint-map'.w(),
        layout: {left: 0, top: 25, right: 0, bottom: 0},

        project: null,
        projectBinding: SC.Binding.oneWay('*parentView.project'),

        readyToCreateMap: NO,
        // We can create the map when the mapController indicates and the project is bound--the latter is needed for extents.
        readyToCreateMapBinding: SC.Binding.and('Footprint.mapController.readyToCreateMap', 'Footprint.mapController.project'),
        /***
         * Create the map after this layer becomes ready
         */
        didCreateLayer: function () {
            SC.Timer.schedule({target: this, action: 'afterDelay', interval: 100});
        },
        afterDelay: function () {
            this.addObserver('readyToCreateMap', this, 'createMap');
            this.createMap();
        },
        createMap: function() {
            if (this.get('readyToCreateMap')) {
                this.removeObserver('readyToCreateMap', this, 'createMap');
                this.get('parentView').createMap();
            }
        }

    }),

    mapOverlayView: SC.View.extend({
        layout: {left: 0, top: 25, right: 0, bottom: 0},
        childViews: [
            SC.LabelView.extend({
                tagName: 'span', // for wrapping text
                layout: { centerY: 0, centerX: 0, width: .5, height: .5 },
                classNames: ['footprint-map-overlay'],
                value: 'Selection is too large to show on map',
            }),
        ],

        isVisibleBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController.features_count')
            .transform(function(features_count) {
                return features_count >= Footprint.MAX_MAP_VECTOR_FEATURES;
            }),
    }),

    /***
     * The div element containing the leaflet map.
     * @returns {*}
     */
    mapNode: function() {
        return this.$('.footprint-map')[0];
    }.property(),

    /***
     * The DOM element where the map is found (used for dblclick and other browser signals to the map)
     */
    mapWindow: function() {
        return this.get('map').focusableParent();
    }.property('map')

});
