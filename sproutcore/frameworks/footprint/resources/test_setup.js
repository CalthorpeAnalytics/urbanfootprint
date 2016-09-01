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
 * Sets up the application testing
 * @param config. An object with configuration attributes:
 *  attribute datasource: an optional class to use for the Datasource, such as Footprint.Datasource. Defaults to SC.Record.fixtures
 * @return {*}
 */
function setupForTesting(config) {
    config = config || {};
    // Set the TEST variable so the application doesn't render views
    Footprint.TEST = YES;
    //Footprint.TEST_DATASOURCE = Footprint.FixturesDataSource.create();
    Footprint.TEST_DATASOURCE = Footprint.DataSource.create();
    // Reset the store to use fixtures, unless the config specifies a datasource
    Footprint.store = SC.Store.create().from(config.datasource || Footprint.TEST_DATASOURCE);
    SC.Logger.debugEnabled = YES;
    //SC.LOG_OBSERVERS = YES;
    //SC.LOG_BINDINGS = YES;
    CoreTest.trace = YES;
}

/***
 * A stateSetup option to skip the login step for controller testing
 */
function bypassLoginState() {
    setUserContent();
    Footprint.statechart.gotoState('loadingApp');
    SC.RunLoop.begin();
    try {
        SC.RunLoop.end();
    } catch(e) {
        Footprint.logError(e);
        throw e;
    }
}

