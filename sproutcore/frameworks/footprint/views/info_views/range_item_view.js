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

sc_require('views/info_views/info_view');

Footprint.RangeItemView = Footprint.InfoView.extend({
    classNames:'footprint-range-item-view'.w(),

    value:null,
    rangeValue:null,
    contentStatus:null,
    contentStatusBinding:SC.Binding.oneWay('*content.status'),

    init: function() {
        sc_super();
        // Bind value to the attribute {value} property
        this.bind('value', this, this.get('attribute'));
        // Bind rangeValue to the attribute {value}__range property
        this.bind('rangeValue', this, "%@__range".fmt(this.get('attribute'))).oneWay();
    }
});
