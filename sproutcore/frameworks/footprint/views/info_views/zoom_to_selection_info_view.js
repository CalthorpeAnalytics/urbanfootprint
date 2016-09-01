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


Footprint.ZoomToSelectionView = SC.View.extend({
    classNames: "footprint-zoom-to-selection-view".w(),
    childViews: ['zoomToSelectionLabelView', 'zoomToSelectionButtonView'],
    action: null,
    title: null,
    toolTip: null,
    zoomToSelectionLabelView: SC.LabelView.extend({
        classNames: 'footprint-map footprint-map-rezoom-to-extent-label'.w(),
        layout: { height: 16, width: 150, right: 2, top: 4},
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),
    zoomToSelectionButtonView: SC.ButtonView.extend({
        classNames: 'footprint-map footprint-map-rezoom-to-extent-button'.w(),
        layout: { height: 24, width: 20, right: 0},
        icon: sc_static('footprint:images/zoom_to_extent.png'),
        actionBinding: SC.Binding.oneWay('.parentView.action'),
        toolTipBinding: SC.Binding.oneWay('.parentView.toolTip')
    })
});
