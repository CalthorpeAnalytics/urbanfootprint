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


Footprint.EditableFloatFieldItemView = Footprint.EditableModelStringView.extend({
    textAlign: SC.ALIGN_CENTER,
    isPercent: null,
    status: null,
    statusBinding: SC.Binding.from('*content.status'),

    contentKeys: {'contentValueKey': 'displayValue'},

    /***
     * The value that's bound to the content's contentValueKey directly.
     * This exists since value is sometimes converted to/from a percent to a decimal
     * It updates the value if the content's contentValueKey value changes.
     */
    displayValue: null,

    /***
     * A percent representation of displayValue if isPercent is true. This is aways what's shown to the user.
     * When the user inputs a percent this sets displayValue to the corresponding decimal.
     * Additionally if the user enters and empty string, this sets the content value to 0 but
     */
    value: function(propKey, value) {
        var multiplier = this.get('isPercent') ? 100 : 1;
        if (this.get('status') & SC.Record.READY) {

            if (value !== undefined) {
                if (value == '') {
                    // Value is "", set content key to 0
                    this.setIfChanged('displayValue', 0.0);
                    return ""
                }
                if (isNaN(value))
                    // Allow whatever the user typed but don't update the displayValue
                    return value;
                // Value number or percent, set the content key accordingly
                this.setIfChanged('displayValue', parseFloat(value) / multiplier);
                return parseFloat(value);
            }
            // Show this value in the input field. This does not set the content key because of contentKeys
            return (this.get('displayValue') || 0) * multiplier;
        }
    }.property('status', 'displayValue').cacheable()
});
