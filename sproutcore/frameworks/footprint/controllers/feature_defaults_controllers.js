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


/***
 * The following constant array represents the default available tools. Some may be disabled depending on the
 * type of Layer, loading state, etc
 * @type {string[]}
 */
Footprint.ToolSelectionStandardItems = [
    'zoomToProjectExtent', 'zoomToSelectionExtent',
    'navigate', 'pointbrush', 'rectanglebrush', 'polybrush',
    'doClearSelection', 'doManageBuiltForms','doExportMap', 'identify'
];

/***
 * Controls the use of map tools by enabling or disabling them depending on the application state
 * @type {*
*/
Footprint.toolController = SC.Object.create({
    /***
     * Controls if navigation tools are enabled
     */
    navigatorIsEnabled: YES,
    /***
     * Controls if selection tools are enabled
     */
    selectorIsEnabled: NO,

    /***
     * For now always enable deselect so that we can use the clear button at any time
     * in case a slow query is stuck
     */
    deselectorIsEnabled: YES ,

    /***
     * Controls if feature edit/info tools are enabled
     */
    featurerIsEnabled: NO,

    /***
     * Set true whenever the selector needs refresh, which clears the box or other shape it makes
     */
    selectionToolNeedsReset: NO,

    /***
     * If true shows the tool shape on the map after the user finishes drawing.
     * The tool shape can be adjusted and moved by the user
     */
    showToolShape: NO,

    activeLayerStatus: null,
    activeLayerStatusBinding: SC.Binding.oneWay('Footprint.layerActiveController*content.status'),

    /***
     * Binds to the active Layer for used by isItemEnabled
     */
    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    /**
     * Configuration of feature tables that are eligible for scenario or agriculture painting. isEnabledItems
     * takes the standard tool actions and adds doFeaturesUpdate. This means that the Footprint.EditSectionView
     * will allows painting of features as long as it is one of these feature tables and the statechart is in
     * a state that allows feature editing (i.e. on loading the LayerSelection). See edit_section_view.js for
     * more details.
     * @param item
     * @returns {*|boolean|*}
     */
    layerLookup: SC.Object.create({
        'scenario_end_state': {
            subtitle: 'Scenario Painting',
            isEnabledItems:  Footprint.ToolSelectionStandardItems.concat(['doFeaturesUpdate'])
        },
        'future_agriculture_canvas': {
            subtitle: 'Agriculture Painting',
            isEnabledItems:  Footprint.ToolSelectionStandardItems.concat(['doFeaturesUpdate'])
        },
        'base_agriculture_canvas': {
            subtitle: 'Agriculture Painting',
            isEnabledItems:  Footprint.ToolSelectionStandardItems.concat(['doFeaturesUpdate'])
        }
    }),

    activeLayerConfig: function () {
        if (this.get('activeLayerStatus') & SC.Record.READY)
            return this.getPath('layerLookup.%@'.fmt(this.getPath('activeLayer.dbEntityKey')));
    }.property('activeLayer', 'activeLayerStatus').cacheable(),

    /***
     * Return true if the given item is enabled based on the activeLayerConfig & Footprint.toolController
     * An item is something having a type and action, for example:
     * SC.Object.create({
        title: 'Apply',
        action:'doFeaturesUpdate',
        isEnabled: NO,
        type: 'featurer'
     * })
     * type must checks Footprint.toolController.[item]IsEnabled
     * action checks this.activeLayerConfig to see if the action matches the active layer
     * @param item
     * @returns {*|boolean}
     */
    isItemEnabled: function (item) {
        var layerConfig = this.get('activeLayerConfig');
        // Find the optional toolController boolean for this item type
        var controllerEnabled = Footprint.toolController.get('%@IsEnabled'.fmt(item.get('type')));
        // Return YES if the layerConfig (or default config) and tool enables the item
        return (layerConfig ? layerConfig.isEnabledItems : Footprint.ToolSelectionStandardItems).contains(item.action) &&
            (typeof(controllerEnabled) == 'undefined' || controllerEnabled);
    },
});

Footprint.endStateDefaultsController = SC.ObjectController.create({
    keys: ['built_form', 'dev_pct', 'density_pct', 'clear_flag', 'gross_net_pct', 'redevelopment_flag'],
    unmodifiedClientSideEmployment: null,
    unmodifiedClientSideDwellingUnits: null,
    userDefinedProperty: NO,
    previousDensityPct: 1,
    content: SC.Object.create({
        // Use this context to uniformly update features to the current user's choices, or the defaults below built_form
        update: SC.Object.create({
            built_form: null,
            built_formBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormActiveController.content'),
            dev_pct: 1,
            density_pct: 1,
            gross_net_pct: 1,
            clear_flag: NO,
            redevelopment_flag: NO,
            asObject: function() {
                return mapToObject(
                    Footprint.endStateDefaultsController.get('keys'),
                    function(key) { return [key, this.get(key)]},
                    this
                )
            }.property()
        }),
    })
});

Footprint.agricultureFeatureDefaultsController = SC.ObjectController.create({
    keys: ['built_form', 'dev_pct', 'density_pct', 'clear_flag', 'gross_net_pct'],
    userDefinedProperty: NO,
    previousDensityPct: 1,
    content: SC.Object.create({
        update: SC.Object.create({
            built_form: null,
            built_formBinding: SC.Binding.oneWay('Footprint.agricultureBuiltFormActiveController.content'),
            dev_pct: 1,
            density_pct: 1,
            gross_net_pct: 1,
            clear_flag: NO,
            // SC provides no way to extract keys so provide this function to get a plain old JS object
            asObject: function() {
                return mapToObject(
                    Footprint.agricultureFeatureDefaultsController.get('keys'),
                    function(key) { return [key, this.get(key)]},
                    this
                )
            }.property()
        }),
    })
});
