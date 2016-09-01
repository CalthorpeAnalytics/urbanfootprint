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

Footprint.ToolSegmentedButtonView = SC.SegmentedView.extend({
    classNames: ['footprint-tool-segmented-button-view', '.ace.sc-regular-size.sc-segment-view'],
    selectSegmentWhenTriggeringAction: YES,
    itemActionKey: 'action',
    itemIconKey: 'icon',
    itemTitleKey: 'title',
    itemKeyEquivalentKey: 'keyEquivalent',
    itemValueKey: 'value',
    itemIsEnabledKey: 'isEnabled',
    itemToolTipKey: 'toolTip',
    itemWidthKey: 'width',

    // The unfiltered items. Same format as the items, but these are filtered down
    // for the final item list
    rawItems: null,
    activeLayer: null,
    activeLayerStatus: null,
    activeScenario: null,
    activeScenarioStatus: null,
    // The Behavior or the activeLayer
    activeBehavior: null,
    activeBehaviorBinding: SC.Binding.oneWay('*activeLayer.db_entity.feature_behavior.behavior'),
    activeBehaviorStatus: null,
    activeBehaviorStatusBinding: SC.Binding.oneWay('*activeBehavior.status'),

    isEnabledBinding: SC.Binding.oneWay('.activeLayerStatus').matchesStatus(SC.Record.READY),
    /***
     * Optional dictionary to lookup the activeLayerConfig for the activeLayer.
     * The dictionary must be keyed by DbEntity key and can return whatever you want to use
     * in isItemEnabled to determine if the item should be enabled based on the activeLayer
     */
    layerLookup: null,
    globalLayerConfig: null,
    activeLayerConfig: function () {
        if (this.get('activeLayerStatus') & SC.Record.READY)
            return this.getPath('layerLookup.%@'.fmt(this.getPath('activeLayer.dbEntityKey')));
    }.property('activeLayer', 'activeLayerStatus').cacheable(),
    // A list of items that are by default enabled for a layer that doesn't defined its enabled items in the layerLookup
    standardItems: null,

    /**
     * Override to return YES or NO based on whether or not the given item is currently enabled.
     * This will be called on all each items whenever the 'items' property is refreshed
     * @param item
     * @returns {*|boolean|*}
     */
    isItemEnabled: function(item) {
        return YES
    },

    /**
     * The items that may or may not be isEnabled, based on the current activeLayer
     * This fires whenever the active layer or its status changes, and depends on the configuration of the layer
     * type ('selector', 'featurer', etc) and on any specific configuration for that layer.
     */
    items: function () {
        return (this.get('rawItems') || []).map(function (item) {
            return SC.Object.create($.extend({},
                item,
                // merge a dict that enables it if it's configured for the active layer, otherwise disables
                {isEnabled: this.isItemEnabled(item)}));
        }, this);
    }.property('activeLayer', 'activeLayerStatus', 'activeBehavior', 'activeBehaviorStatus', 'rawItems').cacheable(),

    // Don't allow stateless buttons to remain selected
    valueObserver: function () {
        var value = this.get('value');
        var itemValueKey = this.get('itemValueKey');
        if (value) {
            var item = this.get('items').filter(function (item) {
                return item.get(itemValueKey) == value;
            }, this)[0];
            if (item.get('isStatelessButton'))
                // Set it back. This will refire the observer once
                this.set('value', this._statefulValue);
            else
                // Update it
                this._statefulValue = value;
        }
    }.observes('.value'),

    _statefulValue: null

});
