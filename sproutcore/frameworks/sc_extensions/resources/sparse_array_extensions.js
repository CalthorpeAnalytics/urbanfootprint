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


SC.SparseArray.reopen({

    /***
     * Override to reliably set loadedCount
     * @param start
     */
    rangeRequestCompleted: function(start) {
        var i = this.wasRangeRequested(start);
        if(i>=0) {
            this.requestedRangeIndex.removeAt(i,1);
            this.set('loadedCount', this.definedIndexes().get('length'));
            return YES;
        }
        return NO;
    },

    /***
     * The number of loaded records. Set by definedIndexes
     */
    loadedCount: null,

    portionLoaded: function() {
        return (this.get('loadedCount') || 0) / (this.get('length') || 1)
    }.property('loadedCount', 'length').cacheable(),

    /***
     * Indicates if the SparseArray is fully loaded
     */
    isCompletelyLoaded: function() {
        return this.get('loadedCount') == this.get('length');
    }.property('loadedCount', 'length').cacheable(),

    /***
     * Starts loads the next missing index. Logs an error if nothing to load is found
     */
    loadNext: function() {
        var definedIndexes = this.definedIndexes();
        if (definedIndexes.max-definedIndexes.min()==this.get('loadedCount')) {
            // Easy normal case. Just load the max index, which represented the
            // next unloaded index. objectAt kicks off the next load
            this.objectAt(definedIndexes.max);
        }
        else {
            // Some intermediate indexes aren't loaded, find the first unloaded index
            for (var i=0; i<definedIndexes.max; i++) {
                if (!this.objectAt(i, true)) {
                    this.objectAt(i);
                    break;
                }
            }
            if (i==definedIndexes.max) {
                throw Error("No missing indexes found to load for this. Length: %@. Loaded indexes: %@".fmt(
                    this.get('length'),
                    definedIndexes.map(function(i) {return i;}).join(',')
                ))
            }
        }
    }
});
