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

Footprint.ControllerMixins = {
    /**
     * Denotes if the data source is ready
     */
    isReady: function() {
        var status = this.get('status');
        return status & SC.Record.READY;
    }.property('status').cacheable(),

    /**
     * Provides a summary of the status of the controller.
     */
    summary: function() {
        var ret = '';

        var status = this.get('status');
        if (status & SC.Record.READY) {
            var len = this.get('length');
            if (len && len > 0) {
                ret = len === 1 ? "1 item" : "%@ items".fmt(len);
            } else {
                ret = "No items";
            }
        }
        if (status & SC.Record.BUSY) {
            ret = "Loading..."
        }
        if (status & SC.Record.ERROR) {
            ret = "Error"
        }
        return ret;
    }.property('length', 'status').cacheable()
};
