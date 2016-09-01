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
sc_require('views/info_views/range_item_view');

Footprint.NumberItemView = Footprint.InfoView.extend({
    classNames:'footprint-number-item-view'.w(),
    contentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-view'],
        layout: {left: .2, width: .8},
        valueBinding: parentViewPath(1, '*value'),
        validator: SC.Validator.Number
    })
});

Footprint.NumberRangeItemView = Footprint.RangeItemView.extend({
    classNames:'footprint-number-range-item-view'.w(),
    contentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-view'],
        layout: {left: .2, width: .8},
        isEditableBinding: parentViewPath(1, '.isEditable'),
        valueBinding: parentViewPath(1, '*value'),
        validator: SC.Validator.Number
    })
});
