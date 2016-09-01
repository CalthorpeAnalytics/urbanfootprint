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

sc_require('controllers/search_filter_mixin');

 /***
  * Specialized TreeController that takes a Footprint.TreeContent for its ontent
  * @type {Class}
  */
Footprint.TreeController = SC.TreeController.extend(Footprint.SingleSelectionSupport, SC.CollectionViewDelegate, {
    treeItemIsGrouped: YES,
    allowsMultipleSelection: NO,
    allowsEmptySelection: NO,

    // Delegate the status to the leaves property of the content to get a status
    // The status is used by Footprint.SelectController to know they can assign their content to the selected item
    // or else first item of the leaves list
    statusBinding:SC.Binding.oneWay('*leaves.status'),

    /***
     * Returns the record type
     */
    recordType: function() {
        return this.getPath('leaves.firstObject.constructor');
    }.property('.leaves'),

	toString: function() {
	    return this.toStringAttributes('content'.w());
	},

    /***
     * Deals with a bug in SC.TreeItemObserver where the expandedState is set to closed if the treeItemChildren
     * are not immediately present. We assume that the root element is never displayed and thus should
     * always be expanded here when the treeItemChildren exist
     */
    treeItemChildrenObserver: function () {
        if (this.getPath('content.treeItemChildren')) {
            var arrangedObjects = this.get('arrangedObjects');
            if (arrangedObjects) {
                this.setPath('treeItemIsExpanded', YES);
            }
        }
    }.observes('*content.treeItemChildren', 'arrangedObjects')

});
