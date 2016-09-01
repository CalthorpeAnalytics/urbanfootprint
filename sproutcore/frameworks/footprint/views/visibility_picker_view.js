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
 * Displays a visible, invisible, and solo button as a segmented view. Exactly one value can be set at.
 */
Footprint.VisibilityPickerView = SC.SegmentedView.design({
    content:null,
    allowsMultipleSelection:NO,
    // Don't present the more... button
    shouldHandleOverflow:NO,

    items: [
        SC.Object.create({
            value: Footprint.VISIBLE,
            direction:SC.LAYOUT_VERTICAL,
            theme: SC.ButtonView,
            size: SC.AUTO_CONTROL_SIZE,
            action:'visibleAction'
        })
    ],

    itemValueKey: 'value',
    height: 'size',
    theme: 'theme',
    itemActionKey: 'action',
    layoutDirection: 'direction',
    itemWidthKey: 'width'
});
