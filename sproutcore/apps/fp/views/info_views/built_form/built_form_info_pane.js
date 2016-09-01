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


sc_require('views/info_views/built_form/urban_built_forms/manage_building_view');
sc_require('views/info_views/built_form/urban_built_forms/manage_building_type_view');
sc_require('views/info_views/built_form/urban_built_forms/manage_placetype_view');


Footprint.BuiltFormInfoPane = SC.PalettePane.extend({
    classNames: ['footprint-add-building-pane'],
    layout: { centerX: 0, centerY: 0, width: 1250, height: 650 },

    // This takes up most of the screen. Don't let the user click behind it
    isModal: YES,

    // Only run this on pane creation
    nowShowing:function() {
        var recordType = Footprint.builtFormEditRecordTypeController.get('content');
        return this.getPath('context.nowShowing') ||
            (recordType && recordType.toString()) ||
            'Footprint.ManageBuildingView';
    }.property('context').cacheable(),

    // Tells the pane elements that a save is underway, which disables user actions
    // In the case of BuiltForm management the first view to store the recordsEditController
    // is the nowShowing view below
    isSaving: null,
    isSavingBinding: SC.Binding.oneWay('.contentView*contentView.recordsEditController.isSaving'),

    contentView: SC.ContainerView.design({
        classNames: ['footprint-add-built-form-container-view'],
        childViews: ['closeButtonView', 'toggleButtonsView'],

        recordType: null,
        // The recordType is stored in the contentView of this view (the nowShowing view)
        recordTypeBinding: SC.Binding.oneWay('*contentView.recordType'),
        // Likewise for the current selectedItem
        selectedItemBinding: SC.Binding.oneWay('*contentView.selectedItem'),

        nowShowingBinding: SC.Binding.oneWay('.parentView.nowShowing'),

        closeButtonView: SC.ImageButtonView.extend({
            layout: {left: 12, top: 9, width: 18, height: 18},
            classNames: 'footprint-close-panel-button-view'.w(),
            action: 'doPromptCancel',
            image: 'close-panel-icon'
        }),

        toggleButtonsView: SC.SegmentedView.extend({
            layout: {top: 5, centerX: 0, width: 500, height:22},
            crudType: 'view',
            selectSegmentWhenTriggeringAction: YES,
            itemTitleKey: 'title',
            itemActionKey: 'action',
            itemValueKey: 'title',
            itemIsEnabledKey: 'isEnabled',

            layers: null,
            layersBinding: SC.Binding.oneWay('Footprint.layersController.content'),
            layersAndDependenciesStatus: null,
            layersStatusBinding: SC.Binding.oneWay('Footprint.layersController*content.status'),

            rawItems: [
                SC.Object.create({title: 'Building',  action: 'doManageBuildings', recordType:Footprint.Building, isEnabled: NO}),
                SC.Object.create({title: 'Building Type', action: 'doManageBuildingTypes', recordType:Footprint.BuildingType, isEnabled: NO}),
                SC.Object.create({title: 'Placetype', action: 'doManagePlacetypes', recordType:Footprint.UrbanPlacetype, isEnabled: NO}),
                SC.Object.create({title: 'Crop',  action: 'doManageCrops', recordType:Footprint.Crop, isEnabled: NO}),
                SC.Object.create({title: 'Crop Type', action: 'doManageCropTypes', recordType:Footprint.CropType, isEnabled: NO}),
                SC.Object.create({title: 'Landscape Type', action: 'doManageLandscapeTypes', recordType:Footprint.LandscapeType, isEnabled: NO})
            ],

            isItemEnabled: function (item) {
                var ag_types = ['Footprint.Crop', 'Footprint.CropType', 'Footprint.LandscapeType'];
                var urban_types = ['Footprint.Building', 'Footprint.BuildingType', 'Footprint.UrbanPlacetype'];
                // Find the optional toolController boolean for this item type
                var layers = F.layersController.get('content');
                if (layers) {
                    var agLayers = layers.filter(function(layer) {
                        return layer.get('dbEntityKey') == 'future_agriculture_canvas' ||
                            layer.get('dbEntityKey') == 'base_agriculture_canvas'
                    });

                    var agItem = ag_types.contains(String(item.recordType));
                    var urbanItem = urban_types.contains(String(item.recordType));

                    if (agLayers.length > 0 && agItem) {
                        return YES
                    }
                    if (urbanItem) {
                        return YES
                    }
                    return NO;
                }
            },

            items: function () {
                return this.get('rawItems').map(function (item) {
                    return SC.Object.create($.extend({},
                        item,
                        // merge a dict that enables it if it's configured for the active layer, otherwise disables
                        {isEnabled: this.isItemEnabled(item)}));
                }, this);
            }.property('layers', 'layersAndDependenciesStatus').cacheable(),

            value: Footprint.builtFormEditRecordTypeController.get('content'),
            valueObserver: function() {
                var recordType = Footprint.builtFormEditRecordTypeController.get('content');
                // Updates value so the right tab is highlighted. Clicking the tabs will do this automatically,
                // this is for launching the pane from elsewhere
                if (recordType) {
                    var matchingItem = this.get('items').filter(function(item) {
                        return item.recordType==recordType
                    })[0];
                    if (matchingItem)
                        this.setIfChanged('value', matchingItem.title);
                }
            }.observes('Footprint.builtFormEditRecordTypeController.content')
        })
    })
});
