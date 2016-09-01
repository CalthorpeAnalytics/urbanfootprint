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



Footprint.SimpleEditableStringFieldItemView = Footprint.EditableModelStringView.extend({
    textAlign: SC.ALIGN_CENTER,
    status: null,
    statusBinding: SC.Binding.from('*content.status'),

    contentKeys: {'contentValueKey': 'displayValue'},
    displayValue: null,
    value: function(propKey, value) {
        if (value !== undefined) {
            // Value number or percent, set the content key accordingly
            this.setIfChanged('displayValue', value);
            return value;
        }
        // Show this value in the input field. This does not set the content key because of contentKeys
        return this.get('displayValue') || "";
    }.property('status', 'displayValue').cacheable()
});
