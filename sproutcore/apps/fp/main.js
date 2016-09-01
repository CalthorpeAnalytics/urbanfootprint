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



Footprint.main = function main() {

    Footprint.developerModeController.loadFromUrl(window.location);

    Footprint.statechart.initStatechart();
    // The statechart is the defaultResponder. It will delegate actions throughout the hierarchy of active states
    // until a states responds to the action
    SC.RootResponder.responder.set('defaultResponder', Footprint.statechart);

    Footprint.DO_STATE_TESTS = NO;
    //
    // Skipping the login page for now to save time
    //setUserContent();

    Footprint.statechart.gotoState('applicationReadyState');

    // Log errors to New Relic, if enabled.
    //   https://docs.newrelic.com/docs/browser/new-relic-browser/browser-agent-apis/noticing-or-logging-front-end-errors
    //   http://docs.sproutcore.com/symbols/SC.ExceptionHandler.html
    if (window.NREUM) {
        var oldHandler = SC.ExceptionHandler.handleException;
        SC.ExceptionHandler.handleException = function(exception) {
            NREUM.noticeError(exception);
            oldHandler.call(SC.ExceptionHandler, exception);
        };
    }
};

function main() { // eslint-disable-line no-unused-vars
    Footprint.main();
}
