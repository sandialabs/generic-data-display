# GD2 Data Store
The GD2 data store is a distinct component from the GD2 pipeline.
It exists as a way in which to store data processed through the GD2 pipeline for historical viewing in the frontend.
The GD2 Data Store connects to the GD2 Pipeline via ZMQ and then stores received data in a MongoDB instance in such a way so that the frontend can directly querry the database instance to retreive historical data.

### MongoDB Database
GD2 utilizes a MongoDB database to retain messages for displaying at a later time.
The database connects to the pipeline which essentially pushes copies of the OpenMCT messages to the database.
These historical messages are retained for a user defined amount of time, if no time limit is specified the default retention period is 1000 seconds.

The data store configuration has the following config values:
- `time_limit`: The amount of time in seconds to keep messages in the database, after this amount of time has passed the message is removed from the database.
- `gd2_pipeline_host`: The host address to use for the internal ZMQ connection between the pipeline and the datastore.
  - Note: This value _must_ be a IP address (`127.0.0.1`) and not `localhost`.
- `gd2_pipeline_port`: The port number to use for the internal ZMQ connectio between the pipeline and the datastore.
- `database_host`: The host address of the running MongoDB database for the datastore to connect to.
- `database_port`: The port number of the running MongoDB database for the datastore to connect to.

**Note:** The GD2 datastore is _only_ compatible with MongoDB databases.

Example Config:
```json
{
  "name": "data_store",
  "config": {
    "time_limit": 1000,
    "gd2_pipeline_host": "127.0.0.1",
    "gd2_pipeline_port": 5050,
    "database_host": "127.0.0.1",
    "database_port": 27017
  }
}
```