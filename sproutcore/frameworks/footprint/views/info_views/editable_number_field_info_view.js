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
 * A field for editing floats and numbers. This doesn't used contentValueKey.
 * Instead two-way bind the view's value to the value.
 */
Footprint.EditableNumberFieldInfoView = SC.View.extend({
    classNames:'footprint-editable-field-info-view'.w(),
    childViews:['titleView', 'editableContentView'],

    value: null,
    title:null,
    titleClassNames: null,
    content: null,
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    // The layout for the title.
    titleViewLayout: {},
    // The layout for the value
    editableContentViewLayout: {},
    titleBackgroundColor: null,
    isEditable: YES,
    isTextArea: null,
    contentIsEnabled: NO,

    titleView: SC.LabelView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        backgroundColorBinding: SC.Binding.oneWay('.parentView.titleBackgroundColor'),
        textAlign: SC.ALIGN_CENTER,
        isVisibleBinding: SC.Binding.oneWay('value').bool(),
        init: function() {
            sc_super()
            this.classNames = this.classNames.concat(this.getPath('parentView.titleClassNames'))
        }
    }),

    // TODO should this use EditableFloatFieldItemView ?
    editableContentView: Footprint.EditableModelStringView.extend({
        classNames:['footprint-editable-field-content-view', 'footprint-editable-content-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.editableContentViewLayout'),
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        displayValue: null,
        displayValueBinding: '.parentView.value',
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentIsEnabled: null,
        contentIsEnabledBinding: SC.Binding.oneWay('.parentView.contentIsEnabled'),
        isEnabled: function() {
            if ((this.get('content') && this.getPath('content.length') > 0) || this.get('contentIsEnabled')) {
                return YES
            }
            return NO
        }.property('content', 'contentIsEnabled').cacheable(),

        value: function(propKey, value) {
                if (value && !isNaN(value)) {
                    // parse the float and round. This eliminates anything the user enters beyond 2 decimal places.
                    var roundedValue = parseFloat(value).toFixed(0);
                    // Still return the percent with rounding
                    this.set('displayValue', parseFloat(roundedValue));
                    return roundedValue;
                }
                else if (!isNaN(this.get('displayValue'))){
                    // Multiply to a percent
                    if (this.get('displayValue')) {
                        return (parseFloat(this.get('displayValue'))).toFixed(0);
                    };
                }
            }.property('displayValue').cacheable(),
        hint: '--'
    })
});
