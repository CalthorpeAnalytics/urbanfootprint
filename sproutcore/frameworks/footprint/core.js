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

sc_require('resources/d3.v3.js');

// ==========================================================================
// Project:   Footprint
// ==========================================================================
/*globals Footprint */

/** @namespace

 UrbanFootprint is one cool app.  Described as anything we want it to be.

 @extends SC.Object
 */
window.F = window.Footprint = SC.Application.create(
    /** @scope Footprint.prototype */ {

        NAMESPACE: 'Footprint',
        VERSION: '0.1.0',


        // Here is the server connector that replaces the fixtures connector
        store: SC.Store.create({
            commitRecordsAutomatically: NO,
            _autonomousStore: null,
            /***
             * The singleton AutonomousStore. This instance should be shared as much as possible
             * so that edited records are all in the same store. If necessary a separate
             * AutonomousStore can be created, but there are limited cases for it.
             * When a state finishes or edits or discards changes, it should reset the store.
             * This assumes that edits are isolated to one panel at a time. If changes need
             * to be done simultaneously then multiple autonomous stores should be created
             */
            autonomousStore: function() {
                return this.chainAutonomousStore();
            }.property().cacheable(),
        }).from('Footprint.DataSource')
    });

// Create a path to static content with a wildcard in it. socket.io.js is just used because it's in the resources
// For some reason SC doesn't just offer the path
Footprint.STATIC_FW = sc_static('socket.io.js').replace('socket.io.js','%@');
Footprint.VISIBLE = 'visible';
Footprint.HIDDEN = 'hidden';
Footprint.SOLO = 'solo';

// The maximum features to draw on the leaflet map. If we try to draw
// more, the map tends to crash the browser.
Footprint.MAX_MAP_VECTOR_FEATURES = 5000;
