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



Footprint.LoadingState = SC.State.extend({

    init: function() {
        sc_super();
        if (!this.get('loadingController'))
            this.set('loadingController', SC.ArrayController.create());
    },

    initialSubstate: 'readyState',

    /**
     * Required for ConcurrentLoadingAnalysisToolState subclass and if combineMultipleQueryResults is YES
     */
    recordType:null,

    /**
     * Optional. The controller that is loaded by binding its content to the query.
     * If context contains a loadingController this is ignored
     */
    loadingController: null,

    /***
     * Optional. Default NO. Clear the loadingController content when entering this state
     */
    clearLoadingControllerContentOnEnter: NO,

    /***
     * Optional. Check the status of each record returned by recordArray(). Normally
     * just the status of the query or ManyArray that is returned by recordArray() is checked
     */
    checkRecordStatuses: NO,

    /***
     * Optional. If the recordArray returns multiple queries, setting this to YES will combine the query results
     * into a single array. Since there's no simply way to make a combine SC.Query (as far as I know), you
     * must set checkRecordStatuses: YES in order to ensure that all of the results are loaded
     */
    combineMultipleQueryResults: NO,

    /***
     * Set to YES to attach the loading controller to the remote query. This is useful in that
     * it will update the controller's status to BUSY. By default the controller is assigned
     * after the load completes
     */
    setLoadingControllerDirectly: NO,

    /**
     * The state event sent when the controller loads
     * TODO rename to isReadyEvent
     */
    didLoadEvent:null,

    /***
     * This event is only used by ConcurrentLoadingAnalysisToolState and LoadingConcurrentDependenciesState
     */
    didLoadControllerEvent: 'didLoadController',

    // Called before didLoadEvent is sent. Used by subclasses
    recordsAreReady: function() {
    },

    /**
     * The state event sent when the controller fails
     */
    didFailEvent:'didFailLoadingController',

    didFailLoadingController: function(context) {
        this.gotoState('errorState', context);
    },

    recordArray:function() {
        throw Error('Provide an Footprint.Store.find to load the content of loadingController. If just loading related records, this can simply return' +
            'the ManyArray records in question. Then the state will wait for the ManyArray status to become READY_CLEAN');
    },

    loadingStatusValue:0.5,

    _recordsQueue: null,

    enterState: function(context) {
        this._context = context;
        var loadingController = context && context.get('loadingController') || this.get('loadingController');
        // Clear the loadingController content is specified
        if (this.get('clearLoadingControllerContentOnEnter') && loadingController.get('content'))
            loadingController.set('content', null);

        //TODO remove
        Footprint.loadingStatusController.increment(this.get('loadingStatusValue'));
        // Need to fetch the content
        if (this.get('setLoadingControllerDirectly') && loadingController) {
            loadingController.set('content', this.recordArray(context));
            this._results = loadingController;
        }
        else {
            this._results = SC.ArrayController.create({content: this.recordArray(context)});
        }
        if (this.get('checkRecordStatuses')) {
            this._recordsQueue = SC.Set.create(this._results);
            this._recordsQueue.forEach(function(record) {
                record.addObserver('status', this, 'recordStatusDidChange');
            }, this);
            // Call in case they are already all READY_CLEAN
            this.recordStatusDidChange();
        }
        else {
            this._results.addObserver('status', this, 'loadingControllerStatusDidChange');
            // Call in case the status already READY_CLEAN
            this.loadingControllerStatusDidChange();
        }
    },

    readyState: SC.State,


    /***
     * Observe the status change of each record. This is only used
     * when checkRecordStatuses==YES
     */
    recordStatusDidChange: function() {
        var loadingController = this._context && this._context.get('loadingController') || this.get('loadingController');
        var recordsDequeue = this._recordsQueue.filter(function(record) {
            if (record && record.get('status') & SC.Record.ERROR) {
                this.statechart.sendEvent(this.get('didFailEvent'), this._results);
                return NO;
            }
            return record && record.get('status') === SC.Record.READY_CLEAN;
        }, this);
        recordsDequeue.forEach(function(record) {
            record.removeObserver('status', this, 'recordStatusDidChange');
            this._recordsQueue.removeObject(record);
        }, this);
        if (this._recordsQueue.length == 0) {
            this.loadingControllerStatusDidChange();
            if (this.get('combineMultipleQueryResults')) {
                // Now that all queries are loaded we need to flatten the results
                // Use a local query to combine results so that we have a READY_CLEAN status
                var store = Footprint.store;
                // TODO there's a corner case where
                // "showingAppState.firstLoadingTierState.firstTierAwaitingState.secondTierLoadingState.showingDbEntitiesState.dbEntitiesAreReadyState.loadingTemplateFeatureDependenciesState.loadPrimaryGeographyTemplateFeaturesState"
                // runs when it doesn't have a loadingController (meaning it should not run)
                if (!loadingController) {
                    Footprint.logError('loadingController should not be null for state %@'.fmt(this.get('fullPath')));
                    this.statechart.sendEvent('didLoadConcurrentDependencies', this._context);
                    return;
                }
                loadingController.set('content',
                    store.find(SC.Query.create({
                        recordType: this.get('recordType'),
                        location: SC.Query.LOCAL,
                        conditions: '{ids} CONTAINS id',
                        ids: loadingController.get('content').flatten().mapProperty('id')}))
                );
            }
            // This event is only used by LoadingConcurrentDependenciesState
            // Normally this is called when the loadingController's status changes, but we don't have
            // a composite status.
            if (this.get('parentState').instanceOf(Footprint.LoadingConcurrentDependenciesState))
                this.statechart.sendEvent('didLoadConcurrentDependencies', this._context);
        }
    },

    /***
     * Observe the results status and notify listeners on load or failure
     */
    loadingControllerStatusDidChange:function() {
        var results = this._results;
        if (results && (results.get('status') & SC.Record.READY) ||
            (this.get('checkRecordStatuses') && this._recordsQueue.length == 0)) {
            if (!this.get('setLoadingControllerDirectly')) {
                // This means we didn't previously set the loading controller, so so we have to set it now.
                var loadingController = this._context && this._context.get('loadingController') || this.get('loadingController');
                if (loadingController) {
                    // If combineMultipleQueryResults is set it means that we expect the results to be an array
                    // of queries. Since they are all loaded we can flatten the contents for the controller
                    if (this.get('combineMultipleQueryResults')) {
                        loadingController.set(
                            'content',
                            store.find(SC.Query.create({
                                recordType: this.get('recordType'),
                                location: SC.Query.LOCAL,
                                conditions: '{ids} CONTAINS id',
                                ids: loadingController.get('content').flatten().mapProperty('id')})));
                    } else {
                        loadingController.set('content', results.get('content'));
                    }
                }
            }
            this.invokeNext(function() {
                if (this.get('didLoadEvent'))
                    this.statechart.sendEvent(this.get('didLoadEvent'), results);
                this.recordsAreReady();
                if (loadingController)
                    // This event is only used by ConcurrentLoadingAnalysisToolState and LoadingConcurrentDependenciesState
                    this.statechart.sendEvent(this.get('didLoadControllerEvent'), loadingController);
            });
        }
        else if (!results || (results.get('status') & SC.Record.ERROR)) {
            this.statechart.sendEvent(this.get('didFailEvent'), results);
        }
    },

    errorState: SC.State.extend({
        enterState: function() {
            Footprint.logError('Error in loading state: %@'.fmt(this.toString()));
        }
    }),

    exitState:function() {
        // Stop observing upon exiting the state
        if (this._results)
            this._results.removeObserver('status', this, 'loadingControllerStatusDidChange');
        // Remove record observes
        if (this.get('checkRecordStatuses')) {
            this._recordsQueue.forEach(function(record) {
                record.removeObserver('status', this, 'recordStatusDidChange');
            }, this);
        }


        this._results = null;
        this._context = null;
    }
});
