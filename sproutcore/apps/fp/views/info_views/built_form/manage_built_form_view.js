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

Footprint.ManageBuiltFormView = SC.View.extend({

    childViews: ['crudButtonsView'],

    // Set this to the BuiltForm subclass
    recordType: null,

    recordsEditController: null,

    content: null,
    contentBinding: SC.Binding.oneWay('*recordsEditController.arrangedObjects'),

    selection: null,
    selectionBinding: SC.Binding.from('*recordsEditController.selection'),

    selectedItem: null,
    selectedItemBinding: SC.Binding.from('*selection.firstObject'),

    // Tells the pane elements that a save is underway, which disables user actions
    isSaving: null,
    isSavingBinding: SC.Binding.oneWay('*recordsEditController.isSaving'),

    crudButtonsView: Footprint.InfoPaneCrudButtonsView.extend({
        closeButtonLayout: {bottom: 5, left: 20, height:24, width:80},
        progressOverlayLayout:  { left:200, width:250, bottom: 4, height: 26},
        saveButtonLayout: {bottom: 5, left: 120, height:24, width:80},
        layout: { bottom: 0, right: 0, height: 40 },

        selectedItem: null,
        selectedItemBinding: SC.Binding.from('.parentView.selectedItem'),

        // This is a hack since the progress overlay view only knows how to track on item
        // Give it the selected item if it's dirty. Else the first dirty item
        selectionBinding: SC.Binding.oneWay('.parentView*recordsEditController.representativeEditedRecord'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        // Save all the edited content. Not just the current item
        saveContentBinding: SC.Binding.oneWay('.parentView*recordsEditController.editedRecords')
    })
});
