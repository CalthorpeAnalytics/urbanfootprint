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


sc_require('models/presentation_models');

/***
 * The API delivers presentations by type so that we don't have to deal with mixed inheritance in a flat list
 * TODO We should make the map presentations of type Map and abstract Presentation (both here and on the server)
 * @type {{maps: (SC.ManyAttribute|SC.ChildrenAttribute), results: (SC.ManyAttribute|SC.ChildrenAttribute)}}
 */

Footprint.PresentationTypes = Footprint.Record.extend({
    _internal:YES,
    layers: SC.Record.toMany('Footprint.LayerLibrary', {
        isMaster:YES
    }),
    results: SC.Record.toMany('Footprint.ResultLibrary', {
        isMaster:YES
    }),
    _cloneProperties: function() { return 'layers results'.w(); }
});
