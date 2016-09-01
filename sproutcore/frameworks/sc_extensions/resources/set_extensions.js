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


var extensions = {
    /***
     * Create a new set that contains items in this set minus the given set
     * @param anotherSet
    */
    subtract: function(anotherSet) {
        return SC.Set.create(this.filter(function(item) {
            return !anotherSet.contains(item)
        }))
    },

    /***
     * Returns true if the contents of this set equal that of the given set
     * @param anotherSet: The set to test against
     * @returns {*|Boolean|boolean}
     */
    equals: function(anotherSet) {
        return (anotherSet.get('length')==this.get('length')) && this.every(function(item) {
            return anotherSet.contains(item);
        })
    }
};
SC.Set = $.extend(SC.Set, extensions);
SC.SelectionSet.reopen(extensions);
