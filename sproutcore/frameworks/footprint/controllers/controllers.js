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
 * The standardized packaging of controllers for use by views for editing and cloning
 */
Footprint.ControllerConfiguration = SC.Object.extend({

    /***
     * An SC.ObjectController that edits one or more objects
     */
    editController:null,
    /***
     * A list controller, such as an ListController or TreeController that manages the objects
     */
    itemsController:null,
    /***
     * A controller with additional computed properties about the objects, otherwise the same as itemsController
     */
    recordSetController:null

    //toString: function() {
    //    return "%@:\n%@".fmt(sc_super(), this.toStringAttributes('editController itemsController recordSetController'.w()));
    //}
});

Footprint.SingleSelectionSupport = {

    // Whenever something changes the mixer's selection, notify the singleSelection property
    // so that it updates immediate for those that are bound to/observing it
    selectionObserver: function() {
        this.notifyPropertyChange('singleSelection');
    }.observes('.selection'),

    /***
     * Property to read and write a single value from/to the selection property
     * @param keyProp
     * @param value
     */
    singleSelection: function(keyProp, value) {
        //Clear the selection and add the selected set of the controller
        if (value !== undefined) {
            this.selectObject(value);
        }
        return this.getPath('selection.firstObject');
    }.property('selection').cacheable()
};


Footprint.ArrayContentSupport = {
    contentHasChangedObserver: function() {
        if (this.getPath('content.status') & SC.Record.READY) {
            this.notifyPropertyChange('firstObject');
            this._scac_contentDidChange();
            this.updateSelectionAfterContentChange();
            if (this.firstObject() !== this.get('firstObject'))
                throw "firstObject did not invalidate. Should be %@ but got %@".fmt(this.firstObject(), this.get('firstObject'))
        }
    }.observes('*content.status')
};

Footprint.ArrayController = SC.ArrayController.extend(Footprint.ArrayContentSupport, {
    allowsEmptySelection:NO,
    allowsMultipleSelection:NO,
    canDeleteContent:YES,
    // Sometimes we'll destroy the item on the server if its removed from the Array.
    // For some lists we'll just want to remove the item from the list, especially for Libraries
    destroyOnRemoval:NO

    //toString: function() {
    //    return this.toStringAttributes('content'.w(), {content: function(content) {
    //        return content && content.map(function(item) {
    //            return item.toString()
    //        }, this).join("\n---->");
    //    }});
    //}

});

/***
 * Helps an editController stay up to date with the non-edit controller selection
 * @type {{selectionDidChange: Function}}
 */
Footprint.EditControllerSupport = {
    /***
     * The non-nested controller whose selection we are tracking
    */
    sourceController: null,
    sourceSelectionDidChange: function() {
        if (this.get('content')) {
            // Get the unnested store selection for the sourceController
            var selection = this.getPath('sourceController.selection');
            if (!selection)
                return;
            var selectedIds = selection.mapProperty('id');

            // Find the nested store equivalent
            var storeItems = this.get('content').filter(
                function(item) {
                    return selectedIds.contains(item.get('id'));
                }
            );

            // If it doesn't match our selection update our selection
            if (!SC.Set.create(storeItems).isEqual(SC.Set.create(this.get('selection'))))
                this.selectObjects(storeItems);
        }
    }.observes('*sourceController.selection', '.content'),

    // If our selection goes to none selected resync with the source controller's selection
    // This happens when a managing state is exited
    selectionDidChange: function() {
        if (this.getPath('selection.length') == 0 &&
            this.getPath('sourceController.selection.length') > 0) {
            // Resync
            this.sourceSelectionDidChange();
        }
    }.observes('.selection'),

    /***
     * Keep track of what records are new or dirty
     */
    editedRecordsObserver: function(object, property, value) {
        // For status or saveInProgress changes, see if anything important happened
        if (object && (
            // Did the value actually change?
            !object.didChangeFor('editedRecordsObserver', 'status', 'saveInProgress') ||
            // If the value that changed did not become edited/saveInProgress and none such records exist, simply quit
            !(Footprint.Record.EDITING_STATES.contains(object.get('status')) ||
              object.get('saveInProgress') ||
              this.getPath('editedRecords.length')))
        )
            return;

        // Who's edited/saveInProgress?
        this.set('editedRecords', this.filter(function(record) {
            return Footprint.Record.EDITING_STATES.contains(record.get('status')) || record.get('saveInProgress');
        }));
    }.observes('*content.@each.status', '*content.@each.saveInProgress'),

    editedRecords: null,
    /***
     * This is a hack that supports the save process.
     * It gives one of the edited items, prioritizing the selected item if it's dirty.
     */
    representativeEditedRecord: null,
    representativeEditedRecordBinding: SC.Binding.or('.firstEditedSelectedItem', '*editedRecords.firstObject'),
    firstEditedSelectedItem: function() {
        var selection = this.get('selection');
        var editedRecords = this.get('editedRecords') || [];
        return selection && selection.find(function(item) {
            return editedRecords.contains(item);
        });
    }.property('editedRecords', 'selection').cacheable()
};

