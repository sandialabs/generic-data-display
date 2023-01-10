
from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.timer import Timer
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper

import shutil
import subprocess
import pathlib
import importlib.util


class ProtobufParser(object):
    def __init__(self, push_queue, **kwargs):
        log.info("Initializing the protobuf parser")
        protobuf_path = shutil.which("protoc")
        if protobuf_path is None:
            log.error("could not find protoc compiler")
            exit(1)

        self.push_queue = push_queue
        self.pb2 = None
        config = {}
        config.update(kwargs)
        self.config = config

        file_path = config["protobuf_file"]
        proto_file = pathlib.Path(file_path)

        if not proto_file.exists():
            log.error("Could not find protofile: \"{}\" ".format(file_path))
            exit(1)

        # some/proto_file.proto -> some/proto_file_pb2.py
        output_file = file_path.split('.')[0] + '_pb2.py'
        result = subprocess.run([protobuf_path, file_path, "--python_out=./"])
        log.info("{} result {}".format(protobuf_path, result))

        if not pathlib.Path(output_file).exists():
            log.error("Did not generate the protofile: \"{}\" (maybe the path is wrong?)".format(output_file))
            exit(1)

        spec = importlib.util.spec_from_file_location("generic_data_display", str(output_file))
        protobuf_module = importlib.util.module_from_spec(spec)
        print(protobuf_module.__doc__)
        spec.loader.exec_module(protobuf_module)
        if (not config['protobuf_class']):
            log.error("A protobuf class must be specified!")
            exit(1)

        self.protobuf_class = getattr(protobuf_module, config['protobuf_class'])

    def reset_io_byte_stream(self):
        pass

    def parse_io_byte_stream(self, io_stream): # TCP implementation
        timer = Timer()
        with timer('Protobuf Parser'):
            header_size = self.config['prefix_message_size_bytes']
            message_size_bytes = io_stream.read(header_size)
            message_size = int.from_bytes(message_size_bytes, byteorder='big')
            protobuf_bytes = io_stream.read(message_size)
            proto_msg = self.protobuf_class()
            proto_msg.ParseFromString(protobuf_bytes)
            self.push_queue.put(AccessWrapper(proto_msg, timer=timer))


    def parse_from_bytes(self, obj_bytes): # ZMQ
        timer = Timer()
        with timer('Protobuf Parser'):
            try:
                proto_msg = self.protobuf_class()
                proto_msg.ParseFromString(obj_bytes)
            except TypeError as e:
                log.error('Failed to parse protobuf message: ' + e)
                return

            self.push_queue.put(AccessWrapper(proto_msg, timer=timer))

