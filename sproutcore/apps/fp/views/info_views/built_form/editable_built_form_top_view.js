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


Footprint.EditableBuiltFormTopView = SC.View.extend({
    classNames: ['footprint-built-form-top-view'],
    childViews:'nameTitleView contentView'.w(),
    recordType: null,
    content: null,
    titleValue: null,

    nameTitleView: SC.LabelView.extend({
       classNames: ['footprint-bold-title-view'],
       valueBinding: SC.Binding.oneWay('.parentView.title'),
       fontWeight: 700,
       layout: {left: 25, width: 100, height:24, top: 10}
    }),

    contentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-view'],
        // Editing of BuiltForms is disabled
        isEditable: NO,
        valueBinding: SC.Binding.from('.parentView*content.name'),
        layout: {left: 30, height:20, top: 30, width: 450}
    })
})