/***
 * Copies the behavior of SC.ManyArray to calculate a combined status of the items. The max status of all items is returned by calculatedStatus
 * @type {{contentDidChange: Function, calculateStatus: Function, _calculateStatus: Function, calculatedStatus: null, refresh: Function, toString: Function}}
 */
Footprint.CalculatedStatusSupport = {

    // Set up observers.
    contentDidChange: function() {
        var observedRecords = this.observedRecords;
        if (!observedRecords) observedRecords = this.observedRecords = [];
        var record, i, len;
        // If any items in observedRecords are not in content, stop observing them.
        len = observedRecords.length;
        for (i = len - 1; i >= 0; i--) {
            record = observedRecords.objectAt(i);
            if (!this.contains(record)) {
                record.removeObserver('status', this, this.calculateStatus);
                observedRecords.removeObject(record);
            }
        }
        // If any item in content is not in observedRecords, observe them.
        len = this.get('length');
        for (i = 0; i < len; i++) {
            record = this.objectAt(i);
            if (!observedRecords.contains(record)) {
                record.addObserver('status', this, this.calculateStatus);
                this.invokeOnce(this.calculateStatus);
                observedRecords.pushObject(record);
            }
        }
    }.observes('[]'),

    calculateStatus: function() {
        this.invokeOnce(this._calcluateStatus);
    },
    _calcluateStatus: function() {
        var length = this.get('length');
        var maxStatus = 0;
        for (i = 0; i < length; i++) {
            var status = this.objectAt(i).get('status');
            maxStatus = status > maxStatus ? status : maxStatus;
        }
        var status = maxStatus || SC.Record.EMPTY;
        this.setIfChanged('calculatedStatus', status);
    },

    calculatedStatus: null,

    refresh: function() {
        var length = this.get('length');
        for (i = 0; i < length; i++) {
            var record = this.objectAt(i);
            record.refresh();
        }
    }

    //toString: function() {
    //    return sc_super() + "\n---->" +
    //        this.map(function(item) {
    //            return item.toString()
    //        }, this).join("\n---->");
    //}
};

// A nested store version of the record that expects a sourceController with one record
// As an
Footprint.EditController = SC.ObjectController.extend({
    recordType: null,
    store: null,
    /***
     * The non-nested store controller. It can have one content object or many.
     */
    sourceController: null,
    /***
     * Bind this to something of the sourceController, either the content or the first selected item of the content,
     * for instance
     */
    sourceControllerContent: null,

    /***
     * Set by the Crud stat when saving starts and ends
     */
    isSaving: NO,

    /***
     * Content is the nested store version of the sourceController content
     */
    content: function() {
        var store = this.get('store');

        var recordType = typeof this.get('recordType') === 'string' ?
            SC.objectForPropertyPath(this.get('recordType')) :
            this.get('recordType');

        if (!store || !recordType)
            return null;
        return this.get('store').find(
            recordType,
            this.getPath('sourceControllerContent.id')
        );

    }.property('recordType', 'store', 'sourceControllerContent').cacheable()
});

/***
 * A controller whose content is the nested store version of the single item of the
 * sourceController.
 */
