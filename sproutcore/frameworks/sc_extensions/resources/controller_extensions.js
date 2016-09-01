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

SC.Controller.reopen({
    /***
     * Adds the ability to quickly dump fields and properties for debugging.
     * content isn't technically defined on SC.Controller but I assume callers will be extending SC.Object or SC.Array
     * @returns {*}
     */
    dump: function() {
        return "content: %@".fmt(this.get('content'));
    }
});

SC.ArrayController.reopen({
  status: function() {
    var content = this.get('content'),
        ret = content ? content.get('status') : null;
    return ret ? ret : SC.Record.EMPTY;
  }.property().cacheable()
});
