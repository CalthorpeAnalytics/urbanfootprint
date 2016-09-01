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

Footprint.ReadonlyDescriptionView = Footprint.InfoView.extend({
    childViews: ['titleView', 'contentView'],

    titleView: Footprint.LabelView.extend({
        classNames: 'footprint-infoview-title-view'.w(),
        layout: {top: 0 , height: 24},
        valueBinding: '.parentView.title'
    }),

    contentView: Footprint.LabelView.extend({
        classNames: ['footprint-uneditable-content-view'],
        layout: {top: 24},
        isTextArea: YES,
        isEditable: NO,
        // TODO hopefully all three of these can be set without conflicting
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        valueBinding: SC.Binding.oneWay('.parentView.value'),
        hint: ''
    })
});
