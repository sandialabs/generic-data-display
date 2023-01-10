const { MongoClient } = require('mongodb');
const express = require('express')
var cors = require('cors')
var minimist = require('minimist');
const bodyParser = require('body-parser');

// CLI args
let args = minimist(process.argv.slice(2), {
    default: {
        url: 'mongodb://localhost:27017',
    },
});

console.log('MongoDB URL:', args['url']);

// MongoDB Connection URL
const url = args['url'];
const client = new MongoClient(url);

// MongoDB Database Name
const dbName = 'GD2';

// Database and collection connection
const db = client.db(dbName);
const collection = db.collection('messages');

// Server and server port
const server = express()
server.use(bodyParser.urlencoded({ extended: true }));
server.use(bodyParser.json());
const port = 3000

server.use(cors())

// Start server on a specified port
server.listen(port, ()=>{
    console.log(`Server is listening on port ${port}`)
})

// Setup get endpoint
server.get('/', (request, response) => {
    // console.log(request)
    // console.log(request.query)
    field = request.query['field']
    collection.find({topic:field}).project({ _id: 0, expire_at: 0}).toArray().then(results => {
        // console.log('Found documents =>', results)
        response.send(results)
        }
    )
    .catch(console.error)
})

var namespaces

// Namespaces POST endpoint
server.post('/namespaces', (request, response) => {
    namespaces = request.body['namespaces']
    response.sendStatus(200);
})

// Namespaces GET Endpoint
server.get('/namespaces', (request, response) => {
    response.send(namespaces)
})

client.connect().then(client => {
    console.log('Connected successfully to the GD2 MongoDB database');
    }
)
.catch(console.error)
