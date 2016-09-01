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

/**
 * A Mixin to identify the child items of each Policy, PolicySet or PolicyCategory for tree display
 * @type {Object}
 */
Footprint.PolicyTreeItemChildren = {
    treeItemIsExpanded: YES,
    treeItemChildren: function(){
        return this.get("policies");
    }.property()
};

Footprint.Policy = Footprint.Record.extend(
    Footprint.Key,
    Footprint.Name,
    Footprint.Tags,
    Footprint.PolicyTreeItemChildren, {

    value:SC.Record.attr(Number),
    policies: SC.Record.toMany("Footprint.Policy", {
        isMaster:YES
    }),
    _copyProperties: function() { return 'policies'.w(); }
});



Footprint.PolicySet = Footprint.Record.extend(
    Footprint.Key,
    Footprint.Name,
    Footprint.PolicyTreeItemChildren, {

    policies: SC.Record.toMany("Footprint.Policy", {
        nested: true,
        isMaster:YES
    }),
    _copyProperties: function() { return 'policies'.w(); }
});
