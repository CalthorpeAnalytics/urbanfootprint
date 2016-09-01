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


sc_require('views/info_views/edit_records_select_view');
sc_require('views/cancel_button_view');
sc_require('views/save_overlay_view');
sc_require('views/info_views/info_pane_crud_buttons_view');
sc_require('views/detail_views/scenario_detail_view');

/***
 * The pane used to edit the settings of a new or existing PresentationMedium and the DbEntity to which it is associated (if any). The saving order of this will have to first save a created DbEntity and then the PresentationMedium if a DbEntity is being created here
 * @type {*} */
Footprint.ScenarioInfoPane = Footprint.PanelPane.extend({

    layout: { width: 600, height: 300, centerX: 0, centerY: 0 },
    classNames:'footprint-scenario-info-view'.w(),

    recordType: Footprint.Scenario,

    // Tells the pane elements that a save is underway, which disables user actions
    isSaving: null,
    isSavingBinding: SC.Binding.oneWay('Footprint.scenariosEditController.isSaving'),

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.scenariosEditController.arrangedObjects'),

    selection: null,
    selectionBinding: SC.Binding.from('Footprint.scenariosEditController.selection'),

    contentView: SC.View.extend({
        classNames:'footprint-info-content-view'.w(),
        childViews:['titleView', 'scenarioSelectView', 'editableContentView', 'infoPaneButtonsView', 'overlayView'],
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        selection: null,
        selectionBinding: SC.Binding.from('.parentView.selection'),

        titleView: SC.LabelView.extend({
            layout: { left: 10, height: 25, top: 5 },
            classNames: ['footprint-info-title-view'],
            value: 'Manage Scenarios'
        }),

        scenarioSelectView: Footprint.EditRecordsSelectView.extend({
            layout: {width:.36, left: 10, bottom: 40, top: 30},
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            selectionBinding: SC.Binding.from('.parentView.selection'),
            deletableNameProperty: 'isDeletable',
            copyIsVisible: YES
        }),

        overlayView: Footprint.SaveOverlayView.extend({
            savingMessage: 'Saving Scenario...\n',
            isVisibleBinding: SC.Binding.oneWay('.pane.isSaving')
        }),

        editableContentView: Footprint.ScenarioDetailView.extend({
            layout: {top: 30, left: 245, bottom: 40, right: 20},
            layerId: 'scenario-detail-view',
            // Edit just the single selected Scenario
            contentBinding: SC.Binding.oneWay('.parentView*selection.firstObject')
        }),

        infoPaneButtonsView: Footprint.InfoPaneCrudButtonsView.extend({
            layout: { bottom: 0, height: 35, left: 10, right: 20 },
            recordTypeName: 'Scenario',
            selectionBinding: SC.Binding.oneWay('.parentView.selection'),
            selectedItem: null,
            selectedItemBinding: SC.Binding.oneWay('*selection.firstObject'),
            contentBinding: SC.Binding.oneWay('.parentView.content'),
            closeButtonLayout: {bottom: 10, left: 0, height:24, width:80},
            saveButtonLayout: {bottom: 10, left: 90, height:24, width:80},
            saveButtonForSelectionOnly: YES,

            nestedStoreContentStatusBinding: SC.Binding.oneWay('*selectedItem.status'),
            nestedStoreHasChanges: null,
            nestedStoreHasChangesBinding: SC.Binding.oneWay('*selectedItem.store.hasChanges'),
            nestedStoreContent: function() {
                // GATEKEEP: No nested content.
                var nestedStoreContent = this.get('selectedItem');
                if (!nestedStoreContent)
                    return null;
                // GATEKEEP: Doesn't exist in the master store yet.
                var storeKey = nestedStoreContent.get('storeKey');
                var store = nestedStoreContent.getPath('store.parentStore');
                // The check of < 0 is a bug work around for materializeRecord of nested records
                var id = store.idFor(storeKey);
                if (!id || id < 0)
                    return null;
                // Return the master store's copy of the record.
                return store.find(nestedStoreContent.constructor, nestedStoreContent.get('id'));
            }.property('selectedItem', 'nestedStoreContentStatus', 'nestedStoreHasChanges').cacheable(),

            progressOverlayView: SC.View.extend({
                childViews: ['progressView', 'updatingIconView', 'updatingTitleView'],
                layout: {left: 180, top: 0},
                selectedItem: null,
                selectedItemBinding: SC.Binding.oneWay('.parentView.selectedItem'),
                nestedStoreContent: null,
                nestedStoreContentBinding: SC.Binding.oneWay('.parentView.nestedStoreContent'),

                saveInProgress:null,
                saveInProgressBinding:SC.Binding.oneWay('*nestedStoreContent.saveInProgress'),

                isVisible: function() {
                    return (this.get('nestedStoreContent') && (
                        // Record is READY but post_save is in-progress
                        this.get('saveInProgress')
                    )) ? YES : NO;
                }.property('nestedStoreContent', 'saveInProgress').cacheable(),

                updatingIconView: SC.ImageView.extend({
                    layout: { left:0, width:24, height:24, right: 32},
                    useCanvas: NO,
                    value: sc_static('footprint:images/spinner24.gif'),
                    isVisibleBinding: SC.Binding.oneWay('.parentView.isVisible')
                }),
                updatingTitleView: SC.LabelView.extend({
                    layout: {left: 35, top: 5, right: 0.7 },
                    value: 'Processing...',
                    isVisibleBinding: SC.Binding.oneWay('.parentView.isVisible')
                }),
                progressView: Footprint.ProgressOverlayForNestedStoreView.extend({
                    layout: { left:0.3, right:5, top: 5, height: 16},
                    nestedStoreContentBinding: SC.Binding.oneWay('.parentView.selectedItem')
                })
            })
        })
    })
});
