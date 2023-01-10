# GD2 Pipeline
This directory contains the python files, packages, and code needed to instantiate the GD2 pipeline.
Additionally this documentation contains more information describing the features provided by the GD2 pipeline as well as how to write a JSON DSL configuration file.

## How to Write a Config File
A GD2 JSON DSL config file is a file containing a single JSON object that validates against the GD2 json schema and describes the inputs, data format, and outputs of a data processing stream.
At a highest level, each config file contains a `config: []`, each of which describes how to create a single GD2 `DataProcessor`.
The config for a `DataProcessor` consists of a `name`, `connection`, `data`, `preprocessing`, `generator` and `output` fields.
- `name` will uniquely describe this `DataProcessor` when compared to other configs defined in the same file.
- `connection` will describe the input connection type.
- `data` will describe the input data format to parse.
- `preprocessing` will describe the various functions to apply to the parsed input data in series.
- `generator` will describe the finalized output data taken and then tee-ed out from the final preprocessing stage (like OpenMCT shaped data).
- `output` will describe the tee-ed output stages for sending the processed data to other applications (like the GD2 frontend/data storage solutions).

Fields can be access within each section using a GD2 specific parsing syntax.
This syntax describes how to access nested field members and array members while also supporting regular expression processing of field paths.

Example Root Config:
```json
{
  "description": "An Example Configuration",
  "version": "1.0",
  "config": [
    {
      "name": "example_config",
      "connection": {"..."},
      "data": {"..."},
      "preprocessing": [
        {"..."},
        {"..."}
      ],
      "generator": [
        {"..."},
        {"..."}
      ],
      "output": [
        {"..."},
        {"..."}
      ]
    }
  ]
}
```

### Name
Single config files can hold multiple data configurations that will be parsed and displayed separately in the OpenMCT frontend.
The combined configurations should be of the following form:

```json
{
  "description": "An Example Configuration",
  "version": "1.0",
  "config": [
    {
      "name": "tcp_config",
      "connection": {"..."},
      "data": {"..."},
      "preprocessing": [
        {"..."},
        {"..."}
      ],
      "output": [
        {"..."},
        {"..."}
      ]
    },
    {
      "name": "zmq_config",
      "connection": {"..."},
      "data": {"..."},
      "preprocessing": [
        {"..."},
        {"..."}
      ],
      "output": [
        {"..."},
        {"..."}
      ]
    }
  ]
}

```

### Connection
Connection type is chosen by supplying the required `"type": "x"` option to the `connection` config field.

#### TCP
Selected when using a type of `tcp`.
Has the following config arguments:
- `method`: supports one of either `connect` or `bind`
- `address`: the hostname or IP address to connect/bind to
- `port`: the port to connect/bind to
- `reconnect_attempts`: the number of reconnect attempts to make when if the connection experiences an interruption or drop
- `reconnect_interval_sec`: the amount of time, in seconds, to wait between each reconnection attempt

Example Config:
```json
"connection": {
    "type": "tcp",
    "method": "connect",
    "address": "localhost",
    "port": 21772,
    "reconnect_attempts": 5,
    "reconnect_interval_sec": 2
}
```

#### HTTP / GET
Selected when using a type of `http`.
Has the following config arguments:
- `method`: Specifies that the HTTP request will use the GET method.
- `http_accept`: Specifies the data format to expect from the HTTP server.
- `address`: The IP or Domain Name of the data source HTTP server.
- `port`: The port number of the data source HTTP server.
- `path`: The path portion of the URL.
- `rate_sec`: The delay time (in seconds) between polling iterations.
- `timeout_sec`: The maximum amount of time to wait (in seconds) for an HTTP polling request to respond.

```json
"connection": {
    "type": "http",
    "method": "GET",
    "http_accept": "json",
    "address": "127.0.0.1",
    "port": 8081,
    "path": "/endpoint",
    "rate_sec": 10,
    "timeout_sec": 10
}
```

