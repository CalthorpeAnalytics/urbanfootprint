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


Footprint.User = Footprint.Record.extend({
    // This is always an email address
    username: SC.Record.attr(String),
    first_name: SC.Record.attr(String),
    last_name: SC.Record.attr(String),
    api_key: SC.Record.attr(String),
    groups: SC.Record.toMany("Footprint.Group", {inverse: 'users', isMaster: YES}),
    name: function() {
        return '%@ %@'.fmt(this.get('first_name'), this.get('last_name'));
    }.property('first_name' ,'last_name').cacheable(),

    /***
     * We assume all users are of a single group for now
     * @param propKey
     * @param value
     */
    singleGroup: function(propKey, value) {
        if (value !== undefined) {
            if (value != this.getPath('groups.firstObject')) {
                this.get('groups').clear();
                this.get('groups').pushObject(value);
            }
        }
        return this.getPath('groups.firstObject');
    }.property('groups').cacheable(),

    // this observer will force loading of this.groups, and in turn tickle the
    // isManager property.
    groupNameObserver: function() {
        this.set('firstGroupName', this.get('groups.firstObject.name'));
    }.observes('groups.firstObject.name'),

    firstGroupName: null,

    isManager: function() {
        var groupNames = this.get('groups').getEach('name');
        return groupNames.some(function(name) {
          return (name.indexOf('superadmin') != -1 ||
                  name.indexOf('admin') != -1 ||
                  name.indexOf('manager') != -1);
      });
    }.property('groups', 'firstGroupName'),
});
