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



sc_require('views/editable_model_string_view');
sc_require('views/info_views/info_view');
sc_require('views/info_views/info_view_configuration');

Footprint.NameInfoView = Footprint.InfoView.extend({
    classNames:'footprint-name-view'.w(),

    contentLayout: {left:.2, width: .8},
    title:'Name',
    contentView: Footprint.EditableModelStringView.extend({
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
        classNames: ['footprint-editable-content-view'],
        contentBinding: SC.Binding.oneWay('.parentView.content'),
        contentValueKey: 'name',
        isEditableBinding:SC.Binding.oneWay('.parentView.isEditable')
    })
});
