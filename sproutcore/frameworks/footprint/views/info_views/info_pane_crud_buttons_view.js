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
 * The buttons at the bottom of an info pane.
 * Save, Revert, and Close are enabled according to the bound content's nestedStore
 * status.
 * @type {*|RangeObserver|Class|void}
 */

sc_require('views/info_views/progress_bar_view');

Footprint.InfoPaneCrudButtonsView = SC.View.extend({
    childViews: 'closeButtonView revertButtonView createButtonView progressOverlayView saveButtonView'.w(),
    classNames: ['footprint-crud-buttons-view'],
    // The name used to describe the Record type being edited. Used for the doCreate[recordTypeName] action
    recordTypeName: null,
    content: null,
    selection: null,
    // If YES, the save button corresponds with the selected. Otherwise it's active if anything is edited
    saveButtonForSelectionOnly: NO,
    /**
     * Optional array of items to save. If not specified then the state chart decides what needs to be saved
    */
    saveContent: null,
    /***
     * Required. The layout of the close button if visible.
     */
    closeButtonLayout: null,
    /***
     * Optional. The layout of the revert button if visible.
     */
    revertButtonLayout: null,
    /***
     * Optional. The layout of the created button if visible.
     */
    createButtonLayout: null,
    /***
     * Required. The layout of the save button if visible.
     */
    saveButtonLayout: null,
    /***
     * Optional. The layout of the progress Overlay
     */
    progressOverlayLayout: null,

    closeButtonView: SC.ButtonView.design({
        layoutBinding: SC.Binding.oneWay('.parentView.closeButtonLayout'),
        title: 'Close',
        action: 'doPromptCancel',
        isCancel: YES
    }),

    revertButtonView: SC.ButtonView.design({
        layoutBinding: SC.Binding.oneWay('.parentView.revertButtonLayout').transform(function(value) {
            return value || {};
        }),
        isVisibleBinding: SC.Binding.oneWay('.parentView.revertButtonLayout').bool(),
        title: 'Revert',
        action: 'doRevert',
        isEnabledBinding: SC.Binding.and('.parentView*content.store.hasChanges', '.parentView*content.store.hasNoBusyRecords')
    }),

    createButtonView: SC.ButtonView.design({
        layoutBinding: SC.Binding.oneWay('.parentView.createButtonLayout').transform(function(value) {
            return value || {};
        }),
        isVisibleBinding: SC.Binding.oneWay('.parentView.createButtonLayout').bool(),
        recordTypeName: null,
        recordTypeNameBinding: SC.Binding.oneWay('.parentView.recordTypeName'),
        icon: 'add-icon',
        title: function() {
            return 'New %@'.fmt(this.get('recordTypeName'));
        }.property('recordTypeName').cacheable(),
        action: function() {
            return 'doCreate%@'.fmt(this.get('recordTypeName'));
        }.property('recordTypeName').cacheable()
    }),

    progressOverlayView: Footprint.ProgressBarView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.progressOverlayLayout'),
        nestedStoreContentBinding: SC.Binding.oneWay('.parentView.selection'),
        titleViewLayout: {width: 250, top: 0, bottom: 0, left: 0},
        progressBarLayout: {top: 5, bottom: 5, left: 100}
    }),

    saveButtonView: SC.ButtonView.design({
        layoutBinding: SC.Binding.oneWay('.parentView.saveButtonLayout'),
        title: 'Save',
        action: 'doSave',
        // Optionally set the content to be saved. Otherwise it will default to whatever the
        // the statechart is configured to save
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.saveContent'),
        selection: null,
        selectionBinding: SC.Binding.oneWay('.parentView.selection'),

        saveButtonForSelectionOnly: null,
        saveButtonForSelectionOnlyBinding: SC.Binding.oneWay('.parentView.saveButtonForSelectionOnly'),
        hasChanges: null,
        hasChangesBinding: SC.Binding.oneWay('.parentView*content.store.hasChanges'),
        selectedItem: null,
        selectedItemBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),

        /**
         * Enable if anything is edited. If saveButtonForSelectionOnly is YES,
         * only enable if the single selection is dirty or new
         */
        isEnabled: function() {
            if (!(this.get('hasChanges')))
                return NO;

            if (!this.get('saveButtonForSelectionOnly') ||
                [SC.Record.READY_DIRTY, SC.Record.READY_NEW].contains(this.getPath('selectedItem.status'))) {
                return YES;
            }
        }.property('hasChanges', 'saveButtonForSelectionOnly', 'selectedItem').cacheable(),
    })
});
