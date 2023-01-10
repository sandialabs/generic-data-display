GD2: Generic Data Display
=========================
GD2 is a real time data visualization application that can be used to display any type of formatted user defined input data.
GD2 consists of two components: a python backend that handles receipt and pre-processing of live user input data, and a javascript webserver that handles the display of data pre-processed by the backend.
The python backend is composed of a web-socket server connection component, a configuration parsing component, and multiple data processing components that are invoked through a user created JSON configuration file that adheres to the DSL GD2 defines.
The javascript frontend is built upon NASA's OpenMCT framework, and manages multiple backend connections using websockets.
The primary focus of GD2 is to make it incredibly easy to spin up a visual data display for real-time data: simply create a json config file to describe the input connections and fields you wish to display and pass that file as an argument to the python backend application.

![example](assets/gd2_display.png)

# Component Overview
GD2 is made up of two main directories:
- [generic_data_display](generic_data_display), which holds python code for any backend/utility processes
- [frontend](frontend), which holds javascript code for the frontend server application

## Python Backend
GD2 comes with mutiple python processes to support processing, storing, and simulating data flow from input to the frontend.
- `gd2_pipeline`: The processing component of GD2. Configured with a json file that describes the types of connections to make, format of the input data, and how to preprocess it for display purposes.
- `gd2_data_store`: The database component of GD2. Used by the frontend to display historical data.
- `gd2_data_sim`: The simulation component of GD2. Generates data for testing and for trying out features.
- `gd2_validate`: A simple process that can be used to validate pipeline and data_store config files according to the json_schema.

### Pipeline Features
GD2 supports multiple input connection types, input data formats, and preprocessor functions for manipulating/formatting data.
The data formats and functions currently supported are listed below.
For more information on how to write a configuration to utilize the below features please read [the GD2 pipeline README.md](generic_data_display/pipeline/README.md)

### Data Store Features
GD2 stores data from the pipeline using a MongoDB database.
For information on how to configure the data store, please read [the GD2 data_store README.md](generic_data_display/data_store/README.md)

### Data Sim Features
For testing and trial purposes, the GD2 data simulator can be spun up to create multiple data testing endpoints and is used to showcase the various GD2 capablities.
There are also examples on how to create GD2 pipeline and GD2 data store configuration files in the resources directory within this module.
For information on how to utilize the data simulator please read [the GD2 data_sim README.md](generic_data_display/data_sim/README.md)

### Validate Features
Validation is a simple script available when installing the gd2 python module.
Simply run `gd2_validate` to see the options available for validating configuration files before usage in other GD2 backend processes.

## Javascript Frontend
GD2 expands on OpenMCT, a javascript framework developed at NASA used to display real-time telemetry data from their rovers and satellite missions.
It implements a generic interface for connecting to a proxied websocket data stream, and a display dictionary http endpoint.
Together, this allows the GD2 frontend to display any type of json data streamed through the GD2 pipeline.
Testing deployments are configured via webpack dev server, and a docker container exists with an nginx configuration for deploying the frontend server application.
For more information on the frontend component, please read [the GD2 frontend README.md](frontend/README.md)

# Installation Requirements
## Python Backend
To run the python backend you will need at least `python3.7` and install the requirements found [here](requirements.txt).
We recommend using python virtual environments when installing GD2 directly.
You can create a python virtual environment, activate the environment, install GD2 and its requirements with the following commands:
```
python -m venv ~/path/to/gd2_venv
source ~/path/to/gd2_venv/Scripts/activate
pip install -r requirements.txt
pip install -e setup.py
```

## Javascript Frontend
[See README in frontend for instructions](frontend/README.md)


## Docker
This repository contains Dockerfiles for running the [python backend](Dockerfile.pipeline),
the [python data simulator](Dockerfile.data_sim), the [javascript frontend](Dockerfile.frontend),
the [historical data store](Dockerfile.data_store), and the [historical sidecar server](Dockerfile.sidecar).
The docker images and their dependencies can be built via [build.sh](build.sh).


## Additional Third Party Software (TPS) Requirements
### Kaitai
GD2 uses the Kaitai parser to generate python structures used to parse binary data.
To use Kaitai, you must install the kaitai-struct-compiler (found here: https://kaitai.io/)

### Protocol Buffer
GD2 uses the protocol buffer compiler to generate python structures used to parse binary protobuf data.
To use Protocol Buffers you must install the protoc python compiler.

# How to Run
## Docker
An example Docker Compose script is [included](docker-compose.yml).
Before spinning up the docker containers, you will need to follow these instructions:
- ensure `no_proxy=[no_proxy_info]` is set
- ensure `http_proxy={proxy_url}` is set
- ensure `https_proxy={proxy_url}` is set
- ensure you have a docker container runtime installed and running
- ensure that you have `docker-compose` installed
- create a personal access token on gitlab in user/Settings/Access Tokens with read_registry and write_registry access selected (save this token)

Once the above steps are followed, to spin up the docker swarm, simply run `docker-compose up`.
With the default compose configuration, this will startup the GD2 frontend, backend, and data simulator, accessed at [http://localhost:8080](http://localhost:8080).

### Modifying the configuration files
Using docker volumes, it is possible to change the configuation file utilized for a given application in the `docker-compose.yml` file.
This involves creating a `volumes` attribute for a given service and modifying the path to the `/opt/gd2/conf` directory in that mount.
The following example shows what to set for the `pipeline` service to modify the configuration file used (which is named `pipeline.json`) by pointing to the files in a local `gd2-conf` directory.
```
  pipeline:
    image: ${CI_REGISTRY_IMAGE}/pipeline:latest
    volumes:
      - ./gd2-conf:/opt/gd2/conf
    deploy:
      mode: global
      restart_policy:
        condition: on-failure
    depends_on:
      - sidecar
      - data_sim
```

## Startup Backend
With GD2 installed, you can run the following python command to spin up the processing pipeline application and frontend server:
```
gd2_pipeline --config-file path/to/config/file --http-port 8221
```
From inside the frontend directory.
```
npm build && npm run start
```
You can then connect to the frontend webpack server at `http://localhost:8080`

## Startup Data Store
With GD2 installed, you can run the following python command and node command to spin up the data store pipeline application and sidecar server:
```
gd2_data_store --config-file path/to/config/file
```
From inside the frontend/sidecar_server directory.
```
npm build && npm run start
```
If you are planning on making changes to the side car server want to have the server automatically reload you can use the following command in the frontend/sidecar_server directory.
```
nodemon
```
You can then connect to the frontend webpack server at `http://localhost:8080`

## Run an Example Scenario
First, startup the test data server:
```
gd2_data_sim --config-file generic_data_display/data_sim/resources/data_sim_configs/sim_config_tcp_kaitai_image.json --log-level debug
```
Next, startup the Generic Data Display backend using this config file:
```
gd2_pipeline --config-file generic_data_display/data_sim/resources/pipeline_configs/backend_config_tcp_kaitai_image.json --log-level debug
```
Next, startup the historical data store using the following config file:
```
gd2_data_store --config-file generic_data_display/data_sim/resources/data_store_configs/data_store_config_basic.json --log-level debug
```
Then, from inside the frontend directory
```
npm build && npm run start
```
Lastly, from inside the frontend/sidecar_server directory run
```
npm build && npm run start
```
You can then connect to the frontend webpack server at `http://localhost:8080`
For more info on how to run the examples see the [Examples README.md](generic_data_display/data_sim/README.md)