Footprint.Test = SC.Object.extend({
    /**
     * A label to identify the test for debugging
     */
    label: "Unlabeled Test",

    /**
     * Footprint.Test class extensions that depend on this instance completing. These will be instantiated and chained
     * so that they execute after the previous is ready. The first is executed when this is ready
     */
    dependents:null,
    /**
     * Status of the test. The dependent tests are instantiated when this status becomes READY_CLEAN
     *
     **/
    status: null,
    /**
     * Set to an observable object with a status property for top-level tests. Dependent tests will be instantiated
     * with this set to their parent.
     */
    dependsOn: null,
    /**
     * Optional timeout period from the start of onReady until the calling of onComplete
     */
    timeout:null,
    /**
     * Optional timeout period that measures from onReady to the last dependent completing. The regular timeout
     * only test the time between onReady and onComplete for this test, ignoring dependents
     */
    dependentTimeout:null,
    /**
     * Optional timout period that specifies that the test must be ready to run after creation in this period of time
     */
    onReadyTimeout:null,

    /**
     * The status code to expect from the dependOn property, SC.Record.READY_CLEAN by default
     * This only makes sense to change on the top level test, since dependent tests will always listen for their
     * parent 'status' property to become READY_CLEN
     */
    dependsOnStatus: SC.Record.READY_CLEAN,
    /**
     * The status property of dependsOn, by default 'status'
     */
    dependsOnStatusProperty: 'status',
    /**
     * The status code to expect from the result object of run(). SC.Record.READY_CLEAN by default
     */
    completeStatus: SC.Record.READY_CLEAN,
    /**
     * The status property of the result object of run, by default 'status'
     */
    completeStatusProperty: 'status',

    /**
     * Override to do something when the dependent tests complete, such ass resume the main thread
     */
    onDependentsComplete: function() {},

    /**
     * Internal tracking of the instantiated _dependents. Used for debugging
     */
    _dependents: null,
    _timeout: null,
    _dependentTimeout: null,
    _onReadyTimeout:null,
    // References the parent test for dependent tests. Just used to call dependentsComplete
    _parentTest:null,
    // Indicates that a test is the final dependent and tus calls parentTests's dependentsComplete upon completion
    _isLastDependent:NO,

    init: function() {
        sc_super();
        if (!this.dependents)
            this.dependents = [];
        // Iterate through the dependents and make each run when the previous is READY_CLEAN
        // The first dependent has no previous to observe and thus is invoked manually in onReady to start the chain
        var self = this;
        this._dependents = $.mapWithPreviousResult(this.get('dependents'), function(test, previous, index) {
            return test.create({
                dependsOn:previous,
                _parentTest:self,
                _isLastDependent:index==self.get('dependents').length-1
            });
        });
        // Observer what we depend on completing
        if (this.get('dependsOn')) {
            this.get('dependsOn').addObserver(this.get('dependsOnStatusProperty'), this, 'onReady');
        }
        // Optional timeout between now and onReady. This makes sure that the dependsOn actually completes
        // for top-level tests (where the dependsOn is a controller or something and not a parent test.)
        if (this.get('onReadyTimeout')) {
            this.set('_onReadyTimeout', setTimeout(function() {
                fail("OnReady timeout for Test %@".fmt(self.get('label')));
            }, self.get('onReadyTimeout')))
        }
    },
    /***
     * The actual test content to run. If this returns a value it must have a status that will be tracked.
     * Otherwise the test is assumed to be synchronous and the next dependent will run immediately afterward
     */
    run: function() {

    },
    onReady: function(sender, key) {
        // Invoke last to avoid a direct chain of events from the controller code
        this.invokeLast(function() {
            if (!this.get('dependsOn') || this.get('dependsOn').get(this.get('dependsOnStatusProperty')) === this.get('dependsOnStatus')) {

                // Clear the onReadyTimeout
                if (this.get('_onReadyTimeout'))
                    clearTimeout(this.get('_onReadyTimeout'));

                // Start the first dependent if there is one.
                if (this._dependents.length > 0) {
                    this._dependents[0].onReady();
                }

                // Run this Test
                var result = this.run();
                if (result && result.get(this.get('completeStatusProperty')) !== this.get('completeStatus')) {
                    // If we have a result and it's not in the complete state yet, create an observer to await yon state
                    var completeStatusProperty = this.get('completeStatusProperty');
                    if (undefined===result.get(completeStatusProperty)) {
                        throw "The result of the test %@ was not null but has no status property to track".fmt(result);
                    }
                    result.addObserver(completeStatusProperty, this, 'onComplete');
                }
                else {
                    // Run onComplete immediately
                    this.onComplete()
                }
                // Remove the observer
                if (sender)
                    sender.removeObserver(key, this, 'onReady');

                // If there's a timeout set we expect onComplete to be called within the specified time from now.
                var self = this;
                if (this.get('timeout')) {
                    this.set('_timeout', setTimeout(function() {
                        fail("Timeout for Test %@".fmt(self.get('label')));
                    }, self.get('timeout')))
                }
                // If there's a dependentTimout we expect the last dependent to finish within the specified duration
                if (this.get('dependentTimeout')) {
                    this.set('_dependentTimeout', setTimeout(function() {
                        fail("Timeout for Dependents Completing for Test %@".fmt(self.get('label')));
                    }, self.get('dependentTimeout')))
                }
            }
        });
    },
    /***
     * Called when the status of the test result changes
     * Triggers the next dependent
     */
    onComplete: function(sender, key) {
        // Clear the timeout if one was set
        if (this.get('_timeout'))
            clearTimeout(this.get('_timeout'));
        if (!sender || sender.get(key) === this.get('completeStatus')) {
            this.set('status', SC.Record.READY_CLEAN);
            // Remove the observer if it exists
            if (sender)
                sender.removeObserver(key, this, 'onComplete');
        }
        // If this is the last dependent test call the parent's dependentsComplete, which is simply used for
        // validate that the dependentTimeout duration wasn't exceeded
        if (this.get('_parentTest') && this.get('_isLastDependent')) {
            this.get('_parentTest').dependentsComplete()
        }
    },
    /***
     * Called when the last dependent is complete. Use dependentTimeout to check if this was called in time
     */
    dependentsComplete: function() {
        if (this.get('_dependentTimeout'))
            clearTimeout(this.get('_dependentTimeout'));
        this.onDependentsComplete();
    },

    toString: function() {
        return this.toStringAttributes('label dependsOn status _dependents'.w());
    }
});
