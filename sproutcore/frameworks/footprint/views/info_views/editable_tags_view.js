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


sc_require('views/info_views/editable_associated_list_view');

/***
 * Provides a view that lists the current tags of a record and allows the user to add existing system-wide
 * tags to that record or define new tags
 */
Footprint.EditableTagsView = Footprint.EditableAssociatedListView.extend({

    classNames: ['footprint-editable-tags-view'],

    title: 'DMUI.Tags',

    itemTitleKey: 'tag',
    selectionAction: 'doPickTag',
    addAction: 'doAddTag',
    removeAction: 'doRemoveTag',
    emptyTitle: 'DMUI.ChooseOrCreateTags'
});
