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


Footprint.EditableBuildingTopView = SC.View.extend({
    classNames: ['footprint-built-form-top-view'],
    childViews:'nameTitleView contentView addressNameTitleView addressContentView'.w(),
    recordType: null,
    content: null,

    nameTitleView: SC.LabelView.extend({
       classNames: ['footprint-bold-title-view'],
       value: 'Building Name',
       fontWeight: 700,
       layout: {left: 25, width: 100, height:24, top: 10}
    }),
    contentView: Footprint.EditableModelStringView.extend({
        layout: {left: 30, width: 280, height:20, top: 30},
        valueBinding: SC.Binding.from('.parentView*content.name'),
        classNames: ['footprint-editable-content-11px-view'],
        // Editing of BuiltForms is disabled
        isEditable: NO
    }),
    addressNameTitleView: SC.LabelView.extend({
       classNames: ['footprint-bold-title-view'],
       value: 'Building Address',
       fontWeight: 700,
       layout: {left: 325, width: 100, height:24, top: 10}
    }),
    addressContentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-11px-view'],
        valueBinding: SC.Binding.from('.parentView*content.building_attribute_set.address'),
        layout: {left: 330, width: 280, height:20, top: 30},
        // Editing of BuiltForms is disabled
        isEditable: NO
    })
});
