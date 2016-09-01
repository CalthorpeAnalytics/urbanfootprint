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


sc_require('views/editable_model_string_view');
sc_require('views/info_views/info_view');
sc_require('views/info_views/range_item_view');

Footprint.EditableStringView = Footprint.InfoView.extend({
    classNames:'footprint-editable-string-view'.w(),
    value:null,
    contentStatus:null,
    contentStatusBinding:SC.Binding.oneWay('*content.status'),

    contentView: Footprint.EditableModelStringView.extend({
        layout: {width:.99, height: 0.99},
        isEditableBinding: parentViewPath(1, '.isEditable'),
        valueBinding: parentViewPath(1, '*value')
    }),

    // Don't use the range to display string ranges
    initBindings: function() {
        this.bind('value', this, "%@".fmt(this.get('attribute')));
    }
});


Footprint.StringRangeItemView = Footprint.RangeItemView.extend({
    classNames:'footprint-string-range-item-view'.w(),
    contentView: Footprint.EditableModelStringView.extend({
        layout: {width:.99, height: 0.99},
        isEditableBinding: parentViewPath(1, '.isEditable'),
        valueBinding: parentViewPath(1, '*value')
    }),

    // Don't use the range to display string ranges
    initBindings: function() {
        this.bind('value', this, "%@".fmt(this.get('attribute')));
    }

});
