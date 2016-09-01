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



Footprint.ToolSectionView = SC.View.extend({
    classNames: 'footprint-tool-section-view'.w(),
    childViews: ['searchView', 'selectStatusView', 'paintAndSelectButtonView'],
    /***
     * The delegate for the active configEntity, used to override settings
     */
    configEntityDelegate: null,
    /***
     * Bind this to the active layer in the layer library.
     * The active layer determines what tools are available
     */

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),
    activeLayerStatus: null,
    activeLayerStatusBinding: SC.Binding.oneWay('Footprint.layerActiveController*content.status'),

    selectStatusView: Footprint.LoadingSpinnerView.extend({
        layout: {left: 0, width:32, top:1, height: 26},
        featuresStatus:null,
        featuresStatusBinding: SC.Binding.oneWay('Footprint.featuresActiveController.status'),
        layerSelectionStatus: null,
        layerSelectionStatusBinding: SC.Binding.oneWay('Footprint.layerSelectionEditController.status'),
        // Don't appear when the statuses are empty, e.g. for background layers
        showOnBusyOnly: YES,
        /***
         * Only show the spinner if features or layer selection are loading. If there are no features
         * or layer selection it won't show
         */
        status: function() {
            return Math.max(this.get('featuresStatus') || 0, this.get('layerSelectionStatus') || 0);
        }.property('featuresStatus', 'layerSelectionStatus').cacheable()
    }),

    searchView: SC.TextFieldView.extend({
        classNames: 'footprint-map-search-view'.w(),
        layout: {left:32, width:200, top: 1, height:24},

        didCreateLayer: function() {

            // Create the search box and link it to the UI element.
            var $input = this.$input(),
                input = $input[0];

            $input.attr('placeholder', 'Search Map');

            try {
                var searchBox = new google.maps.places.SearchBox(input);
                // Listen for the event fired when the user selects an item from the
                // pick list. Retrieve the matching places for that item.
                google.maps.event.addListener(searchBox, 'places_changed', function() {
                    var places = searchBox.getPlaces();

                    var place = places[0];
                    if (place) {
                        var map = Footprint.mapController.get('content');
                        if (map)
                            // map.center({lat:place.geometry.location.lat(), lon:place.geometry.location.lng()});
                            map.panTo(new L.LatLng(place.geometry.location.lat(), place.geometry.location.lng()));
                    }
                });
            }
            catch(e) {
                logWarning('Google Search Box failed to load');
            }
        }
    }),

    paintAndSelectButtonView: Footprint.ToolSegmentedButtonView.extend({
        layout: {height: 26, left:234, width: 450, top: 1},
        // The standard items for layers that don't have specific items specified in the layerLookup
        standardItems:Footprint.ToolSelectionStandardItems,
        itemValueKey: 'action',
        // The selectable tools
        rawItems: null,
        rawItemsBinding: SC.Binding.oneWay('Footprint.mapToolsController.toolConfigs'),

        activeLayerBinding: SC.Binding.oneWay('.parentView.activeLayer'),
        activeLayerStatusBinding: SC.Binding.oneWay('.parentView.activeLayerStatus'),
        activeTopView: null,
        activeTopViewBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.content'),
        globalLayerConfig: function() {
            if (this.getPath('activeTopView') == 'approval')
                return ['zoomToProjectExtent', 'navigate'];
        }.property('activeTopView').cacheable(),

        /**
         * Returns YES if the given item is configured for the active layer and the toolsController says its type is isEnabled
         * @param item
         * @returns {*|boolean|*}
         */
        isItemEnabled: function (item) {
            var layerConfig = this.get('globalLayerConfig') ?
                this.get('globalLayerConfig') :
                this.get('activeLayerConfig');
            // Find the optional toolController boolean for this item type
            var controllerEnabled = Footprint.toolController.get('%@IsEnabled'.fmt(item.get('type')));
            // Check if the items are limited by the layerConfig or the standardItems
            var limitedItems = layerConfig ?
                layerConfig :
                this.get('standardItems');
            // Return YES if the layerConfig (or default config) and tool enables the item
            return (!limitedItems || limitedItems.contains(item.action)) &&
                (typeof(controllerEnabled) == 'undefined' || controllerEnabled);
        },

        // Trigger a changes to items whenever a relevant toolController boolean changes
        toolControllerObserver: function () {
            this.propertyDidChange('items');
        }.observes(
            'Footprint.toolController.navigatorIsEnabled',
            'Footprint.toolController.selectorIsEnabled',
            'Footprint.toolController.featurerIsEnabled',
            'Footprint.toolController.deselectorIsEnabled'
        ),
        value: 'navigate',
        /***
         * When the items change we check to see if the selected item has become disabled. If so, we
         * switch value back to the default, 'navigate'
         */
        itemsObserver: function() {
            var selectedItem = this.get('items').find(function(item) {
                return item.get(this.get('itemValueKey'))==this.get('value');
            }, this);
            // We should always have a selectedItem, but it's sometimes null for some reason
            if (selectedItem && !selectedItem.get(this.get('itemIsEnabledKey')))
                this.set('value', 'navigate');
        }.observes('items')
    })
});