#### HTTP / POST
Selected when using a type of `http`.
Has the following config arguments:
- `method`: Specifies that the HTTP request will use the POST method.
- `http_accept`: Specifies the data format to expect from the HTTP server.
- `address`: The IP or Domain Name of the data source HTTP server.
- `port`: The port number of the data source HTTP server.
- `path`: The path portion of the URL.
- `rate_sec`: The delay time (in seconds) between polling iterations.
- `timeout_sec`: The maximum amount of time to wait (in seconds) for an HTTP polling request to respond.
- `post_request`: The body of the POST request.

```json
"connection": {
    "type": "http",
    "method": "POST",
    "http_accept": "json",
    "address": "127.0.0.1",
    "port": 8081,
    "path": "/endpoint",
    "rate_sec": 10,
    "timeout_sec": 10,
    "post_request": "{\"val\": 45, \"post\": {\"ok\": true}}"
}
```

**WARNING:**

The http_sender throws a "Connection reset by peer" exception whenever we try POST requests.
I found the best answers here:
* https://github.com/psf/requests/issues/4937
* https://github.com/urllib3/urllib3/issues/944#issuecomment-237471302

From my understanding, python automatically retries with GET requests, because GET requests are not supposed
to cause any state changes to the website. However, it does not automatically retry with POST (because
these request can change state); and this is why we see the issue only for POST requests.

The first link above proposes a workaround, unfortunately it didn't work when I tried it.
Since this is a client issue, GD2 customers may experience this problem. We might want to look into
alternatives to the built-in HTTP Client.

#### ZMQ
Selected when using a type of `zmq`.
Has the following config arguments:
- `method`: supports one of either `connect` or `bind`
- `address`: the hostname or IP address to connect/bind to
- `port`: the port to connect/bind to
- `socket_type`: The ZMQ socket type to use, main support implemented for `PUB/SUB` and `PUSH/PULL` types.
- `topic`: The ZMQ topic to use for `PUB/SUB` socket type.

Example Config:
```json
"connection": {
    "type": "zmq",
    "method": "connect",
    "address": "localhost",
    "port": 35555,
    "socket_type": "SUB",
    "topic": ""
}
```

### Data Formats
Data format is chosen by suppling the `"format": "x"` option to the `data` config field.

#### Kaitai
Selected when using a format of `kaitai`.
Has the following config arguments:
- `kaitai_file`: full path to the kaitai structure definition file to use when parsing input data.
                 Note: GD2 attempts to manually generate the kaitai python source from the provided kaitai yaml definition file.
                 This requires that the kaitai_compiler can be found on the `PATH` of the user's machine.

Example Config:
```json
"data": {
    "format": "kaitai",
    "kaitai_file": "path/to/kaitai/file.ksy"
}
```

#### Protobuf
Selected when using a format of `protobuf`.
Has the following config arguments:
- `protobuf_file`: The user defined protocol buffer file to parse and generate code for.
                   Note: GD2 attempts to manually generate the protocol python source from the provided protocol buffer file.
                   This requires that the protoc compiler can be found on the `PATH` of the user's machine.
- `protobuf_class`: The user selected class that should be parsed from the input byte stream.
- `prefix_message_size_bytes`: The byte size of the prefix that should be parsed to get the total message size.
                               Note: This is only necessary when the input connection format is TCP.
                               This is because with TCP we need to know how many bytes to parse ahead of time when pulling from the stream.
                               Following protocol buffer guidelines for transferring PB message via TCP recommend prefixing the message size to the stream.

Example Config:
```json
"data": {
    "format": "protobuf",
    "protobuf_file": "path/to/protobuf/file.proto",
    "protobuf_class": "ExampleData",
    "prefix_message_size_bytes": 4
}
```

#### Json
Selected when using a format of `json`.
Has the following config arguments:
- `schema`: An optional json schema with which to validate input json against

Example Config:
```json
"data": {
    "format": "json",
    "schema": "path/to/json/schema/file.jsonschema"
}
```

