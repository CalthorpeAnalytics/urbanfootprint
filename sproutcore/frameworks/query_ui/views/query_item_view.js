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

QueryUI.QueryItemView = SC.View.extend({

    childViews: ['removeButton', 'duplicateButton'],

    displayProperties: ['matchedCurrentQuery'],

    // Binding within item views is frowned upon, but in this case we expect few item views
    // and the complex relationship of the item view to the current query requires this kind of
    // connection.
    currentQuery: null,
    currentQueryBinding: SC.Binding.oneWay('QueryUI.queryController.content'),

    matchedCurrentQuery: function () {
        var content = this.get('content'),
            currentQuery = this.get('currentQuery'),
            ret = false;

        if (content && currentQuery && content !== currentQuery) {
            ret = content.get('layer') === currentQuery.get('layer');
        }

        return ret;
    }.property('content', 'currentQuery'),

    render: function (context) {
        var content = this.get('content'),
            matchedCurrentQuery = this.get('matchedCurrentQuery');

        // The chainable dot.
        context = context.begin().addClass('qiv-chain-dot');
        if (matchedCurrentQuery) {
            context.addClass('and-can-chain');
        }
        context = context.end();

        // The name.
        context = context.begin().addClass('qiv-title');
        if (content) {
            context.push(content.get('name'));
        }
        context = context.end();
    },

    removeButton: SC.ImageButtonView.extend({
        action: 'deleteQuery',
        image: '',
        layout: { height: 20, width: 20, right: 10, centerY: 0 },
        target: QueryUI
    }),

    duplicateButton: SC.ImageButtonView.extend({
        action: 'deleteQuery',
        image: '',
        layout: { height: 20, width: 20, right: 30, centerY: 0 },
        target: QueryUI
    }),

});
