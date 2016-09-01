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



Footprint.developerModeController = SC.Object.create({
    /**
     * Initialize the developerModeController based on a URL.
     * @param {Location} location window.location, or a similar object.
     * Avaialble options thus far are:
     *  traceStatechart: Sets Footprint.statechart.trace
     */
    loadFromUrl: function(location) {
        var paramList = [];
        var params = location.search;
        if (params && params[0] == '?') {
            params = params.split('?')[1];
            paramList = params.split('&').map(function(kv) {
                return kv.split('=', 2);
            });

            paramList.forEach(function(kv) {
                var key = kv[0].camelize();
                var value = kv[1];
                this.set(key, value);
            }, this);

        }
    },

    // A wrapper around window.location/window.history to allow in-place reloads.
    navigateTo: function(url, key, replace) {
        if (replace) {
            window.history.replaceState({}, key, url);
            // Since the url changed but we didn't reload, we need to re-parse the new url.
            this.loadFromUrl(window.location);
        } else {
            window.location = url;
        }
    },
});
