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

SC.RecordArray.reopen({

    /***
     * For SparseArrays, maps only those records that are loaded
     * The function is called with the object at each defined index
     * as well as the index as a second arg
     */
    mapLoadedRecords: function(func, target) {
        var storeKeys = this.get('storeKeys') || [];
        return storeKeys.kindOf && storeKeys.kindOf(SC.SparseArray) ?
            storeKeys.definedIndexes().map(function(index) {
                var obj = this.objectAt(index);
                return func.apply(target || this, [obj, index]);
            }, this) :
            this.map(func, target);
    },

    /***
     * Delegates to the sparse array to get the loaded number of records.
     */
    loadedCount: null,
    loadedCountBinding: SC.Binding.oneWay('*storeKeys.loadedCount'),

    /**
     * Given a Sproutcore object and list of its attributes, returns a dict keyed by attribute and valued by a toString of the attribute value
     * Useful for debugging
     */
    toString: function() {
        return '%@:[\n--->%@ Total Records: %@'.fmt(sc_super(), this.get('count'), this.mapLoadedRecords(function(item) {
            return item && item.get('id');
        }).join('\n--->'))+'\n]';
    }
});
