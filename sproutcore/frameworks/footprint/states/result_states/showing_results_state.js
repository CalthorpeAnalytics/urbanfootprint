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
 * The state that manages the projects pane at the top of the application
 * @type {Class}
 */

Footprint.ShowingResultsState = SC.State.design({

    initialSubstate:'readyState',

    readyState: SC.State,

    doViewScenario: function(context) {
        Footprint.statechart.sendAction('doViewResults', SC.Object.create({
            content:Footprint.scenarioActiveController
        }));
        return NO
    },

    errorState: SC.State.extend({
        enterState: function() {

        }
    })
});
