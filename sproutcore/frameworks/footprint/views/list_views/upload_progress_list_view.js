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


sc_require('views/upload_progress_overlay_view');

/***
 * Tracks the progress of Footprint.FileSources or the Footprint.Datasets of a Footprint.FileSource
 * The FileSource are included until at least one Dataset is in the store, at which point only
 * the Datasets are included.
 */
Footprint.UploadProgressListView = SC.ScrollView.extend({
    layerId: 'progress-list-view',
    classNames: ['progress-list-view'],
    content: null,
    contentBinding: SC.Binding.oneWay('.parentView.content'),
    selection: null,
    selectionBinding: SC.Binding.from('.parentView.selection'),

    contentView: SC.SourceListView.extend({
        layout: {top: 0},
        classNames: ['progress-list-content-view'],
        rowHeight: 40,
        actOnSelect: NO,
        canReorderContent: NO,
        showAlternatingRows: YES,
        contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),
        selectionBinding: SC.Binding.from('.parentView.parentView.selection'),
        exampleView: Footprint.UploadProgressOverlayView
    })
});
