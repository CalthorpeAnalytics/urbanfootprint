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
 * Edits a Footprint.Style record
 */
Footprint.EditStyleView = Footprint.RecordItemWithStyleView.extend({
    classNames: ['footprint-style'],
    layout: {width: 60, right: 0},
    // The Footprint.StyleValueContextView
    content: null,
    style: function() {
        return this.get('content');
    }.property(),

    // These unfortunately match with css-defined classes that
    // specify layout properties. TODO remove layout from all css!
    labelStyleClass: 'footprint-style-label',
    styleClass: 'footprint-style-color'
});
