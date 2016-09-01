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
 * Presents the layers whose feature tables are eligible for joining to the main layer/feature_table
 */
Footprint.QueryJoinInfoView = Footprint.SelectInfoView.extend({
    classNames: 'footprint-query-info-join-view'.w(),
    contentLayout: {left: 45 },
    title: 'Join:',

    titleView: SC.LabelView.extend({
        classNames: "footprint-info-view-title-view".w(),
        layout: {height: 16, width: 45, left: 4, top: 4},
        valueBinding: '.parentView.title'
    }),

    // The Feature RecordType
    recordType: null,
    itemTitleKey: 'name',
    includeNullItem: YES,
    nullTitle: 'Join a Layer',
    nullTitleIfEmpty: 'None'
});
