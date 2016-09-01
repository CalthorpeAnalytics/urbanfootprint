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
 * Designed for editing Feature attributes. This doesn't differ much from a
 * normal editable text field view, so maybe could be removed
 * @type {void|*|Class|SC.RangeObserver}
 */
Footprint.EditableFeatureFieldInfoView = SC.View.extend({
    classNames:'footprint-editable-field-info-view'.w(),
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
    isTextArea: null,

    titleView: SC.LabelView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        backgroundColorBinding: SC.Binding.oneWay('.parentView.titleBackgroundColor'),
        textAlign: SC.ALIGN_CENTER,
        init: function() {
            sc_super()
            this.classNames = this.classNames.concat(this.getPath('parentView.titleClassNames'))
        }
    }),

    editableContentView: Footprint.EditableModelStringView.extend({
        classNames:['footprint-editable-field-content-view', 'footprint-editable-content-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.editableContentViewLayout'),
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        isTextAreaBinding: SC.Binding.oneWay('.parentView.isTextArea'),
        isEnabled: function() {
            if (this.get('content') && this.getPath('content.length') > 0) {
                return YES
            }
            return NO
        }.property('content').cacheable(),

        displayValue: null,
        displayValueBinding: '.parentView.value',
        value: function(propKey, value) {
                if (typeof(value) !== 'undefined') {
                    this.set('displayValue', value == '' ? null : value);
                    return value;
                }
                else {
                    if (this.get('displayValue')) {
                        return this.get('displayValue');
                    }
                }
            }.property('displayValue').cacheable()
    })
});
