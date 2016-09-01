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


sc_require('views/item_views/editable_float_field_item_view');

// TODO some editors use this instead of the EditableFieldInfoView. I don't know why
// Perhaps we can remove this view
Footprint.SimpleEditableFieldInfoView = SC.View.extend(SC.Control, {
    classNames: ['footprint-editable-view'],
    childViews: 'nameTitleView contentView'.w(),
    title: null,
    content: null,
    contentValueKey: null,
    layout: null,
    isPercent: NO,
    titleLayout: null,
    contentLayout: null,
    isEditable: YES,

    nameTitleView: SC.LabelView.extend({
        classNames: ['footprint-editable-title-view'],
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout')
    }),
    contentView: Footprint.EditableFloatFieldItemView.extend({
        classNames: ['footprint-editable-content-view', 'footprint-11font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isPercentBinding: SC.Binding.oneWay('.parentView.isPercent'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout')
    })
});
