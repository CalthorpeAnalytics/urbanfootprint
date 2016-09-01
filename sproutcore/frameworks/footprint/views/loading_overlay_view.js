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


Footprint.LoadingOverlayView = SC.View.extend({
    childViews:['imageView', 'labelView'],
    classNames: ['overlay-view'],
    isVisible: NO,
    showLabel: NO,
    title: null,

    imageView: SC.ImageView.extend({
        layout: { centerX:0, centerY:0, width:24, height:24, zIndex: 1111},
        useCanvas: NO,
        value: sc_static('footprint:images/spinner24.gif')
    }),

    labelView: SC.LabelView.extend({
        classNames: ['footprint-editable-12font-bold-title-view'],
        layout: { centerX: 0, centerY: 30, left: 20, right: 20, height:16},
        isVisibleBinding: SC.Binding.and('.parentView.isVisible', '.parentView.showLabel'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        textAlign: SC.ALIGN_CENTER
    })
});
