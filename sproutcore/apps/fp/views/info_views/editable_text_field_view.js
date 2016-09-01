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



Footprint.EditableTextFieldView = SC.View.extend({
    classNames:'footprint-editable-clone-field-view'.w(),
    childViews:['titleView', 'editableContentView'],
    value: null,
    title:null,
    titleClassNames: null,
    content: null,
    contentValueKey: null,
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    titleViewLayout: null,
    editableContentViewLayout: null,
    titleBackgroundColor: null,
    isEditable: YES,
    isNumber: NO,
    significantDigits: 0,

    // If YES, then only send updates to displayValue on a timer. This
    // prevents bindings from being overwhelmed with changes.
    coalesceChanges: NO,

    // If coalesceChanges is YES, then this is the number of
    // milliseconds after the latest changes before displayValue is
    // updated.
    coalesceInterval: 300,

    titleView: SC.LabelView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        backgroundColorBinding: SC.Binding.oneWay('.parentView.titleBackgroundColor'),
        textAlign: SC.ALIGN_CENTER,
        init: function() {
            sc_super();
            this.classNames = this.classNames.concat(this.getPath('parentView.titleClassNames'));
        }
    }),

    editableContentView: Footprint.EditableModelTextView.extend({
        classNames:['footprint-editable-clone-field-content-view', 'footprint-editable-content-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.editableContentViewLayout'),
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isNumberBinding: SC.Binding.oneWay('.parentView.isNumber'),
        significantDigitsBinding: SC.Binding.oneWay('.parentView.significantDigits'),
        isEnabled: function() {
            if (this.get('content') && this.getPath('content.length') > 0) {
                return YES;
            }
            return NO;
        }.property('content').cacheable(),

        // This timer coalesces changes to 'displayValue'
        changeTimer: null,
        coalesceChangesBinding: SC.Binding.oneWay('.parentView.coalesceChanges'),
        coalesceIntervalBinding: SC.Binding.oneWay('.parentView.coalesceInterval'),

        _updateDisplayValue: function(timer) {
            // TODO: If the timer is taking a long time to fire, probably should back off by raising the interval.
            // We can find the percentage lag from Math.abs(1 - (timer.lastFireTime - timer.startTime)/timer.interval)
            this.set('displayValue', this._convertDisplayValue(this._localValue));
            this.changeTimer = null;
        },

        _convertDisplayValue: function(value) {
            var formatted_value = value == '' ? null : value;
            //handle numeric types
            //TODO handle data with different lengths of significant digits
            if (formatted_value && this.get('isNumber')) {
                formatted_value = parseFloat(value).toFixed(this.get('significantDigits'));
            }
            return value;
        },
        displayValue: null,
        displayValueBinding: '.parentView.value',
        value: function(propKey, value) {
            if (typeof(value) === 'undefined') {
                // getter - returns the text representation
                return this.get('displayValue');
            } else {
                // setter
                this._localValue = value;
                if (this.get('coalesceChanges')) {
                    if (this.changeTimer) {
                        this.changeTimer.invalidate();
                    }
                    this.changeTimer = SC.Timer.schedule({
                        target: this,
                        action: '_updateDisplayValue',
                        interval: this.get('coalesceInterval'),
                    });
                } else {
                    // set the value immediately
                    this._updateDisplayValue();
                }
                return value;
            }
        }.property('displayValue').cacheable()
    })
});
