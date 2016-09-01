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
 * Displays a list of titlebars above the scenarios and the various analytic columns.
 * Clicking on the titlebars themselves changes the state of the application. The default state is the general view, achieved by clicking on the Scenarios bar. Clicking on an analytical changes to the detail state of that analytical category.
 * @type {Class}
 */
Footprint.ResultToolbarView = Footprint.EditingToolbarView.extend({
    classNames: 'footprint-result-toolbars-view'.w(),
    recordType: Footprint.Layer,
    titleViewLayout: {height: 17},
    controlSize: SC.SMALL_CONTROL_SIZE,
    title: 'Results',
    menuItems: []
});
