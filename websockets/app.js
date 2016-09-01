var crypto = require('crypto'),
    io = require('socket.io'),
    fs = require('fs'),
    redis = require('redis'),
    http = require('http');

var app = http.createServer(function(req, res) {
    fs.readFile(__dirname + '/index.html',
        function (err, data) {
            if (err) {
                res.writeHead(500);
                return res.end('Error loading index.html');
            }
            res.writeHead(200);
            res.end(data);
    });
});

var uf_socketio = io.listen(app);
app.listen(8081);

function SessionController (userid) {
    // session controller class for managing redis connections

    this.sub = redis.createClient();
    this.pub = redis.createClient();
    this.userid = userid;
    this.channel = 'channel_' + userid;
}

SessionController.prototype.subscribe = function(socket) {
    this.sub.on('message', function(channel, message) { socket.emit('serversays', message); });
    this.sub.subscribe(this.channel);
};

SessionController.prototype.unsubscribe = function() {
    this.sub.unsubscribe(this.channel);
};

SessionController.prototype.publish = function(message) {
    this.pub.publish(this.channel, message);
};

SessionController.prototype.destroyRedis = function() {

    if (this.sub !== null)
        this.sub.quit();

    if (this.pub !== null)
        this.pub.quit();
};

uf_socketio.sockets.on('connection', function (socket) {
    // the actual socket callback

    console.log('Connection from: ' + socket.id);

    // client asked to authenticate
    socket.on('uf_socket_auth', function(data) {

        var msg = JSON.parse(data);

        console.log('uf_socket_auth : ' + data);

        if (!socket.hasOwnProperty('sessionController')) {

    // todo: here we have to implement authentication (just make call to django and check that the session id we are given is valid),
    // for now, assume msg.user is valid however if we failed, we should emit:
    //
    // result = JSON.stringify({event: 'uf_socket_auth_result', msg: { status: 'bad_credentials' } });
    // socket.emit('serversays', result);

            socket.sessionController = new SessionController(msg.userid);

            socket.sessionController.subscribe(socket);
            var result = JSON.stringify({event: 'uf_socket_auth_result', msg: { status: 'ok' } });
            socket.emit('serversays', result);

        } else {

            // the user already logged in once and should disconnect and reconnect clear session
            // data

            var result = JSON.stringify({event: 'uf_socket_auth_result', msg: { status: 'reconnect' } });
            socket.emit('serversays', result);

            return;
        }

    });

    // receiving events from client
    socket.on('event', function (data) {

        var msg = JSON.parse(data);
        if (!socket.hasOwnProperty('sessionController')) {

            var result = JSON.stringify({event: 'uf_socket_auth_result', msg: { status: 'need_authenticate' } });
            socket.emit('serversays', result);
            return;
        }

    // todo: here we have to implement authorization of cookie to make sure that this session id is valid and belongs
    // to the user.  if that is not correct, we should emit:
    //
    //      result = JSON.stringify({event: 'uf_socket_auth_result', msg: { status: 'bad_session' } });
    //      socket.emit('serversays', result);

        console.log(msg);

        // only send clientsays event
        if (msg.event === "clientsays")
        {
            //var reply = JSON.stringify(msg);
            socket.sessionController.publish(data);
            console.log("clientsays sent");
        }

    });

    socket.on('disconnect', function() { // disconnect from a socket - might happen quite frequently depending on network quality
        if (!socket.hasOwnProperty('sessionController'))
            return;
        socket.sessionController.unsubscribe();
        socket.sessionController.destroyRedis();
        delete socket.sessionController;

    });
});
