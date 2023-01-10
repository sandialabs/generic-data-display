import yaml

from jsonschema import validate, ValidationError

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.timer import Timer
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper


class YamlParser(object):
    """
    Yaml Parser!

    Config:
        - schema: path to a json schema file
    """

    def __init__(self, push_queue, **kwargs):
        log.info("Initializing the Yaml Parser")

        self.push_queue = push_queue
        self.config = {}
        self.config.update(kwargs)
        self.iter = None
        self.buffer = b''

        self.schema = None
        if "schema" in self.config.keys():
            with open(self.config["schema"], 'r') as handle:
                self.schema = yaml.safe_load(handle)

    def _validate(self, yaml_msg):
        if self.schema:
            try:
                # The jsonschema docs say it's possible to validate yaml
                validate(instance=yaml_msg, schema=self.schema)
            except ValidationError:
                log.warn("Yaml msg failed validation")
                log.debug(f"Bad Yaml message: {yaml_msg}")
                return False
        return True

    def reset_io_byte_stream(self):
        self.iter = None

    def parse_io_byte_stream(self, io_stream):
        # TODO mjfadem: Figure out a way to determine the size of the io_stream
        # self.buffer += io_stream.read()
        # if "max_bytes" in self.config.keys():
        #     if len(self.buffer) > self.config["max_bytes"]:
        #         log.error("Yaml IO stream exceeds max_bytes config limit, did you forget a start or stop delimiter?")

        # while '\n---' in self.buffer:
        #     timer = Timer()
        #     with timer('YAML Parser'):
        #         yaml_str, self.buffer = self.buffer.split('\n---', 1)
        #         msg = yaml.safe_load(yaml_str)
        #         if self._validate(msg):
        #             self.push_queue.put(AccessWrapper(msg, timer=timer))

        timer = Timer()
        with timer('Yaml Parser'):
            if self.iter is None:
                self.iter = yaml.safe_load_all(io_stream)
            msg = next(self.iter)
            if self._validate(msg):
                self.push_queue.put(AccessWrapper(msg, timer=timer))

    def parse_from_bytes(self, obj_bytes):
        timer = Timer()
        with timer('Yaml Parser'):
            msg = yaml.safe_load(obj_bytes)
            if not self._validate(msg):
                return
            self.push_queue.put(AccessWrapper(msg, timer=timer))
