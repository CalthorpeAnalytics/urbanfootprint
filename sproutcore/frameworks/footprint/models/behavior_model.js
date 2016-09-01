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


sc_require('models/key_mixin');
sc_require('models/name_mixin');
sc_require('models/tags_mixin');
sc_require('models/deletable_mixin');

Footprint.Behavior = Footprint.Record.extend(Footprint.Key, Footprint.Name, Footprint.Tags, Footprint.Deletable, {
    /***
     * This is used by the Footprint.Key mixin to form the key corresponding to the Name
     * Behavior keys always prefix 'behavior__'
     */
    keyPrefix:'behavior',
    parents: SC.Record.toMany('Footprint.Behavior'),
    intersection: SC.Record.toOne('Footprint.Intersection'),
    // All tags of the behavior and its parents
    computed_tags: SC.Record.toMany(Footprint.Tag, {nested:true, isMaster:YES}),
    readonly: SC.Record.attr(Boolean),
    abstract: SC.Record.attr(Boolean),
    matchesSimpleKey: function(simpleKey) {
        return this.get('key') == '%@__%@'.fmt(this.get('keyPrefix'), simpleKey);
    }
});
