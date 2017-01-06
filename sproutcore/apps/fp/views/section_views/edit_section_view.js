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


sc_require('views/info_views/attribute_editing/scag_existing_land_use_parcels_editor_view');
sc_require('views/info_views/attribute_editing/scag_tier2_taz_editor_view');
sc_require('views/info_views/attribute_editing/scag_general_plan_parcels_editor_view');
sc_require('views/info_views/attribute_editing/scag_city_boundary_editor_view');
sc_require('views/info_views/attribute_editing/scag_scenario_planning_zones_editor_view');
sc_require('views/info_views/attribute_editing/default_editor_view');
sc_require('views/overlay_view');

Footprint.EditSectionView = SC.View.extend({
    classNames: ['footprint-edit-section-view', 'footprint-map-overlay-section'],
    childViews: ['editableLayerInfoView', 'contentView', 'overlayView'],

    activeLayer: null,
    activeLayerBinding: SC.Binding.oneWay('Footprint.layerActiveController.content'),

    content: null,
    contentBinding: SC.Binding.oneWay('Footprint.featuresEditController.content'),

    editorView: null,
    editorViewBinding: SC.Binding.oneWay('Footprint.layerActiveController.editorView'),

    /***
     * We observe the active controller since our edit controller is just thus-far loaded
     * features of the sparse array. We don't want to allow editing until the entire sparse
     * array loads
     */
    overlayView: Footprint.OverlayView.extend({
        contentBinding: SC.Binding.oneWay('Footprint.featuresActiveController.content'),
        statusBinding:SC.Binding.oneWay('Footprint.featuresActiveController.status'),
        /***
         * Override to show the overlay until the sparse Array features are fully loaded
         * When sparse arrays are loading it has a special READY status, so we explicitly
         * check for ready clean or ready dirty before hiding the overlay
         * @param status
         * @returns {*}
         */
        statusMatches: function(status) {
            return ![SC.Record.EMPTY, SC.Record.READY_CLEAN, SC.Record.READY_DIRTY].contains(this.get('status'));
        }
    }),

    editableLayerInfoView: SC.View.extend({
        childViews: ['layerView', 'buttonsView', 'userView', 'recordsView'],
        layout: {height: 86},
        backgroundColor: 'lightgrey',
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        activeLayer: null,
        activeLayerBinding: SC.Binding.oneWay('.parentView.activeLayer'),

        layerView: SC.View.extend({
            childViews: ['layerTitleView', 'layerNameView'],
            layout: {height: 38},
            title: null,
            titleBinding: SC.Binding.oneWay('.parentView*activeLayer.name'),

            layerTitleView: SC.LabelView.extend({
                classNames: ['footprint-editable-9font-title-view'],
                layout: {left: 5, height: 16, top: 5, width: 70},
                value: 'Edit Layer:'
            }),
            layerNameView: SC.LabelView.extend({
                classNames: ['footprint-active-built-form-name-view', 'toolbar'],
                layout: {height: 16, top: 20},
                textAlign: SC.ALIGN_CENTER,
                valueBinding: SC.Binding.oneWay('.parentView.title'),
            })
        }),

        /***
         * The buttons used for the analysis modules or the builder modules
         */
        buttonsView: SC.View.extend({
            childViews: ['buttonsView', 'toggleButtons', 'bufferView'],
            layout: {top: 40, left: 0, height: 30},

            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            // Enable the buttons if the layer is editable
            isEnabled: null,
            isEnabledBinding: SC.Binding.and(
                '.parentView.isEnabled',
                'Footprint.layerActiveController.layerIsEditable'
            ),

            /***
             * These buttons are shown if the features of the active layer are editable
             */
            buttonsView: Footprint.SaveButtonWithStatusView.extend({
                layout: {top: 0, left: 5, width: 150},
                updatingStatusLayout: { top: 0, left: 65, width: 85},

                // The spinner tracks the state of the first feature
                contentBinding: SC.Binding.oneWay('.parentView.content'),
                statusBinding: SC.Binding.oneWay('Footprint.featuresEditController.featuresStatus'),
                monitorProgressOfFirstItem: YES,
                updatingTitle: 'Applying',

                // Change color is the toggle view is checked to indicated clearing the base
                // This is only for scenario builders (e.g. EndState Feature), nor for base condition features
                isClearBase: null,
                isClearBaseBinding: SC.Binding.oneWay('.parentView.toggleView.value'),

                isEnabled: null,
                isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

                // Override the saveButton view to apply class names
                saveButtonView: Footprint.SaveButtonView.extend({
                    layout:{top: 2, left: 0, height: 22, width: 60},
                    classNames: ['theme-button', 'theme-button-blue', 'footprint-buttons-for-builder-view'],
                    classNameBindings: ['isClearBase:is-clear-base'], // adds the is-editable when isEditable is YES

                    title: 'Apply',
                    action: 'doFeaturesUpdate',

                    isClearBase: null,
                    isClearBaseBinding: SC.Binding.oneWay('.parentView.isClearBase'),

                    toolTip: 'Apply built form and calculate new attributes',
                    contentBinding: SC.Binding.oneWay('.parentView.content'),
                    contentLength: 0,
                    contentLengthBinding: SC.Binding.oneWay('.parentView*content.length'),

                    toolState: null,
                    toolStateBinding: SC.Binding.oneWay('Footprint.toolController.featurerIsEnabled'),

                    isBuilder: NO,
                    isBuilderBinding: SC.Binding.oneWay('Footprint.layerActiveController.isBuilderView'),
                    isDirty: null,
                    isDirtyBinding: SC.Binding.oneWay('.parentView.status').matchesStatus(SC.Record.DIRTY),
                    parentViewIsEnabled: null,
                    parentViewIsEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

                    /***
                     * Builder tools always enable the save button, since picking a built form or setting
                     * other parameters does not dirty features (we apply the users choices at the time of update)
                     * Feature editors require that the records be dirty before enabling save
                     */
                    isEnabled: function() {
                        return this.getPath('parentViewIsEnabled') && this.get('contentLength') &&
                            (this.get('isBuilder') || this.get('isDirty'))
                    }.property('isBuilder', 'isDirty', 'parentViewIsEnabled', 'contentLength').cacheable(),
                })
            }),

            /***
             * Exposes undo and redo button.
             * This is purposely positioned over the save status since it can't be used when saving is occurring,
             * so we hide it
             */
            bufferView: SC.SegmentedView.extend({
                layout: {top: 2, height: 27, width: 100, right: 20},
                shouldHandleOverflow: NO,
                selectSegmentWhenTriggeringAction: NO,
                itemActionKey: 'action',
                itemIconKey: 'icon',
                itemKeyEquivalentKey: 'keyEquivalent',
                itemValueKey: 'title',
                itemWidthKey: 'width',
                itemIsEnabledKey: 'isEnabled',
                itemToolTipKey: 'toolTip',
                // Disable whilst features are updating or post-save processing
                isEnabledBinding: SC.Binding.oneWay('Footprint.featuresEditController.recordsAreUpdating').not(),

                items: [
                    // View and edit the selected item's attributes
                    SC.Object.create({
                        icon: sc_static('images/icons/sc-icon-undo-24.png'),
                        keyEquivalent: 'ctrl_u',
                        action: 'doFeaturesUndo',
                        isEnabledBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController*featureUndoManager.canUndo').bool(),
                        toolTip: 'Undo the last changes made to the features of this layer. This might undo changes to features that are no longer selected.',
                        type: 'chronicler',
                        width: 45
                    }),
                    SC.Object.create({
                        icon: sc_static('images/icons/sc-icon-redo-24.png'),
                        keyEquivalent: 'ctrl_r',
                        action: 'doFeaturesRedo',
                        isEnabledBinding: SC.Binding.oneWay('Footprint.layerSelectionActiveController*featureUndoManager.canRedo').bool(),
                        toolTip: 'Redo the last changes made to the features of this layer. This might redo changes to features that are no longer selected.',
                        type: 'chronicler',
                        width: 45
                    }),
                ]
            }),
        }),

        userView: SC.View.extend({
            childViews: ['userTitleView', 'userNameView'],
            layout: {top: 70, height: 16, bottom: 5, width: 100},
            userTitleView: SC.LabelView.extend({
                classNames: ['footprint-editable-9font-title-view'],
                layout: {left: 5, height: 16, top: 5, width: 25},
                value: 'User:'
            }),
            userNameView: SC.LabelView.extend({
                classNames: ['footprint-editable-9font-title-view'],
                layout: {left: 30, height: 16, top: 5, width: 70},
                valueBinding: SC.Binding.oneWay('Footprint.userController.content.firstObject.username').transform(function (user) {
                    if (user) {
                        return user.capitalize();
                    }
                }),
            }),
        }),

        recordsView: SC.View.extend({
            childViews: ['recordsTitleView', 'recordsNumberView'],
            layout: {top: 70, height: 16, bottom: 5, left: 100},
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            recordsTitleView: SC.LabelView.extend({
                classNames: ['footprint-editable-9font-title-view'],
                layout: {left: 5, height: 16, top: 5, width: 80},
                value: 'Selected Records:'
            }),
            recordsNumberView: SC.LabelView.extend({
                classNames: ['footprint-editable-9font-title-view'],
                layout: {left: 87, height: 16, top: 5, width: 35},
                status: null,
                statusBinding: '*content.status',
                content: null,
                contentBinding: SC.Binding.oneWay('.parentView.content'),

                value: function () {
                    return '%@'.fmt(
                            this.get('status') & SC.Record.READY || this.get('status') === SC.Record.EMPTY ? this.getPath('content.length') || 0 : '0');
                }.property('content', 'status').cacheable(),
            }),
        }),
    }),

    /***
     * This view is either the editor view or analysis module view
     * An AnalysisModule view: e.g. Footprint.%@EditorView'.fmt(activeLayerClassKey)
     * The Scenario Builder view:  Footprint.ScenarioBuilderManagementView
     * The Agriculture Builder view: Footprint.AgricultureBuilderManagementView
     */
    contentView: SC.ContainerView.extend({
        classNames: 'footprint-edit-section-content-view'.w(),
        layout: {top:86},
        transitionView: SC.ContainerView.PUSH,
        nowShowingBinding: SC.Binding.oneWay('.parentView.editorView'),
    }),
});
