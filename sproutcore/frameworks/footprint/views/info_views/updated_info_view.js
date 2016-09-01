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
 * Provides a check mark icon and label when something finishes
 */
Footprint.UpdatedInfoView = SC.View.extend({
    childViews: ['iconView', 'labelView'],
    classNames: ['updated-info-view'],

    title: 'Saved',
    iconView: SC.ImageView.extend({
        layout: { left:0, width:27, height:27, right: 30},
        useCanvas: NO,
        value: sc_static('footprint:images/check.png'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.isVisible')
    }),

    labelView: Footprint.LabelView.extend({
        layout: {left: 31, top: 5},
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        isVisibleBinding: SC.Binding.oneWay('.parentView.isVisible')
    })
});
