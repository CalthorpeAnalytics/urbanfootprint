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

sc_require('views/info_views/layer/layer_style_left_side_view');
sc_require('views/info_views/layer/layer_style_right_side_view');
sc_require('views/loading_overlay_view');

/***
 * The pane used to edit the settings of a new or existing PresentationMedium and the DbEntity to
 * which it is associated (if any). The saving order of this will have to first save a created DbEntity and
 * then the PresentationMedium if a DbEntity is being created here
 *
 * @type {*} */
Footprint.LayerInfoPane = SC.PanelPane.extend({

    layout: { width: 650, height: 400, centerX: 0, centerY: 0 },
    classNames:'footprint-layer-info-view'.w(),

    selectedLayer: null,
    selectedLayerBinding: SC.Binding.oneWay('Footprint.layerEditController.content'),

    contentView: SC.View.extend({
        classNames:['footprint-info-content-view'],
        childViews:['updatingView', 'leftSideView', 'rightSideView', 'cancelSaveButtonsView'],

        selectedLayer: null,
        selectedLayerBinding: SC.Binding.oneWay('.parentView.selectedLayer'),

        updatingView: Footprint.LoadingOverlayView.extend({
            classNames: ['overlay-view-low-transparency'],
            layout: { top: 1, right: 1, left: 1, bottom: 1, zIndex: 999},
            isVisibleBinding: SC.Binding.oneWay('Footprint.layerEditController.layerIsSaving'),
            showLabel: YES,
            title: 'Processing New Style...'
        }),

        leftSideView: Footprint.LayerStyleLeftSideView.extend({
            layout: { width: 240, bottom: 40},
            selectedLayerBinding: SC.Binding.oneWay('.parentView.selectedLayer'),
            contentBinding: SC.Binding.oneWay('Footprint.styleableAttributesEditController.content'),
            selectionBinding: SC.Binding.from('Footprint.styleableAttributesEditController.selection')
        }),

        rightSideView: Footprint.LayerStyleRightSideView.extend({
            layout: {left: 240, bottom: 30}
        }),

        cancelSaveButtonsView: SC.View.extend({
            layout: { bottom: 0, height: 30, left: 0, right: 0},
            childViews: ['cancelButtonView', 'saveButtonView'],
            content: null,
            contentBinding: SC.Binding.oneWay('Footprint.layersEditController.content'),

            cancelButtonView: SC.ButtonView.extend({
                layout: { bottom: 5, right: 20, height: 24, width: 80 },
                localize: YES,
                title: 'Close',
                action: 'doPromptCancel',
                calculatedStatusBinding: SC.Binding.oneWay('Footprint.layersEditController.calculatedStatus')
            }),

            saveButtonView: SC.ButtonView.extend({
                layout: { bottom: 5, right: 110, height: 24, width: 80 },

                calculatedStatus: null,
                calculatedStatusBinding: SC.Binding.oneWay('Footprint.layersEditController.calculatedStatus'),
                isEnabled: function() {
                    // Enable saves for new content if an uploadId exists or its a clone
                    // Enable saves for all existing content
                    return this.get('calculatedStatus') === SC.Record.READY_DIRTY ;
                }.property('calculatedStatus').cacheable(),

                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                title: 'Save',
                action: 'doSaveLayer'
            })
        })
    })
});