Footprint.EditObjectController = Footprint.EditController.extend({
    sourceControllerContentBinding: SC.Binding.oneWay('*sourceController.content')
});
/***
 * A controller whose content simply the selectoin.firstObject of a EditArrayController.
 */
Footprint.EditSelectedItemController = Footprint.EditController.extend({
    // Override the EditController's content
    content: null,
    contentBinding: SC.Binding.oneWay('*sourceController.selection.firstObject').defaultValue(null),
    storeBinding: SC.Binding.oneWay('*content.store')
});

// This controller's content is the associated (non-deleted) children of the specified recordType
// in the specified nested store. For example, set parentRecord to the selected project and recordType
// to Footprint.Scenario to get the nested-store copies of the current project's scenarios.
Footprint.EditArrayController = Footprint.ArrayController.extend(Footprint.EditControllerSupport, Footprint.CalculatedStatusSupport, {

    // Called if the sourceController changes or its items or their statuses do
    sourceControllerObserver: function() {
        this.invokeOnce('_sourceControllerObserver');
    }.observes('.sourceController', '*sourceController.[]', '*sourceController.@each.status'),

    _sourceControllerObserver: function() {
        this.propertyDidChange('content');
    },

    recordType: null,
    store: null,
    storeBinding: SC.Binding.oneWay('.store'),

    // a property on the recordType being queried. If specified,
    // it will be used as a query filter matching the value of parentRecord
    // content will be null whenever parentEntityKey is specified but parentRecord is null.
    parentEntityKey: null,
    parentRecord: null,
    /***
     * Set by the Crud state when saving starts and ends
     */
    isSaving: NO,
    /**
     * Optional values for conditions
     */
    conditions: function() {
        return 'deleted != YES';
    }.property().cacheable(),

    /***
     * The content of the EditArrayController are all items of the sourceController plus items
     * from the store that are new. If conditions and parentRecord are specified, they are used
     * for further filtering
     */
    content: function() {
        var store = this.get('store'),
            parentRecord = this.get('parentRecord'),
            parentEntityKey = this.get('parentEntityKey');

        var recordType = typeof this.get('recordType') === 'string' ?
            SC.objectForPropertyPath(this.get('recordType')) : this.get('recordType');

        if (!store || !recordType || (parentEntityKey && !parentRecord))
            return null;

        var inSourceControllerOrNewConditions = '({sourceIds} CONTAINS id OR {statuses} CONTAINS status)';
        var sourceIds = (this.get('sourceController') || []).mapProperty('id')
        return this.get('store').find(SC.Query.local(recordType, merge(this.get('parentEntityKey') ? {
            conditions: '%@ $ {parentRecord} AND deleted != YES AND %@'.fmt(parentEntityKey, inSourceControllerOrNewConditions),
            parentRecord: this.get('store').find(parentRecord.constructor, parentRecord.get('id')),
        } : {
            conditions: '%@ AND %@'.fmt(this.get('conditions'), inSourceControllerOrNewConditions),
        }, {
            // Always filter by sourceIds or status new. Also allow busy states saving new records don't disappear
            sourceIds: sourceIds,
            statuses: [SC.Record.READY_NEW, SC.Record.BUSY_COMMITTING, SC.Record.BUSY_CREATING, SC.Record.BUSY_LOADING]
        })));
    }.property('recordType', 'store', 'parentRecord').cacheable()
});

Footprint.RecordControllerChangeSupport = {

    contentDidChangeEvent: null,
    selectedItemDidChangeEvent: null,
    /***
     * Announces a change of the content when its status matches READY
     */
    contentDidChange: function() {
        if (this.didChangeFor('contentOrStatusChange', 'status', 'content') &&
            // TODO this should just be READY_CLEAN, but our status is sometimes dirty
            // We have to check content.status instead of status. When content changes
            // status will still have the previous status.
            [SC.Record.READY_CLEAN, SC.Record.READY_DIRTY].contains(this.getPath('content.status')))
            // Give bindings a change to update before calling
            this.invokeNext(function() {
                Footprint.statechart.sendAction(this.get('contentDidChangeEvent'), this);
            })
    }.observes('.content', '.status'),

    readonlySelectedItem: null,
    readonlySelectedItemBinding: SC.Binding.oneWay('*selection.firstObject'),
    /***
     * Announces a change of the selected item.
     */
    selectedItemDidChangeObserver: function() {
        if (this.get('status') & SC.Record.READY &&
            (this.getPath('readonlySelectedItem.status') & SC.Record.READY) &&
            this.didChangeFor('readonlySelectedItemCheck', 'readonlySelectedItem'))
            this.invokeNext(function() {
                Footprint.statechart.sendAction(
                    this.get('selectedItemDidChangeEvent'),
                    SC.Object.create({content: this.getPath('readonlySelectedItem')})
                );
            });
    }.observes('.status', '.readonlySelectedItem')
}