#### CSV
Selected when using a format of `csv`.
When using TCP as the connection type, CSV data must include a `\n` delimiter.
If the `\n` delimiter is not included, data will fail to process.
If the CSV includes a `\n` then the TCP processor will fail to process the data.
Has the following config arguments:
- `headers`: A required comma-separated string which specifies the headers of the CSV data

Example Config:
```json
"data": {
    "format": "csv",
    "headers": "field_one,field_two,field_three,field_four"
}
```

#### XML
Selected when using a format of `xml`.
When using TCP as the connection type, XML data must include define a delimiter (typically b'\x00').
If an XML delimiter is not included, data will fail to process.
Has the following config arguments:
- `schema`: An optional XSD Schema file used to validate input XML.
- `message_delimiter_byte`: The delimiter byte expected at the end of each XML object.

Example Config:
```json
"data": {
    "format": "xml",
    "schema": "path/to/schema.xsd",
    "message_delimiter_byte": "\\0"
}
```

#### Yaml
Selected when using a format of `yaml`.
When using TCP as the connection type, YAML data must include the start (`...`) and end delimiters (`---`).
If the YAML delimiters are not included, data will fail to process.
Has the following config arguments:
- `schema`: An optional yaml schema with which to validate input yaml against (this schema is validated by the JSON Schema)

Example Config:
```json
"data": {
    "format": "yaml",
    "schema": "path/to/json/schema/file.jsonschema"
}
```

### Preprocessors
GD2 supplies many custom preprocessors that can be used to modify incoming data.
Many preprocessors assist in making the display of data via the frontend easier.
Under the hood, preprocessing works by wrapping input data in an `AccessWrapper` which facilitates the access and modification of data using python accessors.
Additionally GD2 implements its own custom syntax system to allow for regular expression matching and substitution within a single preprocessor's config definition.
Each preprocessor is a json object that consists of a `name` and `config` field.
The `name` describes the preprocessor to select, and the `config` is the input that tells the preprocessor which functions to perform.

#### base64
Either encodes or decodes a base64 input field.
Selected when using a name of `base64`.
Has the following config arguments:
- `input`: The input field to modify
- `output`: The output field name to generate
- `operation`: One of either `encode`|`decode`, specifies whether to encode data or decode data.

Example Config:
```json
{
  "name": "base64",
  "config": {
    "input": "key:input/data/field",
    "output": "key:output/data/field",
    "operation": "decode"
  }
}
```

#### imagify
Takes an input raster type image and converts it to a format suitable for display.
Selected when using a name of `imagify`.
Has the following config arguments:
- `input_array`: The input image raster to imagify
- `datauri`: The output encoded image used for display
- `rows`: The row size of the image
- `cols`: The col size of the image
- `log_level`: The log level to set the underlying PIL logger to use
- `input_format`: The input image format, currently supported formats: `{RGB}`
- `datauri_format`: The output image format, currently supported formats: `{BMP}`

Example Config:
```json
{
  "name": "imagify",
  "config": {
    "input_array": "key:input/data/field",
    "datauri": "key:output/data/field",
    "rows": "key:num/rows",
    "cols": 64,
    "log_level": "DEBUG",
    "input_format": "RGB",
    "datauri_format": "BMP"
  }
}
```

#### find_index_by_key
Takes an input "value" field to match a provided "key" against, assigning the first element with a matching key value to the root level object.
Useful for searching through a list of values for a specific key to display or manipulate more easily.
Selected when using a name of `find_index_by_key`.
Has the following config arguments:
- `matches`: A list of configs to match against; has the following config arguments:
  - `value`: The field value to check for a match
  - `key`: The specific key that the provided value must match to be selected
  - `return`: What field to specifically bubble up to the root of the data object. If not set defaults to one level above the found value

Example Config:
```json
{
  "name": "find_index_by_key",
  "config": {
      "value": "match:field/([0-9]+)/value",
      "key": "Must Match",
      "return": "sub:field/#0"
      }
  }
}
```

