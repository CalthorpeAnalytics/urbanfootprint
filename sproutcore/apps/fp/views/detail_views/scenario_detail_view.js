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


sc_require('views/detail_views/detail_view');

Footprint.ScenarioDetailView = Footprint.DetailView.extend({
    classNames: ['footprint-scenario-info-editable-content-view'],
    childViews: ['nameView', 'yearView', 'descriptionView'],

    nameView: Footprint.EditableFieldInfoView.extend({
        layout: {height: 40},
        titleViewLayout: {height: 17, width: 100},
        editableContentViewLayout: {top: 19, left: 15},
        valueBinding: '.parentView*content.name',
        title: 'Scenario Name'
    }),

    yearView: Footprint.EditableFieldInfoView.extend({
        layout: {top: 45, height: 40},
        titleViewLayout: {height: 17, width: 100},
        editableContentViewLayout: {top: 19, left: 15},
        valueBinding: '.parentView*content.year',
        title: 'Scenario Year'
    }),

    descriptionView: Footprint.EditableFieldInfoView.extend({
        layout: {top: 90, bottom: 0},
        titleViewLayout: {height: 17, width: 100},
        editableContentViewLayout: {top: 20, left: 15},
        isTextArea: YES,
        valueBinding: '.parentView*content.description',
        title: 'Description'
    })
});
