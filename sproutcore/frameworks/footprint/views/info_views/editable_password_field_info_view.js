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



Footprint.EditablePasswordFieldView = Footprint.EditableFieldInfoView.extend({
    classNames:['footprint-editable-password-field-info-view'],

    /***
     * Removes the computed value from the parent version so that password hiding works
     */
    editableContentView: Footprint.EditableModelStringView.extend({
        classNames:['footprint-editable-field-content-view', 'footprint-editable-content-view'],
        layoutBinding: SC.Binding.oneWay('.parentView.editableContentViewLayout'),
        valueBinding: SC.Binding.oneWay('.parentView.value'),
        localize: YES,
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        textAlign: SC.ALIGN_CENTER,
        type: 'password',
        typeBinding: SC.Binding.oneWay('.parentView.type'),
        hint: '--'
    })
});
