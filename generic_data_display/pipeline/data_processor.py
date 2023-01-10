from inspect import Attribute
from generic_data_display.pipeline.data_parsers import kaitai, json as _json, protobuf, yaml as _yaml, csv as _csv, xml as _xml
from generic_data_display.pipeline.network_receivers import http, tcp, zmq
from generic_data_display.pipeline.output_formats import openmct_display, data_store
from generic_data_display.pipeline.preprocessors import (average, imagify, throttle, base64,
                                                         split_by_key, omct_hints, find_index_by_key)
from generic_data_display.pipeline.output_generators import openmct_generator
from generic_data_display.pipeline.utilities.tee_queue import TeeQueue
from generic_data_display.pipeline.utilities.output_queues import OutputQueues
from generic_data_display.utilities.logger import log

import queue


class DataProcessor(object):
    """Controls the entire processing chain from input to output

    Using the provided config on initialization, this class creates
    the necessary sub-components to handle receipt of data, parsing
    of data, preprocessing of data, and conversion of data into a
    format suitable for consumption by the front-end.  Currently this
    class supports the following sub-components:

    Sub-processors communicate with each other using queues. The
    parser_data_queue is the first input (data received over socket and
    parsed accordingly), each individual preprocessor gets an input and
    an output queue, and the final preprocessor (display_format_preprocessor)
    outputs to the special WebsocketManager managed json_formatter_queue.
    Each queue expects an `AccessWrapper` object which contains the actual
    parsed data and additional structures to assist in processing. Every
    implemented parser is expected to wrap the parsed object in an `AccessWrapper`
    before pushing onto its output queue.
    """

    receiver_dict = {
        "http": lambda *args, **kwargs: http.HttpReceiver(*args, **kwargs),
        "tcp": lambda *args, **kwargs: tcp.TcpReceiver(*args, **kwargs),
        "zmq": lambda *args, **kwargs: zmq.ZmqReceiver(*args, **kwargs)
    }
    parser_dict = {
        "kaitai": lambda *args, **kwargs: kaitai.KaitaiParser(*args, **kwargs),
        "json": lambda *args, **kwargs: _json.JsonParser(*args, **kwargs),
        "protobuf": lambda *args, **kwargs: protobuf.ProtobufParser(*args, **kwargs),
        "yaml": lambda *args, **kwargs: _yaml.YamlParser(*args, **kwargs),
        "csv": lambda *args, **kwargs: _csv.CSVParser(*args, **kwargs),
        "xml": lambda *args, **kwargs: _xml.XmlParser(*args, **kwargs)
    }
    preprocessor_dict = {
        "average": lambda *args, **kwargs: average.FieldAverage(*args, **kwargs),
        "imagify": lambda *args, **kwargs: imagify.Imagify(*args, **kwargs),
        "base64": lambda *args, **kwargs: base64.Base64(*args, **kwargs),
        "throttle": lambda *args, **kwargs: throttle.Throttler(*args, **kwargs),
        "split_by_key": lambda *args, **kwargs: split_by_key.SplitByKey(*args, **kwargs),
        "omct_hints": lambda *args, **kwargs: omct_hints.OmctHints(*args, **kwargs),
        "find_index_by_key": lambda *args, **kwargs: find_index_by_key.FindIndexByKey(*args, **kwargs)
    }
    generator_dict = {
        "openmct": lambda *args, **kwargs: openmct_generator.OpenMctGenerator(*args, **kwargs)
    }
    output_dict = {
        "openmct_display": lambda *args, **kwargs: openmct_display.OpenMctDisplay(*args, **kwargs),
        "data_store": lambda *args, **kwargs: data_store.DataStore(*args, **kwargs),
    }

    def __init__(self, config):
        log.info("Initializing the Data Processor")
        self.parser_data_queue = queue.Queue()
        self.config = config
        self.config_name = self.config['name']
        self.parser = self.parser_dict[self.config["data"]["format"]](self.parser_data_queue,
                                                                      **self.config.get("data", {}))
        self.receiver = self.receiver_dict[self.config["connection"]["type"]](self.parser,
                                                                              **self.config.get("connection", {}))
        prior_queue = self.parser_data_queue

        self.preprocessors = []
        if "preprocessing" in self.config:
            for preprocessing in self.config["preprocessing"]:
                name = preprocessing["name"]
                push_queue = queue.Queue()
                self.preprocessors.append(self.preprocessor_dict[name](
                    prior_queue, push_queue, config_name=self.config_name, **preprocessing.get('config', {})))
                prior_queue = push_queue


        self.generator_tee_queue = TeeQueue(prior_queue)
        self.output_tee_queues = {}
        self.generators = []
        for generator in self.config["generator"]:
            name = generator["name"]
            id = generator["id"]
            push_queue = queue.Queue()
            self.output_tee_queues[id] = TeeQueue(push_queue)
            self.generators.append(self.generator_dict[name](
                self.generator_tee_queue.get_queue(), push_queue,
                config_name=self.config_name, **generator.get('config', {})))

        self.output_queues = OutputQueues()
        self.outputs = []
        for output in self.config["output"]:
            name = output["name"]
            consumes = output["consumes"]
            self.outputs.append(self.output_dict[name](
                self.output_tee_queues[consumes].get_queue(), self.output_queues.get_queue(name),
                config_name=self.config_name, **output.get('config', {})))

        self.run()

    def close(self):
        log.info("Shutting down the Data Processor")
        self.receiver.join()
        for preprocessor in self.preprocessors:
            preprocessor.join()
        self.generator_tee_queue.join()
        for generator in self.generators:
            generator.join()
        for tee_queue in self.output_tee_queues.values():
            tee_queue.join()
        for output in self.outputs:
            output.join()
        log.info("Shut down the Data Processor")

    def run(self):
        log.info("Starting the Data Processor")
        self.receiver.start()
        for preprocessor in self.preprocessors:
            preprocessor.start()
        self.generator_tee_queue.start()
        for generator in self.generators:
            generator.start()
        for tee_queue in self.output_tee_queues.values():
            tee_queue.start()
        for output in self.outputs:
            output.start()
        log.info("Started the Data Processor")
