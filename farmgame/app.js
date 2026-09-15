var bodyParser = require('body-parser');
var express = require('express');
var https = require('https');
var http = require('http');
var fs = require('fs');

var app = express();

app.use(bodyParser.json());

const _DEBUG = false;

if (_DEBUG) {
    app.get('/', function(req, res) {
        res.sendFile(__dirname + '/client/debug.html');
    });
} else {
    app.get('/', function(req, res) {
        res.sendFile(__dirname + '/client/index.html');
    });
}

app.use('/client', express.static(__dirname + '/client'));

app.use((req, res, next) => {
    res.status(404).send('Sorry, that route doesn\'t exist.');
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

var options = {
    key: fs.readFileSync('/etc/letsencrypt/live/tonfarmg.site/privkey.pem'),
    cert: fs.readFileSync('/etc/letsencrypt/live/tonfarmg.site/fullchain.pem')
};

https.createServer(options, app).listen(443, function() {
    console.log('HTTPS server running on port 443');
});

http.createServer(function(req, res) {
    res.writeHead(301, { Location: 'https://' + req.headers.host + req.url });
    res.end();
}).listen(80, function() {
    console.log('HTTP server running on port 80 (redirect to HTTPS)');
});