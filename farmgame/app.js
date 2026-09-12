var bodyParser = require('body-parser');
var express = require('express');

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

var server = app.listen(8082, function() {
    var port = server.address().port;
    console.log('Server running at port %s', port);
});
