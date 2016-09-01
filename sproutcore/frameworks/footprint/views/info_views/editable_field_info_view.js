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
 * Base class to edit a simple field value that is probably text.
 * Use other editors for other types, such as numbers and passwords
 * @type {void|*|Class|SC.RangeObserver}
 */
Footprint.EditableFieldInfoView = SC.View.extend(SC.ContentValueSupport, {
    classNames:'footprint-editable-field-info-view'.w(),
    childViews:['titleView', 'editableContentView'],
    layout: {height: 50},

    title:null,
    titleClassNames: null,
    contentStatus: null,
    contentStatusBinding: SC.Binding.oneWay('*content.status'),
    titleViewLayout: null,
    editableContentViewLayout: null,
    isTextArea: null,

    titleBackgroundColor: null,
    isEditable: YES,
    titleTextAlign: SC.ALIGN_CENTER,
    // Use 'password' for a password field
    type: 'text',
    // Our standard layout puts the title above the form field
    // This will merge with any values set for titleViewLayout and editableContentViewLayout
    // If this is no then you must specify the titleViewLayout and editableContentViewLayout manually
    useDefaultVerticalLayout: YES,
    useVerticalLayoutObserver: function() {
        if (this.get('useDefaultVerticalLayout')) {
            this.set('childViewLayout', SC.View.VERTICAL_STACK);
        }
        this.setIfChanged(
            '_computedTitleViewLayout',
            $.extend(
                {},
                this.get('useDefaultVerticalLayout') ? { height: 17 } : {},
                this.get('titleViewLayout'))
        );
        this.setIfChanged(
            '_computedEditableContentViewLayout',
            $.extend(
                {},
                this.get('useDefaultVerticalLayout') ? { height: 17 } : {},
                this.get('editableContentViewLayout'))
        );
    }.observes('.useDefaultVerticalLayout', 'titleViewLayout', 'editableContentViewLayout'),

    // Internal use only
    _computedTitleViewLayout: {},
    _computedEditableContentViewLayout: {},

    titleView: SC.LabelView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView._computedTitleViewLayout'),
        localize: YES,
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        backgroundColorBinding: SC.Binding.oneWay('.parentView.titleBackgroundColor'),
        textAlign: null,
        textAlignBinding: SC.Binding.oneWay('.parentView.titleTextAlign'),
        init: function() {
            sc_super()
            this.classNames = this.classNames.concat(this.getPath('parentView.titleClassNames'))
        }
    }),

    editableContentView: Footprint.EditableModelStringView.extend({
        classNames:['footprint-editable-field-content-view', 'footprint-editable-content-view'],
        layoutBinding: SC.Binding.oneWay('.parentView._computedEditableContentViewLayout'),
        localize: YES,
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        isTextAreaBinding: SC.Binding.oneWay('.parentView.isTextArea'),
        displayValue: null,
        displayValueBinding: '.parentView.value',
        textAlign: SC.ALIGN_CENTER,
        type: 'text',
        typeBinding: SC.Binding.oneWay('.parentView.type'),
        value: function(propKey, value) {
                if (typeof(value) !== 'undefined') {
                    this.set('displayValue', value == '' ? null : value);
                    return value;
                }
                else {
                    // Multiply to a percent
                    if (this.get('displayValue')) {
                        return this.get('displayValue');
                    }
                }
            }.property('displayValue').cacheable(),
        hint: '--'
    })
});
