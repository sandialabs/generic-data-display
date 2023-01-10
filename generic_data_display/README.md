## How the GD2 Backend Works at a High Level
Under the hood GD2 has 5 main components: application config parsing/validation, data process management, websocket management, an AIOHTTP server, and a database for historical frontend queries.

### Config Parsing/Validation
User specified JSON configuration parsing is done once during system startup.
The loaded JSON configuration file is then internally validated against a multi-layered JSON schema that ensures correct file formatting and validation of the values of the various connection, data, preprocessing and output fields.
All fields in the given config file are validated for their specified structure, type, content and length.
The internal validation will ensure that the config file isn't using fields that are unsupported or incorrectly typed as well as ensuring that all dependencies are satisfied between different fields.
For example, the `prefix_message_size_bytes` for protobuf data needs to be set when utilizing a TCP connection.
The validator will ensure that `prefix_message_size_bytes` is set correctly when the config is specifying a TCP connection.

In addition to validation that happens in process, it is possible to validate files before usage in GD2 by using the `gd2_validate` script provided when installing the GD2 backend package.
You can pass in a configuration file you want to utilize along with an argument specific the type of application you are using the config for to see if your json is well formatted.

### Data Process Management
Once the configuration is loaded, the parsed config is passed as an argument to the `DataProcessManager`.
This class handles the spawning of individual `DataProcessors` for each processing pipeline.
The `DataProcessors` then spin up their corresponding network receivers, data parsers, and preprocessors in order to process the data.
Each of a `DataProcessors` components is an individual python thread.
Data is passed between processing components using a data queue.
Data processing can be though of as a process pipeline.
Each `DataProcessor` has an output queue upon which the final processed data objects are pushed to.

### Websocket Management
On application startup a websocket manager is created to handle the management of client (frontend) requests and the sending of data via client websockets.
The websocket manager is linked to the output queue from all `DataProcessors`.
When clients connect to the pipeline they send subscription `topics` to describe which data they wish to access.
This allows the pipeline to efficiently send only data that the clients request, avoiding bandwidth pollution.
When data is passed into the websocket management processing queue it checks to see if any clients are subscribed to that data and then sends a message out over the connected websocket.
Currently the Websocket Manager only sends data in a format expected by the OpenMCT frontend.

### AOIHTTP Server
The pipeline uses an AOIHTTP server to handle requests for data formats, topics and websocket connections from frontend clients.
The port for the AOIHTTP server is set via the `--http-port` argument and defaults to 8844.
The web endpoints provided by the http server can be found in [web.py](web.py).
The `/config` endpoint allows clients to receive a json blob describing the current data streams available for subscription/display.
The `/live` endpoint allows clients to create a websocket endpoint for sending topic subscriptions and receiving display data.