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
 * TODO remove this in favor of info_pane_crud_buttons_view
 * @type {*|RangeObserver|Class|void}
 */
Footprint.InfoPaneButtonsView = SC.View.extend({

    classNames: "footprint-info-pane-buttons-view".w(),

    childViews: 'saveButton closeButton'.w(),
    // The content
    content: null,
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),
    // Indicates whether or not the content of the pane is editable
    isEditable: NO,
    // Indicates whether or not the content of the pane is editable and has changed--thus can be saved or cancelled
    isChanged: function() {
        return this.get('status') & SC.Record.READY_DIRTY
    }.property('status'),

    /*
     savingImage: SC.ImageView.design({
     layout: { bottom: 15, left: 175, height:16, width: 16 },
     value: sc_static('images/loading'),
     useImageCache: NO,
     isVisibleBinding: SC.Binding.from('parentView.editController*savingRecords.status').transform(
     function(value, isForward) {
     return value !== SC.Record.READY_CLEAN
     }
     )
     }),

     savingMessage: SC.LabelView.design({
     layout: { bottom: 8, left: 195, height:24, width: 100 },
     value: 'Saving ...',
     classNames: ['saving-message'],
     isVisibleBinding: SC.Binding.from('parentView.editController*savingRecords.status').transform(
     function(value, isForward) {
     return value !== SC.Record.READY_CLEAN
     }
     )
     }),

     deleteButton: SC.ButtonView.design({
     layout: {bottom: 10, left: 20, height:24, width:80},
     title: 'Delete',
     action: 'deleteRecord',
     isVisibleBinding: SC.Binding.from('.parentView.editController.contentIsChanged').bool().transform(
     function(value, isForward) {
     return !value;
     }
     )
     }),
     */

    /***
     * The save button transfers the edited data from the nestedStore to the main store and commits it to the server
     * It is only enabled when the controller indicates that the contentIsChanged
     */
     saveButton: SC.ButtonView.design({
         layout: {bottom: 10, right: 20, height:24, width:80},
         title: 'Save',
         action: 'doSave',
         isDefault: YES,
         isVisibleBinding: SC.Binding.oneWay('.parentView.isEditable'),
         isEnabledBindng: SC.Binding.oneWay('.parentView.isChanged')
     }),

    /***
     * Closes the view, discarding edited values that haven't been saved.
     */
    closeButton: SC.ButtonView.design({
        layout: {bottom: 10, height: 24, left: 20, width: 80},
        title: 'Close',
        action: 'doCancel',
        isCancel: YES,
        isVisibleBinding: SC.Binding.oneWay('.parentView.isEnabled')
    })
});
