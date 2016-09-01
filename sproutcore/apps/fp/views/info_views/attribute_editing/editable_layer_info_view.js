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


Footprint.EditableLayerInfoView = SC.View.extend({
    childViews: ['layerView', 'userView', 'recordsView'],
    backgroundColor: 'lightgrey',
    title: null,
    content: null,

    layerView: SC.View.extend({
        childViews: ['layerTitleView', 'layerNameView'],
        layout: {height: 38},
        title: null,
        titleBinding: SC.Binding.oneWay('.parentView.title'),

        layerTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 5, height: 16, top: 5, width: 70},
            value: 'Layer:'
        }),
        layerNameView: SC.LabelView.extend({
            classNames: ['footprint-active-built-form-name-view', 'toolbar'],
            layout: {height: 16, top: 20},
            textAlign: SC.ALIGN_CENTER,
            valueBinding: '.parentView.title'
        })
    }),

    userView: SC.View.extend({
        childViews: ['userTitleView', 'userNameView'],
        layout: {height: 16, top: 40, width: 100},
        userTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 5, height: 16, top: 5, width: 25},
            value: 'User:'
        }),
        userNameView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 30, height: 16, top: 5, width: 70},
            valueBinding: SC.Binding.oneWay('Footprint.userController.content.firstObject.username').transform(function(user) {if (user) {return user.capitalize();}})
        })
    }),

    recordsView: SC.View.extend({
        childViews: ['recordsTitleView', 'recordsNumberView'],
        layout: {height: 16, top: 40, left: 100},
        content: null,
        contentBinding: SC.Binding.oneWay('.parentView.content'),

        recordsTitleView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 5, height: 16, top: 5, width: 80},
            value: 'Selected Records:'
        }),
        recordsNumberView: SC.LabelView.extend({
            classNames: ['footprint-editable-9font-title-view'],
            layout: {left: 87, height: 16, top: 5, width: 35},
            status: null,
            statusBinding: '*content.status',
            content: null,
            contentBinding: SC.Binding.oneWay('.parentView.content'),

            value: function() {
                var length = 0;
                var status = this.get('status');
                if (status & SC.Record.READY || status === SC.Record.EMPTY) {
                    length = this.getPath('content.length') || 0;
                }
                return length;
            }.property('content', 'status').cacheable()
        })
    })
});
