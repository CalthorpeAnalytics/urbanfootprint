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


sc_require('views/info_views/select_or_add_info_view');

/***
 * Displays the main and join table columns available for use
 * in filters, aggregates, and group by
 * @type {*|RangeObserver|Class|void}
 */
Footprint.JoinColumnsInfoView = Footprint.SelectOrAddInfoView.extend({
    classNames:['footprint-query-info-join-columns-view'],
    includeNullItemIfEmpty: YES,
    nullTitleIfEmpty: 'No matches',
    // Make the input area a text area instead of a single line
    isTextArea: NO,
    // We just need to select from the list, so no add button is needed
    showAddButton: NO,
    // By default the user can select a value. If we are just displaying read-only values, set to NO
    isSelectable:YES,
    // This shows if the selection is empty
    nullTitle: function() {
        return this.get('isSelectable') ?
            'Select' :
            'View';
    }.property('isSelectable').cacheable(),
    // Primitives get their title from the content
    itemTitleView: 'content',
    menuWidth: function() {
        return this.getPath('frame.width');
    }.property('frame').cacheable(),

    toolTip: 'Select From Eligible Columns',
    recordType:null,
    icon: null,
    maxHeight: 300,

});
