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



sc_require('controllers/controllers');
/**
 * Manages a configEntity set, such as 'policy_sets' or 'built_form_sets' by storing the array of sets and setting its initial selection to the configEntity's selection
 * Mixes in SingleSelectionSupport, which updates the singleSelection property when the selection change, and updates the selection when the singleSelection property is set. When the singleSelection is update it in turn updates the configEntity's set
 *
 * This is a 2-way binding. 1) The ConfigEntity's specific selections.set property, 2) The ArrayController selection, which is simplified with the property singleSelection.
 * @type {Class}
 */
Footprint.SetsController = SC.ArrayController.extend(Footprint.SingleSelectionSupport, Footprint.ArrayContentSupport, {
    allowsEmptySelection:NO,
    listController: null,
    property:null,

    configEntity:null,
    configEntityBinding:SC.Binding.oneWay('*listController.selection.firstObject'),
    configEntityStatus:null,
    configEntityStatusBinding:SC.Binding.oneWay('*configEntity.status'),

    configEntitySet:function() {
        return this.getPath('configEntity.%@'.fmt(this.get('property')));
    }.property('configEntityStatus', 'property').cacheable(),

    contentBinding:SC.Binding.oneWay('.configEntitySet'),

    selectionPath:function() {
        return 'configEntity.selections.sets.%@'.fmt(this.get('property'));
    }.property('configEntity', 'property').cacheable(),

    contentObserver: function() {
        if (this.getPath('configEntity.status')===SC.Record.READY_CLEAN) {
            this.updateSelectionAfterContentChange();
            this.set('singleSelection', this.get('configEntitySelection'));
        }
    }.observes('*configEntity.status').cacheable(),

    /*
     * Property to read and update the value referenced by the selectionPath
     * The selection sj
     */
    configEntitySelection: function(keyProp, value) {
        if (value !== undefined) {
            // Update the configEntity selection. Note that this will make the ConfigEntity dirty
            // Don't do this. We don't save it anyway. Selections should be per-user anyway
            //this.setPath(this.get('selectionPath'), value)
        }
        return this.getPath(this.get('selectionPath'));
    }.property('configEntity', 'selectionPath'),

    /*
     * When singleSelection is updated via set, we update the configEntitySelection property
     */
    singleSelectionObserver: function() {
        this.set('configEntitySelection', this.get('singleSelection'));
    }.observes('.singleSelection'),

    toString: function() {
        return this.toStringAttributes('content configEntity property selectionPath configEntitySelection'.w());
    }
});
