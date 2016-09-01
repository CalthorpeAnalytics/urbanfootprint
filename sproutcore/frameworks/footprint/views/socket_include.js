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



(function() {

    // Override the SocketIO constructor to provide a default
    // value for the port, which is added to os.environ in the
    // runserver_socketio management command.
    var prototype = io.Socket.prototype;
    io.Socket = function(host, options) {
        options = options || {};
        options.port = options.port || 8000;
        return prototype.constructor.call(this, host, options);
    };

    // We need to reassign all members for the above to work.
    for (var name in prototype) {
        io.Socket.prototype[name] = prototype[name];
    }

    // Arrays are transferred as individual messages in Socket.IO,
    // so we put them into an object and check for the __array__
    // message on the server to handle them consistently.
    var send = io.Socket.prototype.send;
    io.Socket.prototype.send = function(data) {
        if (data.constructor == Array) {
            channel =  data[0] == '__subscribe__' || data[0] == '__unsubscribe__';
            if (!channel) {
                data = ['__array__', data];
            }
        }
        return send.call(this, data);
    };

    // Set up the subscription methods.
    io.Socket.prototype.subscribe = function(channel) {
        this.send(['__subscribe__', channel]);
        return this;
    };
    io.Socket.prototype.unsubscribe = function(channel) {
        this.send(['__unsubscribe__', channel]);
        return this;
    };

})();
