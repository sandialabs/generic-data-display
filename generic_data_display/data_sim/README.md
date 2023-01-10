# GD2 Examples
This directory contains the configuration files used by GD2 to process the data simulator clients as well as configurations for the data simulator clients themselves.
Additional data formats (kaitai, proto) are specified and test clients are provided to ensure that the data simulator clients work as expected.

## Source
To execute a data simulator client, simply use the following command after installing GD2:
```
gd2_data_sim --config-file path/to/config/file.json --log-level debug
```
This spins up a `DataSender` for each config in the provided file that matches an element in the `_connection_dict` and `_generator_dict`.
Currently the `DataSender` supports sending out data in tcp/zmq/http format.
Additionally there are multiple `data_generators` that generate messages with various forms of data in them (nested metadata, images, etc.).
To use a specific data generator you must match the key of the `_generator_dict` to the `type` object in the `connection` dict when configuring a data simulator.
The current list of available data simulator configurations can be found at [resources/data_sim_configs](resources/data_sim_configs)
Each available data client configuration has a different set of config arguments; you will need to inspect the source of the generators to determine what those arguments are and what they represent.
Additionally, a set of example connection configurations for the GD2 processing pipeline that correspond to processing this example data can be found at [resources/pipeline_configs](resources/pipeline_configs).

## Example Data Client Config
The following json blob is an example data client config that uses the `protobuf_test` data generator.
This config uses the tcp_sender defined in [tcp_sender.py](tcp_sender.py) and the BasicProtobufGenerator defined in [data_generators.py](data_generators.py).
```json
{
    "description": "Test file used to implement a basic TCP send of a protobuf data structure",
    "version": 1.0,
    "config": [
      {
        "connection": {
          "type": "tcp",
          "address": "localhost",
          "port": 51772
        },
        "data": {
          "type": "protobuf_test",
          "range_step": 2,
          "range_start": 0,
          "range_stop": 100,
          "ms_between_send": 500,
          "loop_forever": true,
          "prepend_message_size": true 
        }
      }
    ]
  }
```