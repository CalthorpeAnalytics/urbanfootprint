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


Footprint.Key = {
    key:SC.Record.attr(String),
    keyProperty: 'key',
    /***
     * Default NO. Set to YES to make the key always mimic the name, not just when the record is new
     */
    alwaysUpdateName: NO,
    /***
     * Default YES. Set to YES to apply a timestamp to keys of new records. This prevents duplicate
     * keys on the frontend and backend
     */
    applyKeyTimestampToNewRecords: YES,

    nameObserver: function(record, attr) {
        // Keys are bound to a slugified name when new
        // For now only update the key if the record is new.
        // Updating the key on existing records is problematic, since it's a sort of id. Although this should work someday
        var newStatus = this.get('status') === SC.Record.READY_NEW;
        if (this.get('attributes') && (
            newStatus || (this.get('alwaysUpdateName') && (this.get('status') & SC.Record.READY))) &&
            this.didChangeFor('nameObserverCheck', 'name', 'status')
        ) {
            key = '%@%@%@'.fmt(
                // apply a keyPrefix if the recordType has one
                this.get('keyPrefix') || '',
                // dasherize the name to create the key and limit it to 10 characters.
                // The limit is needed for ConfigEntities since the key is used to form the database schema, which has
                // a limitation of 64 characters. We might only limit ConfigEntity keys to 10 characters, but its helpful
                // to limit other classes as well in case the user creates a very long name, and there's no harm in
                // a truncated key since we add a timestamp to the end.
                (this.get('name') || '').dasherize().replace(/-/g, '_').slice(0, 10),
                // If the flag is YES and the record new create a unique timestamp to apply to the end of the key
                newStatus && this.get('applyKeyTimestampToNewRecords') ? '_%@'.fmt(SC.DateTime.createTimestamp()) : ''
            );
            this.setIfChanged(this.get('keyProperty'), key.substr(0,50));
        }
    }.observes('.name', '.status')
};
