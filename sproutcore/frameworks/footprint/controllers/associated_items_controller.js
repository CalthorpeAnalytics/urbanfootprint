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


sc_require('controllers/controllers.js');
sc_require('controllers/search_filter_mixin.js');

Footprint.AssociatedItemsController = Footprint.ArrayController.extend(Footprint.SearchFilterMixin, {
    /***
     * Properties of the associated record type to use for search filtering
     */
    searchProperties: [],
    allowsEmptySelection:YES,
    /***
     * The toMany items to view/edit
     */
    associatedItems: null,
    /***
     * The selection is set to the currently associatedItems if we are changing the associated items
     * based on all the available items. However we don't want to set the selection if we have a separate
     * list displaying the associatedItems, in that case just want to use this selection for temporarily
     * selecting an item from all items to add to the associatedItems
     */
    selectionIsAssociatedItems: NO,

     // If the associated items change, update the selection, but only if selectionIsAssociatedItems is YES
    _selectionUpdater: function() {
        if (this.get('selectionIsAssociatedItems')) {
            this.selectObjects(this.get('associatedItems'));
        }
    }.observes('.associatedItems'),

    // If the selection changes, update the associatedItems, but only if selectionIsAssociatedItems is YES
    _associatedItemsUpdater: function() {
        if (this.get('selectionIsAssociatedItems') && this.get('associatedItems')) {
            var associatedItems = SC.Set.create(this.get('associatedItems'));
            var selection = this.get('selection');
            // Make sure the selection hasn't been cleared by a content change
            if (!selection.get('length')) {
                this.selectObjects(this.get('associatedItems'));
                selection = this.get('selection');
            }
            if (!associatedItems.equals(selection)) {
                this.get('associatedItems').removeObjects(associatedItems.subtract(selection));
                this.get('associatedItems').pushObjects(selection.subtract(associatedItems));
            }
        }
    }.observes('.selection'),

    /***
     * All items available for the associatedItems to be
    */
    allItems: null,
    filteredItemsProperties: ['allItems'],
    // Binding the content to the current filtering of items
    contentBinding: SC.Binding.oneWay('.filteredItems'),
    status: null,
    statusBinding: SC.Binding.oneWay('*allItems.status'),
    orderBy: ['value ASC'],

    associatedItemsDidUpdate: function() {
        this.propertyDidChange('additionalFilter')
    }.observes('*associatedItems.[]'),

    /***
     * Extend the search filter to also filter out the items that are already associated
     */
    additionalFilter: function () {
        var items = (this.get('associatedItems') || []);
        return function(item) {
            return !items.contains(item);
        }
    }.property('associatedItems').cacheable()
});