/***
 * Allows a controller to select all
 * @type {{}}
 */
Footprint.SelectAllSupport = {
    /***
     * Indicates that all items should be selected when YES
     */
    selectAll: NO,

    /***
     * Returns a SelectionSet with all items selected
     */
    fullSelection: function() {
        var selectionSet = SC.SelectionSet.create();
        if (!this.get('content'))
            // If no content is available just return an empty selection set
            return selectionSet;
        selectionSet.addObjects(this.get('content'));
        return selectionSet;
    }.property('content').cacheable(),

    /***
     * Returns the normal selection unless selectAll is YES,
     * in which case it returns the fullSelection while maintaining
     * the normal selection for when selectAll is NO
     * TODO this should delegate at some point sc_super to use selection_support.js functionality
     */
    selection: function(propKey, value) {
        if (value !== undefined && !this.get('selectAll'))
            // Set the internal selection to the value unless selectAll is true, in which case the value that comes
            // in could be the full selection
            this._selection = value;
        // Default the selection to the empty set on the first get
        this._selection = this._selection || SC.SelectionSet.create();
        // Always return the fullSelection when selectAll is true
        return this.get('selectAll') ?
            this.get('fullSelection') :
            this._selection;
    }.property('selectAll', 'fullSelection').cacheable()
};



Footprint.LayerStyleSelectionSupport = {
    selection: function(key, value) {
        var old = this._scsel_selection,
        oldlen = old ? old.get('length') : 0,
        empty,
        arrangedObjects = this.get('arrangedObjects'),
        len;

        // whenever we have to recompute selection, reapply all the conditions to
        // the selection.  This ensures that changing the conditions immediately
        // updates the selection.
        //
        // Note also if we don't allowSelection, we don't clear the old selection;
        // we just don't allow it to be changed.


        if ((value === undefined) || !this.get('allowsSelection')) { value = old; }

        ///Added check for IsStyle so selection doesn't update when style row is selected
        if (value && (value.getPath('firstObject.isStyle') || value.getPath('firstObject.isAttribute'))) {
            value = old;
        }

        len = (value && value.isEnumerable) ? value.get('length') : 0;

        // if we don't allow multiple selection
        if ((len > 1) && !this.get('allowsMultipleSelection')) {

          if (oldlen > 1) {
            value = SC.SelectionSet.create().addObject(old.get('firstObject')).freeze();
            len = 1;
          } else {
            value = old;
            len = oldlen;
          }
        }

        // if we don't allow empty selection, block that also, unless we
        // have nothing to select.  select first selectable item if necessary.
        if ((len === 0) && !this.get('allowsEmptySelection') && arrangedObjects && arrangedObjects.get('length') !== 0) {
          if (oldlen === 0) {
            value = this.get('firstSelectableObject');
            if (value) { value = SC.SelectionSet.create().addObject(value).freeze(); }
            else { value = SC.SelectionSet.EMPTY; }
            len = value.get('length');

          } else {
            value = old;
            len = oldlen;
          }
        }

        // if value is empty or is not enumerable, then use empty set
        if (len === 0) { value = SC.SelectionSet.EMPTY; }

        // always use a frozen copy...
        if(value !== old) value = value.frozenCopy();
        this._scsel_selection = value;

        return value;

  }.property('arrangedObjects', 'allowsEmptySelection', 'allowsMultipleSelection', 'allowsSelection').cacheable()
};