#### omct_hints
Adds OMCT hint information to a provided field name, allowing for omct output processors to automatically infer field data and generate output
Selected when using a name of `omct_hints`.
Has the following config arguments:
- `confs`: A list of configs describing which fields to match and the hints to add; has the following config arguments:
  - `match`: The field to add omct type info to
  - `hints`: A dictionary of omct type info you can append to the type info for the class. Certain types of type info are automatically inferred

Example Config:
```json
{
  "name": "omct_hints",
  "config": {
    "confs": [
      {
        "match": "key:input/data/field",
        "hints": {"units": "MB/s"}
      }
    ]
  }
}
```

#### split_by_key
Takes an input `key` data field and multiple input data fields and adds the `key` as a suffix to the input data fields' name.
Useful for splitting a single input data field into multiple display data fields by a key factor, such as message ID/type.
Selected when using a name of `split_by_key`.
Has the following config arguments:
- `key_fields`: A dict of `keys` to match against and lists of `values` that the key should equal when splitting values.
                The `key` is found using the gd2 `regex` syntax.
                If a `values` list is provided for a given `key` then only values in that list will be matched against
                If a `values` list is omitted every key will be matched against when splitting.
                The example config below shows what both examples may look like, in the first example only keys with id `id_0` and `id_1` will be split.
- `value_fields`: A list of data field names that will be split by key and have the key suffix appended to the field name
                  When this config is given an empty list, split by key will automatically append the key suffix to every data member.
                  Note that when referencing a key that has been split in the future you can either directly reference the data field with the key suffix or without.
- `key_delimiter`: The delimiter to use when appending keys as suffixes to data fields. Defaults to `:`.
                   NOTE: Due to potential display issues in the frontend, avoid using characters that may break urls like `@` or `/`.

Example Config:
```json
{
  "name": "split_by_key",
  "config": {
    "key_fields": {"key:path/to/key": ["id_0", "id_1"], "key:another/id":  []},
    "value_fields": ["data_field_1", "path/to/important/data/field"],
    "key_delimiter": ":"
  }
}
```

#### throttle
Rate limits a selected field so that it gets dropped from processing in any later preprocessor.
Useful when dealing with large, high rate data that GD2 may not be able to process quickly enough (IE high bandwidth image data).
Selected when using a name of `throttle`.
Has the following config arguments:
- `fields`: The fields to throttle.
- `throttle_rate_ms`: The number of milliseconds to wait between allowing any of the fields specified to be accessed for further preprocessing.

Example Config:
```json
{
  "name": "throttle",
  "config": {
    "fields": ["match:field/to/([0-9]+)/match", "key:other/field"],
    "throttle_rate_ms": 100
  }
},
```

### Generators
GD2 supplies different types of data generators for manipulating the processed data and converting it into a different format for storage/forwarding to pipeline external processing components.
These stages are responsible for transforming the GD2 preprocessed data fields and converting them into a finalized output format.
Once this stage is complete, it is the job of the output stages to take the generated data and send them to external components for further processing.
It is important to note that each generator isn't executed in series, but rather in parallel: each generator operates on a duplicate of the last data packet genrated by the previous pipeline function.

