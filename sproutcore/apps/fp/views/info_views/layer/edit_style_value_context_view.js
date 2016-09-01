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
 * Edits a Footprint.StyleValueContext record
 */

sc_require('views/info_views/record_item_with_style_view');

Footprint.EditStyleValueContextView = Footprint.RecordItemWithStyleView.extend({
    classNames: ['footprint-style-value-context'],
    // The Footprint.StyleValueContextView
    content: null,
    // problems with binding this
    style: function() {
        return this.getPath('content.style');
    }.property(),

    // These unfortunately match with css-defined classes that
    // specify layout properties. TODO remove layout from all css!
    labelStyleClass: 'footprint-style-value-context-label',
    styleClass: 'footprint-style-value-context-color'
});
