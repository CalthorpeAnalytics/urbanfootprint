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

Footprint.EditableBottomInfoView = SC.View.extend(SC.ContentDisplay, {
    classNames: ['footprint-bottom-labelled-view'],
    childViews:'nameTitleView contentView'.w(),
    title: null,
    content:null,
    contentValueKey: null,
    layout: null,

    nameTitleView: SC.LabelView.extend({
        classNames: ['footprint-10font-title-view'],
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.oneWay('.parentView.title'),
        layout: {top:0.6}
    }),
    contentView: Footprint.EditableModelTextView.extend({
        layout: {height:.5},
        classNames: ['footprint-bottom-labelled-content-view'],
        classNameBindings: ['positiveNegative:is-negative'],
        isEditableBinding: SC.Binding.oneWay('.parentView.isEditable'),
        positiveNegative: function() {
            return this.get('value') < 0
        }.property('value').cacheable(),
        textAlign: SC.ALIGN_CENTER,
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKeyBinding: SC.Binding.oneWay('.parentView.contentValueKey'),
    })
});
