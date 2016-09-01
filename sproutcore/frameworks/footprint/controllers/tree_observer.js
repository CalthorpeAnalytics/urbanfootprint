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

Footprint.TreeObserver = {

    /*
     * The property of leaf that resolves keyObject that matches one of keyObjects. This attribute hold a single
     * item or a collection. The keyProperty, keyProperty status and keyProperty [] (if it's a collection)
     * of each leaf is dynamically observed in case the value or an item in the value's collection changes
     */
    keyProperty: null,

    // The leaves of the tree.
    leaves: null,

    // Override if you need the observer to call propertyDidChange on something else
    treeProperties: ['treeItemChildren'],

    /***
     * Update the tree if the leaves change
     * Also add/remove observers for each leaf's keyProperty item(s) so we know if any of those values change
     */
    observeNodes: function () {
        var leaves = this.get('leaves');
        // Remove observers for any removed leaves
        if (this._previousLeaves) {
            this._previousLeaves.forEach(function (leaf) {
                if (!(leaves || []).contains(leaf))
                    SC.ObservableExtensions.removePropertyItemsAndStatusObservation(
                        'leafKeyPropertyObserving',
                        leaf,
                        this.get('keyProperty'),
                        this,
                        'treeNeedsUpdate');
            }, this);
        }

        // Add observers for any new leaves
        (this.get('leaves') || []).forEach(function (leaf) {
            if (!this._previousLeaves || !this._previousLeaves.contains(leaf))
                SC.ObservableExtensions.propertyItemsAndStatusObservation(
                    'leafKeyPropertyObserving',
                    leaf,
                    this.get('keyProperty'),
                    this,
                    'treeNeedsUpdate');
        }, this);
        this._previousLeaves = this.get('leaves');
        // Call this assuming the leaves changed
        this.treeNeedsUpdate();
    }.observes('.leaves', '*leaves.status', '*leaves.[]', '.keyProperty'),

    treeNeedsUpdate: function () {
        this.invokeOnce(this._treeNeedsUpdate);
    },

    _treeNeedsUpdate: function() {
        this.get('treeProperties').forEach(function(property) {
            this.notifyPropertyChange(property);
        }, this);
    }
};