#### openmct
GD2's main interface is with OpenMCT.
This generator takes a processed data object and converts it into a data structure that is usable by OpenMCT.
This generator is selected when using a name of `openmct`.
Additionally, it has a required `id` field which is used to distinguish itself when setting the `consumes` field of an output stage.
This stage automatically creates a folder in the frontend at the root level with a value matching the config name of the enveloping `openmct_display` output stage.
Has the following config arguments:
- `data`: A list of dictionaries describing the fields to display in the frontend.
          Each data dictionary may contain an optional `type` to describe how the data should be displayed in the frontend.
          Certain data configuration fields are shared between all types, but many types have custom configuration parameters.
          For all types, if a `location` is not given the data object will be stored at the config name level folder.
          For in-depth descriptions of the different data types available please see the type subsections below.
  - `type`: The display type for a given data object. One of:
    - [plot.data](#plotdata)
    - [image.data](#imagedata)
    - [layout](#layout)
    - [folder](#folder)
  - `location`: Where a given data type should be stored in the front-end composition layout
  - `name`: The display name to use. For `.data` types name doubles as a `range_key` reference.
- `pass_all_omct`: Whether to automatically data objects with open_mct type info or not. Defaults to `False`.
- `pass_bfs_depth`: The depth in the data object structure in which to search for data with open_mct type info. Defaults to None
- `data_timeout_sec`: Specifies how long to wait before deleting stale data from the measurements dict. Defaults to 0 (no deletion).

Example Config:
```json
{
  "name": "openmct",
  "id": "openmct",
  "config": {
    "data": [
      {
        "name": "display_name",
        "range_key": "path/to/field/to/display",
        "format": "line",
        "units": "m/s"
      },
      {
        "name": "flat_field_value"
      },
      {
        "name": "layout_one",
        "type": "layout",
        "format": [
          ["flat_field_value", "display_name"]
        ]
      }
    ],
    "pass_all_omct": true,
    "pass_bfs_depth": 3
  }
}
```

##### plot.data
Displays data as a time series graph, where the x axis (domain) is time and the y axis (range) is the field value you specify.
Supports the following special arguments:
- `name`: The name to display in y-axis on the frontend, if `range_key` is not provided doubles as the `range_key`.
          CAVEAT: The display name CANNOT have any `/` in the name as this causes OpenMCT url resolution errors.
          GD2 currently sanitizes `/` field names by replacing them with `.` but if problems persist attempt to rename the field by manually supplying a `name` with no `/`.
- `range_key`: The data object field name to pull values from for the y-axis.
- `domain_key`: The data object field name to pull values from for the x-axis.
                If not provided will use  `datetime.now()` formatted so OpenMCT can read it.
                CAVEAT: OpenMCT requires timestamps to be in MS since epoch, note that if you wish to use your own timestamp that it must be formatted like so.
                Future features will support a better domain timestamp interface.
- `format`: The format to specify for OpenMCT to use when displaying the range data. Defaults to `None`.
- `units`: The units to specify for OpenMCT to use when displaying the range data. Defaults to `None`.

Example Data:
```json
{
  "type": "plot.data",
  "name": "display_name",
  "range_key": "data_object/path/to/value",
  "units": "m/s",
  "format": "format"
}
```

##### image.data
Displays a base64 encoded string as an image using the native OpenMCT display format.
Uses the image string as the range and the time as the domain.
Supports the following arguments:
- `name`: The name to display in y-axis on the frontend, if `range_key` is not provided doubles as the `range_key`.
          CAVEAT: The display name CANNOT have any `/` in the name as this causes OpenMCT url resolution errors.
          GD2 currently sanitizes `/` field names by replacing them with `.` but if problems persist attempt to rename the field by manually supplying a `name` with no `/`.
- `range_key`: The data object field name to pull values from for the image display.
- `domain_key`: The data object field name to pull values from for the x-axis.
                If not provided will use  `datetime.now()` formatted so OpenMCT can read it.
                CAVEAT: OpenMCT requires timestamps to be in MS since epoch, note that if you wish to use your own timestamp that it must be formatted like so.
                Future features will support a better domain timestamp interface.

Example Data:
```json
{
  "type": "image.data",
  "name": "display_name",
  "range_key": "data_object/path/to/value"
}
```

##### layout
Creates a multi-data flexible layout display to automatically showcase certain fields as describe by the layout configuration.
Supports the following arguments:
- `rowsLayout`: Whether to order the display format in row major ordering (true) or column major ordering (false)
- `format`: A list of lists, where the first list specifies the rows (when using column major ordering) and internal lists specify the columns.
            Internal values should be names matching the display names for other various data fields (may include other layouts or `.data` types).

Example Data:
```json
{
  "type": "layout",
  "name": "layout_one",
  "rowsLayout": true,
  "format": [
    ["display_one", "display_two"],
    ["custom_one"],
    ["field_one", "field_two", "field_three", "field_four"]
  ]
}
```

##### folder
Creates an additional folder location on the frontend file explorer sidebar
Supports the `name` and `location` arguments: folders have no additional arguments.

Example Data:
```json
{
  "type": "folder",
  "name": "new_folder",
  "location": "custom_location"
}
```

### Output
GD2 supplies multiple processing stages that terminate pipeline processing.
These stages are responsible for sending data to additional processes for either data storage or display purposes.
After the generator stage has completed, data is tee-ed up (duplicated) and pushed onto the unique input queue for each output processor.
At this point, each output processing stage operates on the input data and then terminates data packet processing.
It is important to note that output stage execution isn't in series, but rather in parallel: each output stage operates on a duplicate of the last data packet generated by the previous pipeline generator.
Each output stage requires a `name` arg to select the type of output, and a `consumes` arg to select which generator to get input from.

#### data_store
GD2 utilizes a MongoDB database to retain messages for displaying at a later time. The database connects to the
backend which essentially pushes copies of the OpenMCT messages to the database. These historical messages are
retained for a user defined amount of time, if no time limit is specified the default retention period is 1000
seconds.

The data store configuration has the following config values:
- `time_limit`: The amount of time in seconds to keep messages in the database, after this amount of
  time has passed the message is removed from the database.
- `data_store_host`: The host address to use for the internal ZMQ connection between the backend and the datastore.
  - Note: This value _must_ be a IP address (`127.0.0.1`) and not `localhost`.
- `data_store_port`: The port number to use for the internal ZMQ connectio between the backend and the datastore.
- `database_host`: The host address of the running MongoDB database for the datastore to connect to.
- `database_port`: The port number of the running MongoDB database for the datastore to connect to.

**Note:** The GD2 datastore will only work with a MongoDB database for storing messages.

Example Config:
```json
{
  "name": "data_store",
  "consumes": "openmct",
  "config": {
    "time_limit": 1000,
    "data_store_host": "127.0.0.1",
    "data_store_port": 5050,
    "database_host": "127.0.0.1",
    "database_port": 27017,
  }
}
```

#### openmct_display
Takes input data objects and queues them up into an asynchronous websocket server that then sends the messages to a connected frontend interface.
Selected when using a name of `openmct_display`.

Example Config:
```json
{
  "name": "openmct_display",
  "consumes": "openmct"
}
```

### Parsing Syntax
To facilitate parsing complex nested structures and arrays with multiple values GD2 has implemented a custom parsing syntax when specifying which fields to process.
This syntax consists of nested structure specifiers and array access specifiers.
The syntax also includes the regular expression parsing strings and literal data references.

##### Object Parsing
When referencing complex objects there are two main syntax parsing features that GD2 supports: nested structure reference with `/` and array field reference with `[0-9]+`.
- `/`: To reference nested structure objects use the `/` delimiter.
       Example: `path/to/object/you/want/to/reference`
- `[0-9]+`: To reference a specific array index use an integer.
            Example: `path/to/array/5/sub/array/3/field`

##### Regex Parsing
There are 4 field referencing regex processing types described below:

- `literal`: A literal value to use. When one of the below isn't specified a literal is inserted instead.
             Example: `"rows": 64`, will use the value `64` in the processing
- `key`: A field to pull from the data object being processed. References a field's value in the processed data object.
         Example: `"rows": "key:rows"`, will use the value from `data_object[rows]` when processing
- `match`: A field to perform regular expression matching against. References a field's value in the processed data object.
           Example: `"rows": "match:root/([0-9]+)/rows` will use the value from `data_object[root/0../rows]`
- `sub`: A field to perform regular expression group substitution against. Requires a corresponding `match:`. References a field's value in the processed data object.
         Example: `"rows": "sub:root/#0/rows` will reference the index from the first `match:` group to get `data_object[root/0../rows]`