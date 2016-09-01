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


sc_require('views/save_button_view');
sc_require('views/cancel_button_view');
sc_require('views/revert_button_view');
sc_require('views/info_views/progress_bar_view');

Footprint.CancelRevertSaveButtonsView = SC.View.extend({
    classNames: ['footprint-cancel-save-ok-buttons-view'],
    childViews: ['revertButtonView', 'cancelButtonView', 'progressBarView', 'saveButtonView', 'saveAllButtonView'],
    /***
     * The list of items to cancel, revert, or save.
     * For revert and save by default all items are processed, unless selectedItem is specified,
     * in which case only the selected item is processed.
     * Cancel always reverts all items and closes the modal
     */
    content: null,
    /***
     * The status of the content. Override if the content doesn't hold a status
     */
    status: function() {
        return this.getPath('content.status');
    }.property('.content').cacheable(),

    /***
     * The selected item of the content. If a selected item exists it will be saved or reverted.
     * Otherwise save/revert apply to all new or edited items.
     */
    selectedItem: null,
    selectedItemStatus: null,
    selectedItemStatusBinding: SC.Binding.oneWay('*selectedItem.status'),
    resolvedContent: function() {
        return this.get('selectedItem') ? this.get('selectedItem') : this.get('content');
    }.property('content', 'selectedItem').cacheable(),
    resolvedStatus: function() {
        return this.get('selectedItem') ? this.getPath('selectedItemStatus') : this.get('status');
    }.property('selectedItem', 'selectedItemStatus', 'status').cacheable(),

    revertButtonView: Footprint.RevertButtonView.extend({
        layout: { left: 0, width: 80, height: 24 },
        contentBinding: SC.Binding.oneWay('.parentView.resolvedContent'),
        statusBinding: SC.Binding.oneWay('.parentView.resolvedStatus'),
        buttonTitle: 'DMUI.Revert',
        hint: 'DMUI.RevetHint',
    }),

    cancelButtonView: Footprint.CancelButtonView.extend({
        layout: { left: 100, width: 80, height: 24 },
        // Always revert all items
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        hint: 'DMUI.CancelHint',
        buttonTitle: 'DMUI.Cancel'
    }),

    progressBarView: Footprint.ProgressBarView.extend({
        layout: { right: 80, width: 300, height: 24 },
        titleViewLayout: {left: 0, width: 100, top: 0, bottom: 0},
        progressBarLayout: {top: 5, bottom: 5, left: 200, right: 0},
        title: 'DMUI.Saving',
        nestedStoreContentBinding: SC.Binding.oneWay('.parentView.resolvedContent')
    }),

    saveButtonView: Footprint.SaveButtonView.extend({
        layout: { right: 100, width: 80, height: 24 },
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.resolvedContent'),
        statusBinding: SC.Binding.oneWay('.parentView.resolvedStatus'),
        buttonTitle: 'DMUI.SaveChanges',
        action: 'doSave',
        toolTip: 'DMUI.SaveAllHint'
    }),

    saveAllButtonView: Footprint.SaveButtonView.extend({
        layout: { right: 0, width: 80, height: 24 },
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        status: null,
        statusBinding: SC.Binding.oneWay('.parentView.status'),
        title: 'DMUI.SaveAllChanges',
        action: 'doSave',
        toolTip: 'DMUI.SaveHint'
    })
});
