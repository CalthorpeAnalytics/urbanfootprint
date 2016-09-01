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

sc_require('views/item_views/edit_item_view');
sc_require('views/progress_overlay_view');
sc_require('views/item_views/layer_visibility_view');

/**
 *
 * Displays a DbEntity as an item of a list by binding a Footprint.DbEntity to the content.
 * We use Child views to render the item, as opposed to subclassing Footprint.ListItemView and using
 * the render method. If this view needs a third level of tree-items, we probably have to switch
 * to Footprint.ListItemView to get disclosures to work at the second level
 */
Footprint.DbEntityEditItemView = Footprint.EditItemView.extend(SC.Control, {
    childViews: ['titleView', 'layerVisibilityView'],
    classNames: ['footprint-db-entity-edit-item-view'],
    contentDisplayProperties: ['status'],
    // Add this property to the isNew and isDirty record on the base class.
    // We never actually have a new DbEntity, since the server creates it (as of now)
    // But unconfigured DbEntities are provisional

    behavior: null,
    behaviorBinding: '*content.feature_behavior.behavior',
    behaviorStatus: null,
    behaviorStatusBinding: '*behavior.status',
    layerLibrariesApplicationEdit: null,
    layerLibrariesApplicationEditBinding: SC.Binding.oneWay('Footprint.layerLibrariesApplicationEditController.content'),
    configEntityKey: null,
    configEntityKeyBinding: SC.Binding.oneWay('*scenario.key'),
    scenario: null,
    /**
     * The LayerLibrary that has all Layers.
     */
    defaultEditLayerLibrary: null,
    defaultEditLayerLibraryBinding: SC.Binding.oneWay('Footprint.layerLibraryDefaultEditController.content'),

    layersStatus: null,
    layersStatusBinding: SC.Binding.oneWay('*defaultEditLayerLibrary.layers.status'),

    /***
     * Match the layer form the DEFAULT LayerLibrary to the corresponding DbEntity.
     * We use id since the content is currently not from a nestedStore but it probably will need to be
     */
    theLayer: function() {
        var layers = this.getPath('defaultEditLayerLibrary.layers') || [];
        var layer = layers.find(function(layer) {
            return layer.getPath('db_entity.id')==this.getPath('content.id');
        }, this);
        return layer;
    }.property('defaultEditLayerLibrary', 'layersAndDependenciesStatus', 'content', 'contentStatus').cacheable(),

    // Some of our DbEntities don't have Layers
    // We need to disable these DbEntities or figure out how to create the layer
    // The only exception right now is when the DbEntity new, meaning it was uploaded by
    // the user and doesn't have a layer yet
    isEnabled: function() {
        return this.get('theLayer') || this.get('isNew');
    }.property('theLayer', 'isNew').cacheable(),

    titleView: SC.LabelView.extend({
        layout: { left: 50, width: 230},
        valueBinding: SC.Binding.oneWay('.parentView*content.name'),
        behavior: null,
        behaviorBinding: '.parentView.behavior',
        behaviorStatus: null,
        behaviorStatusBinding: '.parentView.behaviorStatus',
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        toolTip: function() {
            if (this.getPath('behavior') && (this.get('behaviorStatus') & SC.Record.READY)) {
                var layer_behavior = this.getPath('behavior.key');
                if (layer_behavior == 'behavior__editable_feature'
                || layer_behavior == 'behavior__scenario_end_state'
                || layer_behavior == 'behavior__agriculture_scenario'
                || layer_behavior == 'behavior__base_agriculture') {
                return 'Editable Feature';
            }
            else {
                return 'Non-editable Feature';
            }
            }
            return 'Layer';
        }.property('behavior' , 'behaviorStatus').cacheable()
    }),

    layerVisibilityView: Footprint.LayerVisibilityView.extend({
        layout: { right:0, width: 100},
        isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        theLayerBinding: SC.Binding.oneWay('.parentView.theLayer'),
        scenarioBinding: SC.Binding.oneWay('.parentView.scenario'),
        layerLibrariesApplicationEditBinding: SC.Binding.oneWay('.parentView.layerLibrariesApplicationEdit').defaultValue(null)
    }),

    // Excluding this for now since it whines with a bunch of warnings about visibilty when the disclosure for
    // the layer group is closed
    progressOverlayView: Footprint.ProgressOverlayView.extend({
        layout: { left: 34, width:100, centerY: 0, height: 16},
        contentBinding: SC.Binding.oneWay('.parentView*content.db_entity'),
        progressBinding: SC.Binding.oneWay('*content.progress'),
        isOverlayVisibleBinding:SC.Binding.oneWay('*content.saveInProgress')
    })
});
