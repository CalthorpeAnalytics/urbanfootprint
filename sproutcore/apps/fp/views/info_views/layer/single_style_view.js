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


sc_require('views/info_views/layer/layer_style_picker_view');

Footprint.SingleStyleView = SC.View.extend({
    childViews: ['titleView', 'stylePickerView'],
    content: null,
    contentBinding: SC.Binding.from('Footprint.styleValueContextsEditController*selection.firstObject'),
    status: null,
    statusBinding: SC.Binding.oneWay('*content.status'),
    isEnabledBinding: SC.Binding.oneWay('.parentView.isEnabled'),

    titleView: SC.LabelView.extend({
        classNames: ['footprint-editable-12font-bold-title-view'],
        layout: {left: 5, width: 110, height: 16, top: 30},
        value: 'Style Options:'
    }),

    stylePickerView: Footprint.LayerStylePickerView.extend({
        layout: { right: 20, height: 130, left: 10, top: 60},
        styleBinding: SC.Binding.from('.parentView*content.style')
    })
});
