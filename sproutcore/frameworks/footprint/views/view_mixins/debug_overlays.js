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

__author__ = 'calthorpe_analytics'

sc_require('views/view_mixins/debug_binding_overlay');
sc_require('views/view_mixins/debug_view_hierarchy_overlay');

Footprint.DebugOverlays = {
    _overlayMixins: [
        Footprint.DebugBindingOverlay,
        Footprint.DebugViewHierarchyOverlay
    ],

    keyDown: function(evt) {
        sc_super();
        this._overlayMixins.forEach(function(overlay_mixin) {
            overlay_mixin.keyDown(evt);
        });
    },
    keyUp: function(evt) {
        sc_super();
        this._overlayMixins.forEach(function(overlay_mixin) {
            overlay_mixin.keyUp(evt);
        });
    }
};
