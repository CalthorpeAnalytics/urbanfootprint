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

sc_require('views/item_views/item_view');

/**
 *
 * Displays a layer group name as the item of a list by binding content to a Footprint.TreeItem or similar
 */
Footprint.LayerGroupItemView = SC.ListItemView.extend(SC.ContentDisplay, {
    contentValueKey: 'name',
    contentUnreadCountKey: 'count',
    contentDisplayProperties: ['name']

    //render: function(context) {
    //    var title = this.getPath('content.name') || '';
    //    title = title.titleize();
    //    var themeClassNames = this.getPath('theme.classNames');
    //    context = context.begin()
    //                     .addClass(themeClassNames)
    //                     .addClass(['sc-view', 'footprint-layer-group-view']);
    //
    //    context.begin()
    //           .addClass(themeClassNames)
    //           .addClass(['sc-view', 'footprint-layer-group-label-view'])
    //           .push(title)
    //           .end();
    //
    //    context = context.end();
    //},
    //
    //update: function($context) {
    //    var title = this.getPath('content.name') || '';
    //    title = title.titleize();
    //    $context.find('.footprint-layer-group-label-view').text(title);
    //}
});
