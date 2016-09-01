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


Footprint.LoadingConcurrentDependenciesState = SC.State.extend({
    substatesAreConcurrent: YES,

    /***
     * Creates an observer for each substates loadingController status and queues up the substate
     * so we know when all of them are finished
     * If a substate lacks a loadingController it's assumed that the substate isn't meant to to run
     * @param context
     */
    enterState: function(context) {
        this._context = context;
        this._loadingControllerQueue = [];
        this.get('substates').forEach(function(substate) {
            if (substate.get('loadingController')) {
                substate.get('loadingController').addObserver('status', this, 'loadingControllerStatusDidChange');
                this._loadingControllerQueue.push(substate);
            }
        }, this);
    },

    loadingControllerStatusDidChange:function(sender) {
        if (sender.get('status') & SC.Record.READY) {
            sender.removeObserver('status', this, 'loadingControllerStatusDidChange');
            this._loadingControllerQueue.pop(sender);
        }
        if (this._loadingControllerQueue.length == 0) {
            this.statechart.sendEvent('didLoadConcurrentDependencies', this._context);
        }
    }
});
