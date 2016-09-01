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


/***
 * Represents one of the datasets of a FileDataset.
 */
Footprint.FileDataset = Footprint.Record.extend({

    // The FileSource of the FileDataset
    file_source: SC.Record.toOne(Footprint.FileSource),
    // The current progress of the upload
    progress: SC.Record.attr(Number),
    // This is the key of the DbEntity that gets created on the client
    // We can't use the DbEntity directly because their are nested store id problems
    db_entity_key: SC.Record.attr(String),
    // The name of the dataset file within the upload file
    file_name: SC.Record.attr(String),
    // The friendly name of the file, used to name the DbEntity
    name: SC.Record.attr(String),
    url: SC.Record.attr(String),

    /***
     * A commonly-named property for sorting among Footprint.FileSources
     */
    orderId: function() {
       return this.getPath('file_source.id');
    }.property('file_source').cacheable()
});
