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



Footprint.CheckboxInfoView = SC.View.extend({
    childViews: 'checkboxView titleView'.w(),
    title: 'Title',
    value:null,
    contentValueKey: null,
    titleLayout: { left:35, top:3},
    buttonLayout: { top:1, left:13, width:20, height:20},

    titleView: SC.LabelView.design({
        classNames: ['footprint-checkbox-item-title'],
        layoutBinding: SC.Binding.oneWay('.parentView.titleLayout'),
        textAlign: SC.ALIGN_LEFT,
        valueBinding: SC.Binding.oneWay('.parentView.title')
    }),

    checkboxView: SC.CheckboxView.design({
        classNames: ['footprint-checkbox-item-checkbox'],
        layoutBinding: SC.Binding.oneWay('.parentView.buttonLayout'),
        valueBinding: SC.Binding.from('.parentView.value'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
        contentBinding: SC.Binding.oneWay('.parentView.content')
    })
})
