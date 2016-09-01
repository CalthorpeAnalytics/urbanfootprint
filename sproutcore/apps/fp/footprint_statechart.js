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

sc_require('resources/main_page');
/***
 * The Footprint Statechart. This extends SC.Statechart, which is a simple class that mixes in SC.StatechartManager
 * See SC.StatechartManager to understand or add functionality to this class.
 * @type {*}
 */
Footprint.Statechart = SC.Statechart.extend({
    rootState: SC.State.extend({
        initialSubstate: 'applicationReadyState',

        // Initial load state
        applicationReadyState: SC.State.plugin('Footprint.ApplicationReadyState'),
        // Login state
        loggingInState: SC.State.plugin('Footprint.LoggingInState'),
        // Loading state, which loads all configuration data required to show the app
        loadingAppState: SC.State.plugin('Footprint.LoadingAppState'),
        // Main application state, which delegates different section_views of the application to substates
        showingAppState: SC.State.plugin('Footprint.ShowingAppState'),
        // For test
        testAppState: SC.State.plugin('Footprint.TestAppState'),

        /***
         * When we logout delete all cookies related to the user and reload
         */
        doLogout: function() {
            Footprint.userController.destroyCookie();
            Footprint.scenariosController.destroyCookies();
            window.location.reload();
        },
    }),
});

Footprint.statechart = Footprint.Statechart.create({
    store: Footprint.store,
    mainPage: Footprint.mainPage,
    trace: NO,
    traceBinding: SC.Binding.bool('Footprint.developerModeController.traceStatechart'),
});
