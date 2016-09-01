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

sc_require('system/array_status');

SC.ManyArray.reopen(SC.ArrayStatus, {

    refresh: function() {
      var length = this.get('length');
      for (i = 0; i < length; i++) {
          var record = this.objectAt(i);
          record.refresh();
      }
    },

    toString: function() {
      return sc_super() + "\n---->" +
          this.map(function(item) {
              return item.toString()
          }, this).join("\n---->");
    }
});
