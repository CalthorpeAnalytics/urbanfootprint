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


Footprint.resultLibraryUpdate = SC.ObjectController.create({
});

Footprint.SocketIOState = SC.State.design({

    initialSubstate: 'readyState',
    readyState: SC.State.design({
        enterState: function() {
            // Open communication to the socketIO server
            this.get('parentState').initSocketIO();
            console.log('socketIO ready state');
        }
    }),

    socket: null,
    /***
     * This initiallizes and reconnects the socket to the server.
     * If it fails then the observer will try to reconnect for tries times
     */
    initSocketIO: function() {
        var host = window.location.host.split(':')[0];
        if (window.location.host.split(':')[1]=='4020')
            // If using a host sproutcore server continue to send socketio straight
            // to the guest server since the host sproutcore server can't seem
            // to proxy it successfully.
            this.set('socket', io.connect('http://172.28.128.3:80'));
        else
            this.set('socket', io.connect(document.location.protocol + '//' + host));
    },
    tries:5,
    _triesCount:5,

    socketReadyObserver: function() {
        console.log('socketReadyObserver');
        var self = this;
        if (!this.socket) {
            this._triesCount--;
            if (this._triesCount > 0) {
                // Keep trying to connect
                setTimeout(function() {
                    self.initSocketIO();
                }, 1000);
            }
            else {
                Footprint.logError('Giving up connection to socketIO after %@ tries'.fmt(this.tries));
            }
        }
        else {
            // Reset the tries in case we get disconnected and have to reconnect
            this._triesCount = this.tries;

            // Set up the listeners
            if (!this.socket.$events || !this.socket.$events['serversays'] || this.socket.$events['serversays'].length == 0) {
                console.log('set up the listeners');
                this.socket.on('serversays', function (msg) {
                    var message = $.evalJSON(msg);

                    // Send the event by its name
                    // message names are matched in states that are appropriate to handle them
                    // For instance showingScenariosState handled createScenarioCompleted and createScenarioFailed,
                    // whereas showingResultsState handles
                    console.log(message.event);
                    SC.run(function() {
                        self.get('statechart').sendEvent(message.event.camelize(), SC.Object.create(message));
                    }, this);
                });
            }

            if (this.timer)
                timer.invalidate();
            // Ping the server every hundred seconds until our socket io is better set up in the future
            // This is just debugging info so we know we are still connected
            this.timer = SC.Timer.schedule({
                target: this,
                action: 'footprintAuth',
                interval: 100000,
                repeats: YES
            });
            // Fire immediately to do the authorization on startup
            this.timer.fire();
        }
    }.observes('.socket'),

    /***
     * Ping to the server
     */
    footprintAuth: function() {
        // send auth message
        this.socket.emit(
            'uf_socket_auth',
            $.toJSON({
                userid: F.userController.getPath('firstObject.id')
            }));
    },

    /***
     * Event handler for the authorization message from the server
     * @param message
     */
    ufSocketAuthResult: function(message) {
        SC.Logger.debug('SocketIO authorization result: %@'.fmt(message.msg.status));
    },



    /***
     * Run when an export completes. Fetches the url to commence download
     * @param message
     */
    layerExportCompleted: function(message) {
        var api_key = Footprint.userController.getPath('content.firstObject.api_key');
        var request_url = '/footprint/%@/get_export_result/%@/'.fmt(api_key, message.job_id);
        window.location.assign(request_url);
    },

    /***
     * Run when an export completes. Fetches the url to commence download
     * @param message
     */
    queryResultExportCompleted: function(message) {
        var api_key = Footprint.userController.getPath('content.firstObject.api_key');
        var request_url = '/footprint/%@/get_export_result/%@/'.fmt(api_key, message.job_id);
        window.location.assign(request_url);
    },

    exportQueryResultsFailed: function(message) {
        SC.AlertPane.warn({
            message: 'Could not complete query export',
            description: 'Something went wrong during the export process'
        });
    },

    /***
     * Run when an instance clone or create completes. This tells the active saving_state to complete
     * @param message
     */
    scenarioCreationComplete: function(message) {
        this.get('statechart').sendEvent('creationDidComplete', SC.Object.create(message));
    },
    scenarioCreationFailed: function(message) {
        SC.AlertPane.warn({
            message: 'Could not complete Scenario clone/create',
            description: 'Something went wrong during the clone/creation process'
        });
    }
});
