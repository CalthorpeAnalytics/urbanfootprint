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

Footprint.DescriptionInfoView = Footprint.InfoView.extend({
    classNames: "footprint-description-item-view".w(),
    /***
     * The layout of the title
     */
    titleViewLayout: {left: 0.01, height: 18},
    /***
     * The layout of the text area. If not set this will
     * put the content below the title
     */
    contentLayout: { top: 18 },

    title:'Description',
    contentView: Footprint.EditableModelStringView.extend({
        classNames: ['footprint-editable-content-view'],
        hint: 'Provide a description',
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout'),
        textArea: YES,
        contentValueKey: SC.Binding.oneWay('.parentView.contentValueKey')
    })
});
