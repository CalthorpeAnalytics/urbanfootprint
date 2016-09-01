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
 * FileSource represents the overall zip file being uploaded.
 * The datasets within it are each represented by a FileDataset.
 * Thus FileDataset can be thought of as showing the upload progress,
 * whereas FileDataset shows the progress of extracting each dataset
 */
Footprint.FileSource = Footprint.Record.extend({
    // The unique id of the Sproutcore file upload
    // This is only used to help the select the newest upload
    // in Footprint.fileSourcesController
    uuid: null,

    // The current progress of the upload
    progress: SC.Record.attr(Number),
    config_entity: SC.Record.toOne('Footprint.ConfigEntity'),
    // The name of the file
    file_name: SC.Record.attr(String),
    url: SC.Record.attr(String),

    // This flag is set as soon as we have at least one Footprint.FileDataset
    // It tells us not to display the Footprint.FileSoure anymore
    datasetsCreated: NO,

    /***
     * Generic name for the progress view
     */
    name: function() {
        return this.get('file_name');
    }.property('file_name').cacheable(),

    /***
     * A commonly-named property for sorting among Footprint.FileDatasets
     */
    orderId: function() {
        return this.get('id');
    }.property('id').cacheable()
});
