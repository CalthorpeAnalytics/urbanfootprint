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


SC.ChildArray.reopen({

    refresh: function() {
        var record = this.get('record');
        if (record) record.refresh();
    },

    status: null,
    statusBinding: SC.Binding.oneWay('*record.status'),

    createNestedRecord: function(recordType, attributes) {
        this.pushObject(attributes);
        return this.get('lastObject');
    },

    /***
     * Matches the interface of SC.RecordArray to support SC.SparseArrays.
     * This implementation simply does the same thing as map, since SC.ChildArrays
     * never use by SC.SparseArrays.
     * @param func
     * @param target
     */
    mapLoadedRecords: function(func, target) {
        return this.map(func, target);
    }
});
