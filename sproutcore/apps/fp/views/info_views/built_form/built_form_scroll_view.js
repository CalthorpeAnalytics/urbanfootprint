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


Footprint.BuiltFormScrollView = SC.ScrollView.extend({
    media: null,
    selection: null,
    content: null,

    contentView: SC.SourceListView.extend({
        isEnabledBinding: SC.Binding.oneWay('.content').bool(),
        rowHeight: 20,
        actOnSelect: NO,
        // Dummy value. We just need to tell the view that we have an icon so it calls our renderIcon
        contentIconKey: 'medium',
        contentValueKey: 'name',

        selection: null,
        selectionBinding: SC.Binding.from('.parentView.parentView.selection'),

        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.parentView.content'),

        groupExampleView: SC.View.extend(SC.ContentDisplay, {
            contentDisplayProperties: ['name'],
            render: function(context) {
                context = context.begin()
                       .addClass(['sc-view', 'footprint-built-form-group-view'])
                       .addClass(this.getPath('theme.classNames'));
                context.begin()
                       .addClass(['sc-view', 'footprint-built-form-group-label-view'])
                       .addClass(this.getPath('theme.classNames'))
                       .push(this.getPath('content.name'))
                       .end();
                context.end();
            },
            update: function($context) {
                $context.find('.footprint-built-form-group-label-view').text(this.getPath('content.name'));
            }
        }),
        /***
         * Displays a BuiltForm name with its style
         */
        exampleView: Footprint.RecordItemWithStyleView.extend({
            classNames: ['footprint-built-form-item'],

            styleClass: 'footprint-medium-color',
            labelStyleClass: 'footprint-built-form-item-label-view',

            // The BuiltForm has a convenient computed property to access the id Style
            styleBinding: SC.Binding.oneWay('*content.idStyle')
        })
    })
});
